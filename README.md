# LPR Monorepo (Server + Edge)

Monorepo for License Plate Recognition system:
- `server/` — LPR Server v3 (Flask + Socket.IO + SQLAlchemy + PostgreSQL)
- `edge/` — AI Camera app (Raspberry Pi + Hailo), imported via git subtree from `aicamera`
- `share/` — shared docs, tools, and future shared libs

Use `instruction.md` for detailed setup, connectivity, and deployment SOP.

## Current Status
- Codebase reorganized to monorepo with history preserved
- Edge integrated via git subtree; can sync from upstream `aicamera` later
- Shared documentation moved to `share/docs/`
- Cursor IDE rules and GitHub workflows added for path-filtered CI

## Quick Start

Server (dev):
```bash
cd server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python run.py
```

Edge (device):
```bash
cd edge
bash setup_env.sh
# Dev run
gunicorn --config gunicorn_config.py v1_3.src.wsgi:app
```

Sync edge with upstream `aicamera` when needed:
```bash
git fetch edge-origin
git subtree pull --prefix=edge edge-origin main -m "chore(edge): pull upstream"
```

## Repository Structure
```
server/                 # LPR Server v3
  src/                  # Flask app, services, models, blueprints
  templates/            # UI templates
  requirements.txt
  env.example
edge/                   # Edge AI Camera app (subtree from aicamera)
  v1_3/src/
  systemd_service/
  requirements.txt
share/
  docs/                 # Shared documentation
  tools/                # Shared scripts (future)
  libs/                 # Shared libs (future)
```

## Issue Labels & Workflow
- Labels: `server`, `edge`, `share`, `docs`, `bug`, `enhancement`, `chore`, `breaking-change`, `ci`
- Commit scopes: `server:`, `edge:`, `share:`, `docs:`
- Path-filtered CI runs server checks on `server/**` changes and syntax checks on `edge/**`

---

## Roadmap / แผนงาน (MVP ➜ Quality & Performance)

This roadmap covers both Server and Edge to deliver an MVP first, then iterate on performance, completeness, and a unified UI theme and code style.

### Epics (High-level)
1) Connectivity & Messaging (WS primary, REST secondary, MQTT fallback)
2) Data Model & Persistence (PostgreSQL, SQLAlchemy models, migrations later)
3) Web UI & Theme Unification (Bootstrap 5, shared components & templates)
4) Edge Inference Pipeline (camera, inference, payloads)
5) Observability & Health (metrics, logs, health pages)
6) Deployment & Ops (systemd, scripts, config)
7) Shared Code Style & Patterns (linting, structure, shared libs)

### Milestones / ไมล์สโตน

- M0: Monorepo Consolidation (DONE)
  - Move server → `server/`, import edge → `edge/`, create `share/`
  - Add SOP (`instruction.md`), IDE rules, path-filtered CI

- M1: MVP Core (Minimum Viable Product)
  - Goal: End-to-end detection from edge → server, stored and visible on UI
  - Server
    - [ ] Finalize `.env` and defaults (DB, WS, storage) (server/config.py)
    - [ ] Ensure WS endpoints: `camera_register`, `lpr_data`, `health_status` stable
    - [ ] Persist detections (models: `cameras`, `lpr_records`, `blacklist_plates`)
    - [ ] Minimal dashboard: recent detections, camera status
    - [ ] REST endpoints for basic queries `/api/records`, `/api/cameras`
  - Edge
    - [ ] Stable camera pipeline: capture ➜ detect ➜ pack WS payload
    - [ ] Health ping + status to server on interval
    - [ ] Config via env/setup script; start reliably via systemd
  - Share
    - [ ] Define unified detection/health payload schema (document in `share/docs/`)

- M2: Theme & UX Baseline / ปรับ UI Theme
  - Goal: Unified look & feel across server and edge web
  - Server
    - [ ] Establish Bootstrap 5 base theme (colors, typography, components)
    - [ ] Refactor templates to shared layout blocks (navbar, footer, cards)
  - Edge
    - [ ] Align debug/status pages to same theme (if applicable)
  - Share
    - [ ] Create `share/docs/ui-guidelines.md` (theme, components, accessibility)
    - [ ] Add optional `share/tools/ui-assets/` (logos, CSS snippets)

- M3: Performance & Resilience / ประสิทธิภาพและความทนทาน
  - Server
    - [ ] DB indexing for hot queries (by `timestamp`, `camera_id`, `plate_number`)
    - [ ] WS throughput tuning; image write throughput & rotation
    - [ ] Configurable image compression / size limits
  - Edge
    - [ ] Inference latency profiling; frame rate & pipeline balance
    - [ ] Retry/backoff for WS; optional MQTT fallback publisher
  - Share
    - [ ] Document perf targets (latency, TPS) and tuning matrix

- M4: Observability & Ops / การมอนิเตอร์และการปฏิบัติงาน
  - Server
    - [ ] Health pages and metrics endpoints (basic JSON metrics)
    - [ ] Log policy: rotation, levels; structured logs (optional)
  - Edge
    - [ ] Device health reporting (thermal, FPS, memory) payloads
  - Share
    - [ ] Operating runbooks in `share/docs/ops/`

- M5: Maintainability & Code Quality / บำรุงรักษาและคุณภาพโค้ด
  - Server & Edge
    - [ ] Adopt pre-commit hooks (black/ruff/isort) — document first
    - [ ] Introduce type hints progressively where valuable
    - [ ] Consistent error handling, guard clauses, and logging
  - Share
    - [ ] Define coding patterns and examples in `share/docs/guides/`

### Issue & Task Breakdown / รายการงาน
Use GitHub Issues with labels and these suggested categories.

- Connectivity & Messaging
  - [ ] Server: finalize WS handlers and schemas
  - [ ] Edge: implement WS client with reconnect/backoff
  - [ ] Optional: MQTT topics (see `server/mqtt_config.py`)

- Data & Persistence
  - [ ] Validate models vs. UI and API
  - [ ] Seed data scripts (optional)

- Web UI & Theme
  - [ ] Base layout templates (server)
  - [ ] Unified theme CSS and components

- Edge Pipeline
  - [ ] Camera capture stability tests
  - [ ] Payload conformance tests

- Observability & Ops
  - [ ] Health endpoints
  - [ ] Journal log review, rotation

- Code Style & Patterns
  - [ ] Pre-commit config proposal (documented, opt-in)
  - [ ] Path-based lint/format CI (later)

### Definition of Done / เงื่อนไขสำเร็จ (per milestone)
- MVP (M1): Edge can send detections and health; server persists and shows them; basic UI and APIs work; instructions reproducible.
- Theme (M2): Consistent Bootstrap 5 theme across pages; UI guidelines documented.
- Performance (M3): Meets agreed latency/throughput targets on test hardware.
- Observability (M4): Health/metrics endpoints and operational runbooks exist.
- Maintainability (M5): Style tools adopted with documentation; CI green on path checks.

---

## Contributing / การมีส่วนร่วม
- Use PR template, label by path: `server`, `edge`, `share`, `docs`
- Keep changes scoped and tested; follow `.cursor/.cursorrules` and `instruction.md`
- File issues using templates, include environment and reproduction steps

## License
See `edge/LICENSE` (for edge subtree). Add a top-level license if needed for the monorepo.