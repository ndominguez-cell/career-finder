# Directive: 01 Scrape Jobs
**Goal:** Gather job listings based on defined criteria and store them for analysis.

## Inputs
- Search criteria (Role, Location, Remote status)
- Target job boards (e.g., LinkedIn, Indeed, direct company sites)

## Tools/Scripts
- `execution/scraper.py`

## Instructions
1. Read the user configuration (e.g., from a JSON file or environment variables).
2. Execute the scraper script with the provided parameters.
3. Handle any CAPTCHA or blocking gracefully (log the failure and proceed).
4. Save the raw scraped data into `.tmp/raw_jobs.json`.

## Expected Output
- A `.tmp/raw_jobs.json` file containing job descriptions, links, and metadata.
