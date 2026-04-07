# Anti-Gravity Template

This project follows the **Anti-Gravity 3-Layer Architecture**, separating concerns to maximize reliability and predictability.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `planning/directives/`.
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases.
- Natural language instructions like you'd give a mid-level employee.

**Layer 2: Orchestration (Decision making)**
- This is the AI's job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, and update directives with learnings.
- The AI acts as the glue between intent and execution.

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts (or other languages) in `execution/`.
- Environment variables, api tokens, etc. are stored in `.env`.
- Handle API calls, data processing, file operations, database interactions.
- Reliable, testable, fast. Use scripts instead of manual work.

## Directory Structure
- `planning/` - For project blueprints, notes, architectural decisions, and SOPs (`directives/`).
- `execution/` - For deterministic Python scripts, tool implementations, and core logic (Layer 3).
- `testing/` - For unit tests and validation scripts.
- `deliverables/` - For final generated outputs, exported reports, or delivery artifacts.
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `Skills/` - Skills that extend the AI agent's capabilities with specialized knowledge, workflows, or tool integrations.
