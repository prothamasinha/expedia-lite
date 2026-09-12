# Expedia Lite — Part 1

## Repository and commit

GitHub repository: https://github.com/prothamasinha/expedia-lite

Exact Part 1 commit: d70d223f93025a3211fea2b4549ef8173e6205af
## Implementation

Expedia Lite allows users to search for a hotel by name.

The Vue frontend provides the hotel search field, Search button, and results table. FastAPI communicates between the frontend and Python backend. The backend reads `hotels.csv` and `trips.csv`, searches hotel names, and connects matching trips using `hotel_id`.

When a match is found, the application displays the hotel information and available stays. When no match is found, it displays a clear no-results message.

## Verification

### Successful hotel search

Action: Entered `Harbor Lantern Hotel` and clicked Search.

Expected result: The matching hotel and its available stays should appear.

Observed result: Harbor Lantern Hotel was displayed with its location, nightly rate, and two available stays.

Screenshot: https://github.com/prothamasinha/expedia-lite/blob/main/screenshots/Screenshot%202026-09-11%20at%2010.00.09%E2%80%AFPM.png

### No-results search

Action: Searched for a hotel that was not contained in the supplied data.

Expected result: The application should display a clear message that no matching hotel was found.

Observed result: The application displayed `No matching hotels found.`

Screenshot: https://github.com/prothamasinha/expedia-lite/blob/main/screenshots/Screenshot%202026-09-11%20at%2010.00.21%E2%80%AFPM.png

### Manual review

I manually reviewed the Part 1 files in VS Code and verified the frontend, FastAPI backend, CSV search logic, and browser behavior.

## Project context and next steps

README: https://github.com/prothamasinha/expedia-lite/blob/main/README.md

AGENTS.md: https://github.com/prothamasinha/expedia-lite/blob/main/AGENTS.md

Design note: https://github.com/prothamasinha/expedia-lite/blob/main/docs/design.md

Selected prompts: https://github.com/prothamasinha/expedia-lite/blob/main/prompts/part1-prompts.md

Current handoff: https://github.com/prothamasinha/expedia-lite/blob/main/handoffs/current.md

Remaining limitation: Part 1 uses CSV data and does not yet include booking functionality or SQLite persistence.

Next task: Implement SQLite and booking CRUD functionality for Part 2.