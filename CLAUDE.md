# Career Finder AI - Development Guide

## Build & Run Commands
- **Backend (FastAPI):** `python3 -m uvicorn backend.main:app --reload --port 8000`
- **Frontend (Vite/React):** `cd frontend && npm install && npm run dev`
- **Docker:** `docker build -t career-finder . && docker run -p 8000:8000 career-finder`

## Environment Variables
Create a `.env` in the root (already exists with valid keys for testing):
- `SEARCHAPI_KEY`: API key for Google Jobs via SearchApi.io
- `OPENAI_API_KEY`: OpenAI API key for resume tailoring and email generation (GPT-4o)

## Project Structure
- `/backend`: FastAPI application
    - `/agents`: 
        - `api_agent.py`: Fetches jobs from LinkedIn/Indeed via SearchApi
        - `scrape_agent.py`: Playwright scraper for YC Jobs and direct career pages
        - `resume_tailor.py`: GPT-4o powered resume optimization and email generation
    - `/scoring`:
        - `engine.py`: Scans job descriptions against resumes to produce fit scores
- `/frontend`: Vite + React + Vanilla CSS (Glassmorphism design)

## Tech Stack
- **Core:** Python 3.10+, React 18+
- **APIs:** FastAPI, SearchApi, OpenAI
- **Scraping:** Playwright (Headless Chromium)
- **Styling:** Vanilla CSS (Glassmorphism, Vibrant Dark Mode)

## Code Style & Standards
- **Python:** Use type hints, adhere to FastAPI patterns, use `load_dotenv()`.
- **React:** Use functional components and hooks, avoid Tailwind (project uses pure CSS).
- **Deployment:** Vercel for frontend, Render (Docker) for backend.
