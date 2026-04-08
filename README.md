# 🚀 Career Finder AI

**Career Finder AI** is a multi-agent SaaS platform that automates the job search, scoring, and application process. It uses specialized agents for job collection (API & Scraping) and a GPT-4o powered engine for resume tailoring.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

## ✨ Features
- **Parallel Job Hunting:** Simultaneously queries LinkedIn/Indeed via SearchApi and scrapes niche sites like YC Jobs.
- **Smart Scoring:** Weighs job descriptions against your resume with a weighted heuristic engine.
- **AI Resume Tailor:** One-click tailoring that optimizes your resume for specific roles using recruiter psychology.
- **High-Conversion Email Gen:** Generates short, punchy application emails for every role.
- **Glassmorphic UI:** Modern, premium dark mode interface.

## 🛠️ Tech Stack
- **Backend:** FastAPI, Playwright (Headless Chrome), OpenAI GPT-4o, SearchApi.io.
- **Frontend:** React, Vite, Vanilla CSS.
- **Ops:** Docker (Backend), Vercel (Frontend).

## 🚀 One-Click Deployment

### Backend (Render)
1. Push this code to GitHub.
2. Click the **Deploy to Render** button above or create a "Blueprint" project on Render.
3. It will automatically detect `render.yaml` and prompt you for these variables:
   - `OPENAI_API_KEY`
   - `SEARCHAPI_KEY`

### Frontend (Vercel)
1. Import the repository into Vercel.
2. Set the `VITE_API_URL` environment variable to your Render service URL (e.g., `https://career-finder-backend.onrender.com`).

---

## 💻 Local Development

### 1. Requirements
- Python 3.10+
- Node.js 18+

### 2. Setup
```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium --with-deps

# Frontend
cd frontend
npm install
```

### 3. Run
```bash
# Terminal 1 (Backend)
source .venv/bin/activate
python -m uvicorn backend.main:app --reload

# Terminal 2 (Frontend)
cd frontend
npm run dev
```

---

## 📂 Architecture
- `/backend/agents/` - The "Brains": API, Scrape, and Tailor agents.
- `/backend/scoring/` - The "Logic": Mathematical fit scoring engine.
- `/frontend/src/` - The "Face": React components and Glassmorphism styles.
