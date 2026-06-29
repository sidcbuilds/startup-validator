# 🚀 Startup Idea Validator

A structured startup idea validator grounded in Harvard's validation framework, YC RFS 2026 themes, and AI-era moat analysis.

## Setup

**1. Add your OpenAI API key**

Copy `.env.example` to `.env` and fill in your key:
```
OPENAI_API_KEY=sk-your-key-here
```
Get a key at https://platform.openai.com/api-keys

**2. Run the app**
```powershell
python -m streamlit run app.py
```
Opens at http://localhost:8501

## How it works

1. You fill in 6 questions about your idea
2. The app auto-researches competitors, market size, and demand signals via DuckDuckGo (free, no API key)
3. GPT-4o mini scores your idea across 6 rubrics
4. You get a structured report with a verdict, scores, risks, and next steps

## Scoring Rubrics

| Rubric | Weight | What it measures |
|---|---|---|
| 🎯 Problem Clarity | 1.0x | Specific customer, pain, frequency |
| 📊 Market Size | 1.2x | TAM/SAM, venture scale potential |
| 📡 Demand Signals | 1.0x | Search volume, forum activity, complaints |
| ⚔️ Competitive Landscape | 1.0x | Saturation, your wedge |
| 🏹 YC RFS Alignment | 0.8x | 2026 investment theme fit, timing |
| 🏰 AI-Era Moat | 1.5x | Defensibility against OpenAI/Google replication |

## Hosting on Streamlit Cloud (free, shareable URL)

Your API keys live in `.env` locally and are **never** pushed (`.gitignore` excludes them). On the cloud, keys go in Streamlit's encrypted Secrets.

1. **Create a GitHub repo** and push:
   ```powershell
   git init
   git add -A
   git commit -m "Startup idea validator"
   git remote add origin https://github.com/<user>/<repo>.git
   git push -u origin main
   ```
2. Go to **https://share.streamlit.io** → sign in with GitHub → **New app**
3. Pick your repo, branch `main`, main file `app.py`
4. Open **Advanced → Secrets** and paste (see `.streamlit/secrets.toml.example`):
   ```toml
   LLM_PROVIDER = "anthropic"
   ANTHROPIC_API_KEY = "sk-ant-..."
   ANTHROPIC_MODEL = "claude-sonnet-4-5"
   ```
5. **Deploy** — you get a public `https://<app>.streamlit.app` URL for the demo

Anyone with the URL can use it; the keys stay encrypted in Secrets, billed to your Anthropic account.
