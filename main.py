import os
import json
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chabita")

app = FastAPI(title="Chabita AI Assistant", version="1.0.0")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("DEFAULT_MODEL", "gemini-3.8-flash")
BASE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"

# Chabita Personality Prompts
BASE_PERSONA = (
    "You are Chabita, a delightfully simple, warm, and highly user-friendly AI assistant. "
    "Your primary goal is to make complex tasks feel effortless for the user.\n\n"
    "Communication Style:\n"
    "- Keep it Simple: Use plain, conversational language. Avoid dense technical jargon, acronyms, "
    "or overly verbose explanations unless the user specifically asks for deep technical details.\n"
    "- Warm & Encouraging: Maintain a polite, helpful, and approachable tone. You are a collaborative partner.\n"
    "- Bite-Sized Responses: When explaining concepts, break them down into easy-to-digest bullet points or numbered steps.\n\n"
    "Behavioral Directives:\n"
    "1. Proactive Clarification: If a request is ambiguous, gently ask one simple clarifying question rather than guessing.\n"
    "2. Graceful Error Handling: If an issue occurs, explain what went wrong in plain English, and immediately offer a simple fix.\n"
    "3. Format your answers neatly using Markdown (headers, bullet points, clean code snippets when needed)."
)

MODES = {
    "warm_simple": BASE_PERSONA,
    "concise": BASE_PERSONA + "\n\nAdditional Directive: Be exceptionally concise. Provide direct, bullet-pointed answers with minimal preamble.",
    "detailed": BASE_PERSONA + "\n\nAdditional Directive: Provide step-by-step deep dives, code explanations, and thorough examples while maintaining your friendly, accessible warmth."
}

class MessageItem(BaseModel):
    role: str  # "user" or "assistant" or "model"
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageItem]
    mode: Optional[str] = "warm_simple"
    temperature: Optional[float] = 0.7

@app.get("/api/health")
async def health_check():
    has_key = bool(GEMINI_API_KEY)
    return {
        "status": "healthy",
        "app": "Chabita AI",
        "model": MODEL_NAME,
        "configured": has_key
    }

def format_gemini_contents(messages: List[MessageItem]):
    """Convert chat messages into Google Gemini API contents array."""
    gemini_contents = []
    
    for msg in messages:
        # Map assistant -> model
        role = "model" if msg.role in ("assistant", "model") else "user"
        content_text = msg.content.strip()
        if not content_text:
            continue
            
        # Avoid consecutive same-role messages by combining them if necessary
        if gemini_contents and gemini_contents[-1]["role"] == role:
            gemini_contents[-1]["parts"][0]["text"] += "\n\n" + content_text
        else:
            gemini_contents.append({
                "role": role,
                "parts": [{"text": content_text}]
            })
            
    # Ensure starts with user
    if gemini_contents and gemini_contents[0]["role"] != "user":
        gemini_contents.insert(0, {"role": "user", "parts": [{"text": "Hello"}]})
        
    return gemini_contents

@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API Key is not configured. Please set GEMINI_API_KEY in Render environment variables."
        )

    system_instruction = MODES.get(request.mode, BASE_PERSONA)
    contents = format_gemini_contents(request.messages)

    if not contents:
        raise HTTPException(status_code=400, detail="No message content provided.")

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": request.temperature or 0.7,
            "maxOutputTokens": 4096
        }
    }

    url = f"{BASE_GEMINI_URL}/models/{MODEL_NAME}:streamGenerateContent?alt=sse&key={api_key}"

    async def sse_generator():
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        logger.error(f"Gemini API returned status {response.status_code}: {error_body.decode(errors='ignore')}")
                        yield f"data: {json.dumps({'error': 'Oh no! I had a little hiccup connecting with the AI engine. Please verify the API key or try again in a moment.'})}\n\n"
                        yield "data: [DONE]\n\n"
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data:"):
                            raw_data = line[5:].strip()
                            try:
                                data_obj = json.loads(raw_data)
                                candidates = data_obj.get("candidates", [])
                                if candidates:
                                    parts = candidates[0].get("content", {}).get("parts", [])
                                    text_chunk = "".join(p.get("text", "") for p in parts if "text" in p)
                                    if text_chunk:
                                        yield f"data: {json.dumps({'text': text_chunk})}\n\n"
                            except Exception as parse_err:
                                logger.warning(f"Failed to parse SSE chunk: {parse_err}")

            yield "data: [DONE]\n\n"

        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': 'The request timed out. Chabita is ready when you want to try again!'})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.exception("Unexpected error in chat streaming")
            yield f"data: {json.dumps({'error': f'Something unexpected happened: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/chat/sync")
async def chat_sync(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key is not configured.")

    system_instruction = MODES.get(request.mode, BASE_PERSONA)
    contents = format_gemini_contents(request.messages)

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {"temperature": request.temperature or 0.7}
    }

    url = f"{BASE_GEMINI_URL}/models/{MODEL_NAME}:generateContent?key={api_key}"

    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(url, json=payload)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail="AI engine request failed")
        data = res.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return {"reply": "I couldn't generate a response. Please try rephrasing your message!"}
        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return {"reply": text}

# Mount static files (Frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Chabita AI on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
