# Directive: 04 Scraping Agent (Direct Sites & Niche Boards)
**Goal:** Scrape diverse, specific career boards that don't aggregate well on major APIs.

## Inputs
- A list of target URLs (e.g., `["https://news.ycombinator.com/jobs", "https://wellfound.com/jobs"]`).
- Target job titles or filters.

## Tools/Scripts
- `backend/agents/scrape_agent.py`

## Instructions
1. Initialize a Playwright headless browser session.
2. Navigate to each URL in the target list.
3. For known layouts, use explicit CSS targeting.
4. For unknown layouts, extract `document.body.innerText` and run it through a fast LLM pass to identify and extract job listings.
5. Consolidate into the universal Career Finder job format.

## Expected Output
- List of standardized job dictionaries `[{"id", "title", "company", "location", "url", "description"}]`.
