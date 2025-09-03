## DINOv3 Utilities Dashboard - UI/UX Implementation Plan

### Goals
- Provide a single web dashboard to invoke any exposed API endpoint.
- Auto-discover endpoints from the FastAPI OpenAPI schema to minimize manual upkeep.
- Support file uploads, JSON bodies, path params, and query params per endpoint.
- Show request/response previews, timing, and status.

### Scope
- Read-only configuration; no authentication initially.
- Browsers: modern Chromium/Firefox/Edge.
- Deployed as part of existing FastAPI app at `/dashboard` with static assets.

### Information Architecture
- Global header: title, base URL selector, health indicator.
- Left sidebar: endpoint groups (tags) from OpenAPI, searchable.
- Main panel: endpoint details and dynamic form
  - Method, path, description
  - Parameters
    - Path params (string/number)
    - Query params
    - Headers (optional free-form key/value editor)
  - Request body
    - `multipart/form-data` with file inputs when schema indicates `UploadFile` or `binary`
    - `application/json` with a JSON editor and example template
  - Execute button + cURL copy
  - Response viewer: status, time, headers, JSON/body

### User Flows
1) Select endpoint from sidebar → dynamic form renders.
2) Fill fields / upload files → click Execute → shows loading state.
3) Request sent to same origin (respecting `/api/v1` prefix) → response appears.
4) Copy cURL or JSON to clipboard as needed.

### Technical Design
- Route: FastAPI serves `/dashboard` (HTML) and `/static/dashboard/*` (JS/CSS).
- Data source: `/openapi.json` for schema, `/` for basic service info, `/api/v1/health` for health.
- Frontend: vanilla JS + minimal CSS (no build step). Single-page app pattern.
- Parsing OpenAPI:
  - Group endpoints by `tags` imported from routers.
  - Identify request body content types and parameter locations (`path`, `query`).
  - Detect `binary`/`string` format: `binary` → file input, otherwise text/number inputs.

### Minimal Feature Set (MVP)
- Endpoint discovery and grouping by tag.
- Dynamic form for parameters and JSON body editor.
- File upload support for multipart.
- Execute and display response JSON/text.
- Basic error handling and status badges.

### Nice-to-Have (Phase 2)
- Persist recent requests per endpoint in `localStorage`.
- Dark mode.
- Collapsible sections and keyboard nav.
- Streaming responses display if applicable.

### Testing Plan
- Smoke test representative endpoints:
  - `POST /api/v1/upload-media` with `file` input
  - `POST /api/v1/extract-features` JSON
  - `POST /api/v1/calculate-similarity` JSON
  - `GET /api/v1/health` no params
- Validate CORS not needed for same-origin dashboard.

### Rollout
- Add to app without changing API paths.
- Document usage in this file; keep `API_REFERENCE.md` as authoritative.

### How to Run
- Ensure the Python venv is active and app dependencies are installed.
- Start the API server (examples):
  - Windows PowerShell: `venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 3012`
  - Or use the provided script if configured: `scripts/start_dev.ps1`
- Open the dashboard at `http://localhost:3012/dashboard`.
- The dashboard fetches `http://localhost:3012/openapi.json` automatically and checks `GET /api/v1/health`.

### Open Questions
- None for MVP. Authentication may be added later.

---

## Implementation Log

1. Create `/dashboard` route and serve static assets [Done]
   - Added static mount at `/static` and HTML route `/dashboard` in `app/main.py`.
   - Created `app/static/dashboard/index.html`, `styles.css`, `ui.js`.
2. Implement frontend: load `/openapi.json`, render groups and forms [Done]
   - Parses OpenAPI, groups by tags, dynamic forms for path/query and JSON/multipart bodies.
   - Executes requests and shows responses; copies cURL.
3. Add styles and UX refinements [Done]
   - Minimal responsive layout with dark theme for clarity.
4. Smoke-test endpoints and update docs [Pending]
   - Next: verify `upload-media`, `extract-features`, `calculate-similarity`, and `health` via the dashboard once the API backend and dependencies (e.g., database/model) are running locally.


