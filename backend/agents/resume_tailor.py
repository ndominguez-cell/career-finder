import os
from typing import Dict, Optional
from openai import OpenAI

# ── SYSTEM PROMPTS ───────────────────────────────────────────────────────────

SYSTEM_PROMPT_TAILOR = """You are an expert resume strategist, ATS optimization specialist, and technical recruiter.

Your task is to adapt a candidate's master resume for a specific job posting so the final resume is:
1. ATS-friendly
2. Truthful and defensible
3. Strongly aligned to the target role
4. Written to position the candidate as a high-fit applicant without inventing experience

INPUTS
- TARGET_JOB_TITLE: {job_title}
- COMPANY_NAME: {company_name}
- JOB_DESCRIPTION: {job_description}
- MASTER_RESUME: {master_resume}
- CANDIDATE_NOTES: {candidate_notes}
- POSITIONING_MODE: {positioning_mode}

POSITIONING MODE INSTRUCTIONS
- conservative: minimal reframing, high literal accuracy, only use language directly from resume
- balanced: optimize wording and alignment, strengthen verbs and framing
- aggressive: maximum perceived fit using strongest possible framing without fabricating facts

RECRUITER PSYCHOLOGY PRIORITIES
Optimize for:
- "Skimmability" (first 6 seconds of scan)
- Early signal strength (top 1/3 of resume carries most weight)
- Clear role alignment within first 2 bullets of each role
- Tool + method visibility (never buried at the bottom)
- Evidence of execution, not just exposure
- Low cognitive load (clean, direct language)

MANDATORY RULES
- Do NOT invent jobs, degrees, certifications, security clearances, projects, measurable results, or software/tools not in the input.
- Do NOT exaggerate scope beyond what is reasonably supported.
- You may strengthen wording, improve framing, and reorganize content.
- Keep the language concise, professional, and recruiter-friendly.
- Remove fluff, weak adjectives, and filler.
- Use plain-text, ATS-safe formatting.
- If GPA is weak and not required, omit it.

BULLET UPGRADE RULES
Rewrite each bullet to:
- Start with a strong action verb (designed, modeled, analyzed, validated, implemented, optimized, integrated, executed, simulated, tested, built, deployed, automated, coordinated)
- Include a tool, method, or system when possible
- Remove weak phrasing ("responsible for", "helped with", "worked on")
- Increase specificity without adding false data
- Reduce length by 10-20% while increasing clarity

OUTPUT FORMAT — return exactly these sections:

=== TAILORED RESUME ===
[Full ATS-friendly tailored resume in clean plain text]

=== ATS KEYWORDS ADDED / EMPHASIZED ===
[Bulleted list of keywords and phrases incorporated from the job description]

=== POSITIONING STRATEGY ===
[3-7 bullets explaining how the candidate was positioned for this role]

=== GAPS / CAUTIONS ===
[Short list of missing qualifications, weak areas, or interview risks]

=== RED FLAGS ===
[Any overstatement risk, unclear claims, weak bullets, or anything a hiring manager might question]"""


SYSTEM_PROMPT_REFINE = """Review the tailored resume you just produced.

Improve it further by checking:
1. ATS keyword alignment
2. Factual safety — no overstatements
3. Recruiter psychology — strongest content earliest
4. Technical credibility — tools and methods are visible and credible
5. Concision — every line earns its place
6. Section prioritization — most relevant sections appear first
7. Whether the strongest evidence appears in the top third

Then output exactly:

=== IMPROVED FINAL RESUME ===
[Revised version]

=== FINAL IMPROVEMENTS MADE ===
[Bulleted list of specific changes made]"""


SYSTEM_PROMPT_EMAIL = """You are a professional job application coach specializing in high-conversion cover emails.

Write a concise, confident application email for this candidate applying to this specific role.

INPUTS
- JOB TITLE: {job_title}
- COMPANY: {company_name}
- CANDIDATE STRONGEST QUALIFICATIONS: {top_qualifications}
- HIRING MANAGER NAME: {hiring_manager} (use "Hiring Manager" if unknown)

RULES
- 3-5 sentences maximum
- Reference the exact role and company
- Mention 1-2 strongest relevant qualifications (specific, not generic)
- Confident but not desperate tone
- End with a clear call to action (interest in speaking/meeting)
- No filler phrases ("I am writing to express...", "I believe I would be a great fit...")

OUTPUT FORMAT — return exactly:

=== EMAIL ===
Subject: [Specific subject line]

[Email body]"""


# ── EXECUTION ENGINE ─────────────────────────────────────────────────────────

def _get_client(openai_key: Optional[str]) -> Optional[OpenAI]:
    api_key = openai_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def draft_tailored_resume(
    job_details: Dict,
    base_resume_text: str,
    openai_key: Optional[str] = None,
    positioning_mode: str = "balanced",
    candidate_notes: str = "",
) -> str:
    """
    3-step LLM pipeline:
    Step 1 → Tailor resume with master prompt + recruiter psychology
    Step 2 → Self-critique and refine
    Returns combined output.
    """
    client = _get_client(openai_key)
    if not client:
        return (
            "⚠️  No OpenAI API key provided.\n\n"
            "Paste your key in Settings (⚙️) or set OPENAI_API_KEY on the server."
        )

    job_title = job_details.get("title", "Target Role")
    company   = job_details.get("company", "Target Company")
    job_desc  = job_details.get("description", "No description provided.")

    # ── Step 1: Tailor ───────────────────────────────────────────────────────
    tailor_system = SYSTEM_PROMPT_TAILOR.format(
        job_title=job_title,
        company_name=company,
        job_description=job_desc,
        master_resume=base_resume_text,
        candidate_notes=candidate_notes or "None provided",
        positioning_mode=positioning_mode,
    )

    tailor_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": tailor_system},
            {"role": "user",   "content": "Produce the tailored resume now."},
        ],
        temperature=0.4,
    )
    tailor_output = tailor_resp.choices[0].message.content

    # ── Step 2: Refine ───────────────────────────────────────────────────────
    refine_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",    "content": tailor_system},
            {"role": "assistant", "content": tailor_output},
            {"role": "user",      "content": SYSTEM_PROMPT_REFINE},
        ],
        temperature=0.3,
    )
    refine_output = refine_resp.choices[0].message.content

    return f"{tailor_output}\n\n{'='*60}\n\n{refine_output}"


def generate_application_email(
    job_details: Dict,
    top_qualifications: str,
    hiring_manager: str = "",
    openai_key: Optional[str] = None,
) -> str:
    """
    Generates a short, high-conversion application email for a specific job.
    """
    client = _get_client(openai_key)
    if not client:
        return "⚠️  No OpenAI API key provided. Add it in Settings (⚙️)."

    email_prompt = SYSTEM_PROMPT_EMAIL.format(
        job_title=job_details.get("title", "Target Role"),
        company_name=job_details.get("company", "Target Company"),
        top_qualifications=top_qualifications,
        hiring_manager=hiring_manager or "Hiring Manager",
    )

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": email_prompt},
            {"role": "user",   "content": "Generate the application email now."},
        ],
        temperature=0.5,
    )
    return resp.choices[0].message.content
