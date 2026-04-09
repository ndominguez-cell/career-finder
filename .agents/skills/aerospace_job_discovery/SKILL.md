---
name: Aerospace Job Discovery
description: Specialized scraping and discovery for Aerospace and Space engineering jobs across startups and major contractors.
---

# Aerospace Job Discovery Skill

## Overview

This skill is designed to find high-value aerospace engineering opportunities that are often missed by general job aggregators. It targets niche job boards, specific company portals (SpaceX, Blue Origin, NASA), and specialized career platforms like Space Talent.

## Capabilities

- **Targeted Discovery**: Specifically searches for roles like "GNC Engineer", "Satellite Systems Engineer", "Thermal Analysis Engineer", and "Aerospace Structure Design".
- **Company Portal Scraping**: Knows the Lever/Greenhouse tokens for major space players (e.g., SpaceX, Rocket Lab).
- **Niche Board Integration**: Instructions and logic for scraping boards like spacetalent.org and spacecrew.com.

## How to use

1. **Direct Search**: Use the `aerospace_discovery.py` script to fetch the latest postings.
2. **Agent Integration**: This skill is attached to the main application via `backend/agents/aerospace_agent.py`.

## Key Search Terms

- `site:lever.co/spacex "engineer"`
- `site:greenhouse.io "rocket lab" "engineer"`
- `"aerospace engineer" (GNC | Propulsion | Orbital)`
- `site:jobs.boeing.com "aerospace"`
- `site:lockheedmartinjobs.com "aerospace"`

## Implementation Details

The scraper uses a combination of:

- **SearchApi.io**: For wide-net discovery.
- **Direct API hits**: For Lever and Greenhouse based boards.
- **BeautifulSoup**: For parsing company-specific career pages.
