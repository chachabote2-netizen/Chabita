# 🌸 Chabita · Your Friendly Web AI Assistant

> **A delightfully simple, warm, and highly capable web-based AI assistant powered by Google Gemini.**  
> Ready for 1-click deployment on **Render**, mobile-responsive, with live streaming, voice recognition, and markdown code formatting.

---

## ✨ Features

- **🌸 Chabita Persona**: Warm, approachable, and encouraging tone designed to make complex problems feel effortless.
- **⚡ Real-Time Streaming**: Instant token-by-token streaming responses using Server-Sent Events (SSE).
- **🎙️ Voice Input (Speech-to-Text)**: Speak directly into the chat using the built-in microphone button.
- **🔊 Read Aloud (Text-to-Speech)**: One-click voice playback for any of Chabita's responses.
- **🎭 3 Personality Modes**:
  - **Warm & Simple (Default)**: Friendly, conversational, and jargon-free explanations.
  - **Quick & Concise**: Fast, bullet-pointed summaries.
  - **Step-by-Step Deep Dive**: In-depth explanations with code walkthroughs.
- **💻 Syntax-Highlighted Code**: Clean dark code blocks with an instant **"Copy code"** button.
- **💾 Conversation History**: Automatically persists chats in `localStorage` so your history is always preserved.
- **📥 Export Chats**: Download your conversations as clean Markdown (`.md`) files.
- **🌙 Light & Dark Themes**: Seamless day/night modes with auto-saved preferences.
- **📱 100% Mobile Friendly**: Slide-out responsive sidebar for phones and tablets.

---

## 🚀 How to Deploy on Vercel (1-Click Import)

1. Go to **[vercel.com/new](https://vercel.com/new)**.
2. Select your repository: **`dullareymart19webde/Chabita`** and click **Import**.
3. Under **Environment Variables**, add:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** *(your Gemini API key)*
4. Click **Deploy**! Vercel will build and launch your site with a live URL like `https://chabita.vercel.app`.

---

## 🚀 How to Deploy on Render (Step-by-Step)

You can publish Chabita to [Render](https://render.com) for **free** in less than 3 minutes.

### Method 1: Deploy with Git (Recommended)

1. **Push your code to GitHub / GitLab:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Chabita Web AI"
   git branch -M main
   git remote add origin https://github.com/<your-username>/chabita-ai.git
   git push -u origin main
   ```

2. **Create a Web Service on Render:**
   - Go to your [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Web Service**.
   - Connect your GitHub repository.

3. **Configure Settings:**
   - **Name:** `chabita-ai` (or any name you like)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`

4. **Add Environment Variable:**
   - Scroll to **Environment Variables** and add:
     - **Key:** `GEMINI_API_KEY`
     - **Value:** Your Gemini API Key (e.g. `AQ.Ab8RN6...`)
   - *(Optional)* **Health Check Path:** `/api/health`

5. **Click "Deploy Web Service"!**  
   Render will build the app and give you a public URL like `https://chabita-ai.onrender.com`.

---

### Method 2: Render Blueprint (`render.yaml`)

Because this project includes a `render.yaml` configuration, you can also deploy using Render Blueprints:
1. Go to **New +** → **Blueprint** on Render.
2. Select your repository.
3. Fill in your `GEMINI_API_KEY` when prompted, and click **Apply**.

---

## 💻 Running Locally

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup your environment variables
Create a `.env` file (or copy `.env.example`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```

### 4. Run the application
```bash
python main.py
```
Open your browser and navigate to **`http://localhost:8000`**.

---

## 📁 Project Structure

```
Chabita/
├── .env                  # Local environment file (API keys)
├── .env.example          # Sample environment config
├── .gitignore            # Git ignore rules
├── Procfile              # Deployment command for PaaS / Render
├── render.yaml           # Render 1-click Blueprint definition
├── requirements.txt      # Python backend dependencies
├── main.py               # FastAPI backend with SSE streaming
├── static/
│   ├── index.html        # Modern single-page chat interface
│   ├── style.css         # Glassmorphic, responsive styles & animations
│   ├── app.js            # Client logic (SSE, Voice in/out, local storage)
│   └── favicon.svg       # Cute Chabita brand avatar
└── README.md             # Documentation & deployment guide
```

---

## 🛡️ License & Credits
Crafted with ❤️ powered by Google Gemini.

