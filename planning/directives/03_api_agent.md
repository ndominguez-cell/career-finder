# Directive: 03 API Agent (Top Job Boards)
**Goal:** Query third-party aggregators (like SerpApi Google Jobs) to extract validated listings from top platforms that lack direct APIs (e.g., LinkedIn, Indeed).

## Inputs
- Search query derived from resume analysis.
- `SERPAPI_KEY` (or similar vendor token).

## Tools/Scripts
- `backend/agents/api_agent.py`

## Instructions
1. Format the search string (e.g. "Software Engineer Remote site:linkedin.com OR site:indeed.com").
2. Query the third-party aggregator.
3. Handle pagination up to N results (determined by user config).
4. Parse the unstructured JSON response into the universal Career Finder job format.

## Expected Output
- List of standardized job dictionaries `[{"id", "title", "company", "location", "url", "description"}]`.
