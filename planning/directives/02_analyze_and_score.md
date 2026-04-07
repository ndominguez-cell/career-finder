# Directive: 02 Analyze and Score
**Goal:** Analyze the scraped job listings against the candidate's profile/resume and assign a match score.

## Inputs
- `.tmp/raw_jobs.json` (from step 01)
- User profile or resume (e.g., `planning/candidate_profile.md` or PDF extraction)

## Tools/Scripts
- `execution/analyzer.py`

## Instructions
1. Load the raw jobs and the candidate profile.
2. For each job, pass the description and candidate profile to the `analyzer.py` script (which may use an LLM).
3. The analyzer should output a score (0-100) and a brief reasoning on why it's a match.
4. Filter out jobs below a certain threshold parameter (e.g., score < 70).
5. Compile the passing jobs into a summarized daily report.

## Expected Output
- A markdown or CSV report in `deliverables/report_<date>.md` containing the top matches.
