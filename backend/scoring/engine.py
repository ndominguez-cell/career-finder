import re
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field


# ── Pydantic Models ─────────────────────────────────────────────────────────

class JobInput(BaseModel):
    title: str
    company: Optional[str] = ""
    description: str


class CandidateInput(BaseModel):
    resume_text: str
    candidate_notes: Optional[str] = ""
    skills: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    keyword_match: float
    tool_match: float
    domain_match: float
    experience_alignment: float
    education_match: float
    recruiter_signal: float


class ScoreResponse(BaseModel):
    overall_fit_score: float
    recommendation: str
    missing_keywords: List[str]
    matched_keywords: List[str]
    matched_tools: List[str]
    inferred_domains: List[str]
    strengths: List[str]
    cautions: List[str]
    breakdown: ScoreBreakdown


# ── Keyword Libraries ───────────────────────────────────────────────────────

TOOL_KEYWORDS = {
    "python", "sql", "matlab", "simulink", "c++", "c", "ros", "ros2",
    "abaqus", "ansys", "nastran", "patran", "stk", "solidworks",
    "catia", "nx", "autocad", "labview", "git", "linux",
    "javascript", "typescript", "react", "node", "docker", "kubernetes",
    "terraform", "aws", "gcp", "azure", "figma", "jira", "confluence",
    "tableau", "power bi", "excel", "spark", "hadoop", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy", "java", "go", "rust",
    "postgresql", "mongodb", "redis", "kafka", "airflow", "dbt"
}

ENGINEERING_KEYWORDS = {
    "fea", "finite element analysis", "simulation", "modeling", "modelling",
    "orbital mechanics", "controls", "control systems", "attitude dynamics",
    "structural analysis", "buckling", "stress", "deflection", "optimization",
    "testing", "validation", "verification", "requirements", "systems engineering",
    "numerical methods", "mission analysis", "aerodynamics", "heat transfer",
    "dynamics", "thermodynamics", "geotechnical", "topography",
    "machine learning", "data pipeline", "api design", "microservices",
    "ci/cd", "devops", "agile", "scrum", "product management",
    "full stack", "backend", "frontend", "cloud architecture",
    "data analysis", "etl", "business intelligence", "reporting"
}

DOMAIN_BUCKETS = {
    "structures": {
        "structural", "structure", "stress", "strain", "buckling", "load",
        "fea", "finite element", "fatigue", "materials", "deflection"
    },
    "controls": {
        "control", "controls", "controller", "feedback", "stability",
        "attitude", "guidance", "navigation", "gnc", "dynamics", "simulation"
    },
    "systems": {
        "systems", "requirements", "integration", "verification",
        "validation", "interface", "architecture", "subsystem"
    },
    "simulation": {
        "simulation", "modeling", "numerical", "python", "stk",
        "monte carlo", "analysis", "trajectory", "mission analysis"
    },
    "aerospace": {
        "spacecraft", "aircraft", "orbital", "mission", "aerospace",
        "flight", "satellite", "rocket", "fairing", "rover"
    },
    "software": {
        "software", "api", "backend", "frontend", "full stack", "devops",
        "microservices", "database", "cloud", "deployment", "ci/cd"
    },
    "data": {
        "data", "analytics", "machine learning", "ai", "pipeline",
        "etl", "visualization", "reporting", "dashboard"
    },
    "product": {
        "product", "roadmap", "stakeholder", "prioritization",
        "user research", "metrics", "kpi", "growth"
    }
}

ACTION_VERBS = {
    "designed", "modeled", "analysed", "analyzed", "validated", "implemented",
    "optimized", "integrated", "executed", "supported", "coordinated",
    "simulated", "tested", "developed", "built", "managed", "reviewed",
    "deployed", "automated", "architected", "led", "scaled", "delivered"
}


# ── Helper Functions ────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\.\-\/\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    return normalize(text).split()


def extract_keywords(job_text: str) -> Tuple[List[str], List[str], List[str]]:
    norm = normalize(job_text)
    matched_tools = sorted([kw for kw in TOOL_KEYWORDS if kw in norm])
    matched_eng = sorted([kw for kw in ENGINEERING_KEYWORDS if kw in norm])
    phrases = set(matched_tools + matched_eng)
    return matched_tools, matched_eng, sorted(phrases)


def keyword_overlap(job_terms: List[str], candidate_text: str) -> Tuple[List[str], List[str]]:
    norm_candidate = normalize(candidate_text)
    matched = [term for term in job_terms if term in norm_candidate]
    missing = [term for term in job_terms if term not in norm_candidate]
    return sorted(set(matched)), sorted(set(missing))


def ratio_score(found: int, total: int) -> float:
    if total == 0:
        return 1.0
    return round(found / total, 4)


def detect_recruiter_signal(candidate_text: str) -> float:
    norm = normalize(candidate_text)
    verb_hits = sum(1 for verb in ACTION_VERBS if verb in norm)
    metric_hits = len(re.findall(r"\b\d+%|\b\d+\b", candidate_text))
    section_hits = sum(
        1 for section in ["summary", "education", "skills", "project", "experience"]
        if section in norm
    )

    score = 0.0
    score += min(verb_hits / 8, 1.0) * 0.45
    score += min(metric_hits / 6, 1.0) * 0.30
    score += min(section_hits / 5, 1.0) * 0.25
    return round(score, 4)


def detect_education_match(job_text: str, candidate_text: str) -> float:
    job_norm = normalize(job_text)
    cand_norm = normalize(candidate_text)

    engineering_required = any(term in job_norm for term in [
        "b.s.", "bs", "bachelor", "degree", "engineering", "aerospace",
        "computer science", "master", "m.s.", "phd"
    ])

    if not engineering_required:
        return 1.0
    if any(term in cand_norm for term in ["aerospace engineering", "computer science"]):
        return 1.0
    if "engineering" in cand_norm or "degree" in cand_norm:
        return 0.8
    return 0.3


def experience_alignment_score(job_text: str, candidate_text: str) -> float:
    job_norm = normalize(job_text)
    cand_norm = normalize(candidate_text)

    alignment_terms = [
        "analysis", "simulation", "testing", "design", "integration",
        "validation", "modeling", "requirements", "controls", "structures",
        "systems", "python", "fea", "stk", "ros2",
        "api", "database", "deployment", "automation", "pipeline",
        "architecture", "cloud", "microservices", "machine learning"
    ]
    relevant = [t for t in alignment_terms if t in job_norm]
    found = [t for t in relevant if t in cand_norm]
    return ratio_score(len(found), len(relevant))


def infer_domains(job_text: str) -> List[str]:
    norm = normalize(job_text)
    domains = []
    for domain, words in DOMAIN_BUCKETS.items():
        if any(word in norm for word in words):
            domains.append(domain)
    return sorted(set(domains))


def weighted_fit_score(
    keyword_match: float,
    tool_match: float,
    domain_match: float,
    experience_alignment: float,
    education_match: float,
    recruiter_signal: float,
    mode: str
) -> float:
    if mode == "conservative":
        weights = {
            "keyword": 0.22, "tool": 0.18, "domain": 0.18,
            "experience": 0.22, "education": 0.12, "recruiter": 0.08,
        }
    elif mode == "aggressive":
        weights = {
            "keyword": 0.28, "tool": 0.22, "domain": 0.18,
            "experience": 0.17, "education": 0.05, "recruiter": 0.10,
        }
    else:  # balanced
        weights = {
            "keyword": 0.25, "tool": 0.20, "domain": 0.18,
            "experience": 0.20, "education": 0.08, "recruiter": 0.09,
        }

    score = (
        keyword_match * weights["keyword"] +
        tool_match * weights["tool"] +
        domain_match * weights["domain"] +
        experience_alignment * weights["experience"] +
        education_match * weights["education"] +
        recruiter_signal * weights["recruiter"]
    )
    return round(score * 100, 1)


def recommendation_from_score(score: float) -> str:
    if score >= 80:
        return "High priority application"
    if score >= 65:
        return "Apply with tailored resume"
    if score >= 50:
        return "Apply selectively if role is strategic"
    return "Low fit — deprioritize unless strong referral"


# ── Main Scoring Function ──────────────────────────────────────────────────

def score_job_fit(
    job: JobInput,
    candidate: CandidateInput,
    positioning_mode: str = "balanced"
) -> ScoreResponse:
    candidate_text = " ".join([
        candidate.resume_text,
        candidate.candidate_notes or "",
        " ".join(candidate.skills),
        " ".join(candidate.projects)
    ])

    matched_tools_jd, matched_eng_jd, extracted_terms = extract_keywords(job.description)
    inferred = infer_domains(job.description)

    matched_keywords, missing_keywords = keyword_overlap(
        extracted_terms + matched_eng_jd, candidate_text
    )
    matched_tools, _ = keyword_overlap(matched_tools_jd, candidate_text)

    keyword_match = ratio_score(len(matched_keywords), len(set(extracted_terms + matched_eng_jd)))
    tool_match = ratio_score(len(matched_tools), len(set(matched_tools_jd)))

    domain_hits = sum(
        1 for domain in inferred
        if any(word in normalize(candidate_text) for word in DOMAIN_BUCKETS[domain])
    )
    domain_match = ratio_score(domain_hits, len(inferred))

    experience_alignment = experience_alignment_score(job.description, candidate_text)
    education_match = detect_education_match(job.description, candidate_text)
    recruiter_signal = detect_recruiter_signal(candidate_text)

    overall = weighted_fit_score(
        keyword_match, tool_match, domain_match,
        experience_alignment, education_match, recruiter_signal,
        positioning_mode
    )

    strengths = []
    cautions = []

    if tool_match >= 0.6:
        strengths.append("Strong tool alignment with job requirements")
    if experience_alignment >= 0.65:
        strengths.append("Relevant technical and project experience present")
    if domain_match >= 0.6:
        strengths.append("Resume language aligns with target domain")
    if recruiter_signal >= 0.7:
        strengths.append("Resume shows strong recruiter-readable signal")

    if len(missing_keywords) > 3:
        cautions.append(f"Missing keywords: {', '.join(missing_keywords[:6])}")
    if education_match < 0.8:
        cautions.append("Education may not fully match stated requirements")
    if recruiter_signal < 0.5:
        cautions.append("Resume needs stronger action verbs, metrics, or section clarity")
    if overall < 65:
        cautions.append("Overall fit is moderate — aggressive tailoring recommended")

    return ScoreResponse(
        overall_fit_score=overall,
        recommendation=recommendation_from_score(overall),
        missing_keywords=missing_keywords[:15],
        matched_keywords=matched_keywords[:15],
        matched_tools=matched_tools,
        inferred_domains=inferred,
        strengths=strengths,
        cautions=cautions,
        breakdown=ScoreBreakdown(
            keyword_match=round(keyword_match * 100, 1),
            tool_match=round(tool_match * 100, 1),
            domain_match=round(domain_match * 100, 1),
            experience_alignment=round(experience_alignment * 100, 1),
            education_match=round(education_match * 100, 1),
            recruiter_signal=round(recruiter_signal * 100, 1),
        )
    )
