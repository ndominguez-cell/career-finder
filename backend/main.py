from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Header, Query
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import io
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from backend.agents.api_agent import run_api_agent
from backend.agents.scrape_agent import run_scrape_agent
from backend.agents.resume_tailor import draft_tailored_resume, generate_application_email
from backend.scoring.engine import JobInput, CandidateInput, score_job_fit

app = FastAPI(title="Career Finder API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class TailorRequest(BaseModel):
    job: dict
    base_resume: str = ""
    openai_key: Optional[str] = None
    positioning_mode: str = "balanced"
    candidate_notes: str = ""

class EmailRequest(BaseModel):
    job: dict
    top_qualifications: str = ""
    hiring_manager: str = ""
    openai_key: Optional[str] = None

class ScoreRequest(BaseModel):
    job: JobInput
    candidate: CandidateInput
    positioning_mode: str = "balanced"

# ── Stored resume text (session-level, single user for MVP) ──────────────────
_resume_store: dict = {"text": "", "profile": {}}


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """Parse uploaded PDF/doc resume and extract text + infer profile."""
    content = await file.read()

    extracted_text = ""
    target_role = "Software Engineer"

    try:
        if file.filename.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                extracted_text += (page.extract_text() or "") + "\n"

            tl = extracted_text.lower()
            skills = []
            for kw in ["react", "python", "node", "aws", "typescript", "java",
                        "c++", "matlab", "abaqus", "stk", "ros2", "docker"]:
                if kw in tl:
                    skills.append(kw.title() if kw not in ["c++", "ros2", "aws"] else kw.upper())

            for role_kw, role in [("frontend", "Frontend Engineer"),
                                   ("backend", "Backend Engineer"),
                                   ("data", "Data Engineer"),
                                   ("aerospace", "Aerospace Engineer"),
                                   ("systems", "Systems Engineer")]:
                if role_kw in tl:
                    target_role = role
                    break

            profile = {
                "title": target_role,
                "skills": skills or ["Python", "React"],
                "location": "Remote",
                "raw_text_length": len(extracted_text),
            }
        else:
            profile = {"title": target_role, "skills": ["Python", "React"],
                       "location": "Remote", "note": "Non-PDF file"}

    except Exception as e:
        extracted_text = ""
        profile = {"title": "Software Engineer", "skills": ["Python"],
                   "location": "Remote", "error": str(e)}

    # Store for session use
    _resume_store["text"] = extracted_text
    _resume_store["profile"] = profile

    return {"filename": file.filename, "status": "Parsed successfully!", "profile": profile}


@app.get("/fetch_jobs")
async def fetch_jobs(
    x_searchapi_key: Optional[str] = Header(None),
    role: str = Query("Software Engineer"),
    location: str = Query("Remote"),
):
    """Run both agents in parallel and return scored job list."""
    # Build dynamic queries from the detected resume profile
    target_queries = [
        f"{role} {location}",
        f"Senior {role} Remote",
    ]
    target_boards = ["https://news.ycombinator.com/jobs"]

    api_jobs     = run_api_agent(target_queries, passed_api_key=x_searchapi_key)
    scraped_jobs = await run_scrape_agent(target_boards)

    all_jobs = api_jobs + scraped_jobs
    resume_text = _resume_store.get("text", "")

    scored = []
    for job in all_jobs:
        candidate = CandidateInput(resume_text=resume_text or "Python React")
        job_input = JobInput(
            title=job.get("title", ""),
            company=job.get("company", ""),
            description=job.get("description", ""),
        )
        result = score_job_fit(job_input, candidate)
        job["score"] = result.overall_fit_score
        job["reasoning"] = result.recommendation
        job["matched_keywords"] = result.matched_keywords
        job["missing_keywords"] = result.missing_keywords
        job["inferred_domains"] = result.inferred_domains
        scored.append(job)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"status": "success", "jobs": scored}


@app.post("/score-job")
def score_job(req: ScoreRequest):
    """Deterministic pre-LLM job fit scorer."""
    result = score_job_fit(req.job, req.candidate, req.positioning_mode)
    return result


@app.post("/tailor_resume")
async def tailor_resume(req: TailorRequest):
    """
    3-step LLM pipeline:
    Step 1 → Tailor resume with master prompt + recruiter psychology
    Step 2 → Self-critique and refine
    """
    resume_text = req.base_resume or _resume_store.get("text", "")
    result = draft_tailored_resume(
        job_details=req.job,
        base_resume_text=resume_text,
        openai_key=req.openai_key,
        positioning_mode=req.positioning_mode,
        candidate_notes=req.candidate_notes,
    )
    return {"tailored_resume": result}


@app.post("/generate-email")
async def generate_email_endpoint(req: EmailRequest):
    """Generate a short high-conversion application email."""
    result = generate_application_email(
        job_details=req.job,
        top_qualifications=req.top_qualifications,
        hiring_manager=req.hiring_manager,
        openai_key=req.openai_key,
    )
    return {"email": result}


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
