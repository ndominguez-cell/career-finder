import os
from typing import Dict, Optional
from openai import OpenAI


# ── STEP 0: SCORE THE CANDIDATE'S FIT BEFORE ANY REWRITING ──────────────────

SYSTEM_PROMPT_STEP_0_SCORE = """You are a technical recruiter and ATS screening engine.

Given a JOB DESCRIPTION and a CANDIDATE RESUME, produce a brutally honest fit assessment.

OUTPUT FORMAT — return exactly:

=== JOB FIT SCORE ===
- Overall Fit: X / 100
- Strength Areas: [bulleted list]
- Weak Areas: [bulleted list]
- Missing Keywords: [bulleted list of keywords/phrases from the JD not present in resume]
"""


# ── STEP 1: MASTER TAILORING PROMPT ─────────────────────────────────────────

SYSTEM_PROMPT_STEP_1 = """You are an expert resume strategist, ATS optimization specialist, and technical recruiter.

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
- OUTPUT_STYLE: {output_style}

OBJECTIVE
Customize the resume to maximize relevance for the role while preserving factual accuracy. Reframe, reorder, and rewrite existing experience so it matches the employer's likely screening logic, recruiter psychology, and ATS keyword matching.

MANDATORY RULES
- Do NOT invent jobs, degrees, certifications, security clearances, projects, measurable results, or software/tools not supported by the input.
- Do NOT exaggerate scope beyond what is reasonably supported.
- You may strengthen wording, improve framing, and reorganize content for relevance.
- You may infer emphasis from the job description, but not fabricate facts.
- Keep the language concise, professional, and recruiter-friendly.
- Prioritize impact, technical relevance, and keyword alignment.
- Remove fluff, weak adjectives, and filler.
- Optimize for both ATS parsing and human scanning.
- Use plain-text, ATS-safe formatting unless another format is explicitly requested.
- If GPA is weak and not required, omit it unless the input explicitly says to include it.

PROCESS
1. Analyze the job description and extract:
   - required qualifications
   - preferred qualifications
   - tools/software/platforms
   - domain keywords
   - likely recruiter priorities
   - likely hiring manager priorities

2. Analyze the candidate background and identify:
   - directly relevant experience
   - transferable experience
   - technical tools and methods already supported
   - projects or work that can be reframed truthfully for stronger relevance
   - any missing qualifications

3. Rewrite and reorder the resume to improve:
   - keyword match
   - clarity
   - technical credibility
   - perceived fit
   - bullet strength
   - section priority

4. Tailor the summary so it reflects:
   - target role
   - strongest supported technical skills
   - domain fit
   - candidate value proposition

5. Rewrite bullets using this pattern where possible:
   - action verb + task + tool or method + outcome or value
   If no metric exists, improve specificity without inventing one.

6. Prioritize the most relevant content earlier in the document.

7. Produce the final tailored resume.

8. Then produce a brief adaptation report.

OUTPUT FORMAT

Return exactly these sections:

=== TAILORED RESUME ===
[Full ATS-friendly tailored resume in clean plain text]

=== ATS KEYWORDS ADDED / EMPHASIZED ===
[Bulleted list of keywords and phrases incorporated from the job description]

=== POSITIONING STRATEGY ===
[3-7 bullets explaining how the candidate was positioned for this role]

=== GAPS / CAUTIONS ===
[Short list of missing qualifications, weak areas, or interview risks]

RESUME WRITING STANDARDS
- Use strong action verbs
- Use compact bullets
- Avoid first person pronouns
- Avoid dense keyword stuffing
- Avoid generic claims like "hard worker," "team player," or "go-getter"
- Make every line earn its place
- Prefer specific nouns over vague language
- Favor verbs such as: designed, modeled, analyzed, validated, implemented, optimized, integrated, executed, supported, coordinated, simulated, tested

SPECIAL POSITIONING LOGIC
- If the candidate is early-career, emphasize projects, tools, coursework, simulation, analysis, lab work, and applied technical problem-solving.
- If the candidate has nontraditional experience, translate it into operational, analytical, technical, systems, logistics, planning, or coordination language where accurate.
- If the role is in aerospace, defense, robotics, manufacturing, systems, software, or engineering, prioritize engineering methods, tools, validation, modeling, simulation, documentation, and technical execution.
- If the employer is a defense contractor or highly structured engineering organization, emphasize systems thinking, requirements alignment, process discipline, documentation, validation, and cross-functional execution where supported.

QUALITY BAR
The final result should read like a deliberate, highly relevant submission tailored for this exact role, not a generic resume with superficial edits."""


# ── STEP 2: REFINEMENT PROMPT ───────────────────────────────────────────────

SYSTEM_PROMPT_STEP_2_REFINEMENT = """Review the tailored resume you just produced.

Your task is to improve it further by checking:
1. ATS keyword alignment
2. factual safety
3. recruiter psychology
4. technical credibility
5. concision
6. section prioritization
7. whether the strongest evidence appears early enough

Then output exactly:

=== IMPROVED FINAL RESUME ===
[Revised version]

=== FINAL IMPROVEMENTS MADE ===
[Bulleted list]"""


# ── EXECUTION ENGINE ────────────────────────────────────────────────────────

def draft_tailored_resume(
    job_details: Dict,
    base_resume_text: str,
    openai_key: Optional[str] = None
) -> str:
    """
    3-step LLM pipeline:
      Step 0  →  Score the candidate's current fit (before any edits)
      Step 1  →  Tailor the resume using the master prompt
      Step 2  →  Self-critique and refine the tailored resume
    Returns the concatenated output of all three steps.
    """

    # Resolve API key: passed-in key > env var
    api_key = openai_key or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return (
            "⚠️  No OpenAI API key provided.\n\n"
            "Please paste your key in Settings (⚙️) or set OPENAI_API_KEY "
            "as an environment variable on the server."
        )

    client = OpenAI(api_key=api_key)

    job_title = job_details.get("title", "Target Role")
    company   = job_details.get("company", "Target Company")
    job_desc  = job_details.get("description", "No description provided.")

    # ── Step 0: Score ────────────────────────────────────────────────────
    score_user_msg = (
        f"JOB DESCRIPTION:\n{job_desc}\n\n"
        f"CANDIDATE RESUME:\n{base_resume_text}"
    )

    score_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_STEP_0_SCORE},
            {"role": "user",   "content": score_user_msg},
        ],
        temperature=0.3,
    )
    score_output = score_resp.choices[0].message.content

    # ── Step 1: Tailor ───────────────────────────────────────────────────
    tailor_system = SYSTEM_PROMPT_STEP_1.format(
        job_title=job_title,
        company_name=company,
        job_description=job_desc,
        master_resume=base_resume_text,
        candidate_notes="None provided",
        output_style="ATS plain-text",
    )

    tailor_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": tailor_system},
            {"role": "user",   "content": "Please produce the tailored resume now."},
        ],
        temperature=0.4,
    )
    tailor_output = tailor_resp.choices[0].message.content

    # ── Step 2: Refine ───────────────────────────────────────────────────
    refine_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": tailor_system},
            {"role": "assistant", "content": tailor_output},
            {"role": "user",   "content": SYSTEM_PROMPT_STEP_2_REFINEMENT},
        ],
        temperature=0.3,
    )
    refine_output = refine_resp.choices[0].message.content

    # ── Combine all three outputs ────────────────────────────────────────
    combined = (
        f"{score_output}\n\n"
        f"{'='*60}\n"
        f"{tailor_output}\n\n"
        f"{'='*60}\n"
        f"{refine_output}"
    )

    return combined
