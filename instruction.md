# Monorepo Setup, Configuration, and Best Practices (Server + Edge)

This repository is now a monorepo with three key directories:
- `server/` — LPR Server v3 (Flask + Socket.IO + PostgreSQL)
- `edge/` — AI Camera app (Raspberry Pi + Hailo, imported from aicamera)
- `share/` — shared docs, tools, and future shared libs

The goal is to keep server and edge development smooth, with clear configuration for DB schema and communication protocols (WebSocket primary, REST and MQTT as secondary/fallback), without Docker.

## 1) Clone and checkout

- Full clone:
```bash
git clone https://github.com/popwandee/lprserver_v3 monorepo
cd monorepo
git switch monorepo/initial
```

- Sparse checkout (only what you need):
```bash
# Server machine
git clone --filter=blob:none --sparse https://github.com/popwandee/lprserver_v3 /opt/monorepo
cd /opt/monorepo && git switch monorepo/initial && git sparse-checkout set server share

# Edge machine
git clone --filter=blob:none --sparse https://github.com/popwandee/lprserver_v3 /opt/monorepo
cd /opt/monorepo && git switch monorepo/initial && git sparse-checkout set edge share
```

## 2) Server setup (no Docker)

- Create venv and install:
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
```

- Key `.env` parameters (see `server/config.py` and `server/env.example`):
```bash
# Flask
FLASK_CONFIG=production            # development|production|testing
SECRET_KEY=change_me_min_32_chars
FLASK_DEBUG=False

# Database (PostgreSQL strongly recommended in prod)
DATABASE_URL=postgresql://lpruser:password@localhost:5432/lprserver_v3
# Dev quick start (file DB):
# DATABASE_URL=sqlite:///lprserver.db

# Storage
IMAGE_STORAGE_PATH=storage/images
MAX_IMAGE_SIZE=10485760

# WebSocket / HTTP
WEBSOCKET_PORT=8765
DEFAULT_HTTP_PORT=5000
DEFAULT_NGINX_PORT=80

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/lprserver.log

# Health / retention
HEALTH_CHECK_INTERVAL_MINUTES=5
HEALTH_CHECK_RETENTION_DAYS=7
DATA_RETENTION_DAYS=30
RECORDS_PER_PAGE=20
```

- Initialize DB schema (PostgreSQL):
```bash
# Create DB/user accordingly, then start the app once to create tables via SQLAlchemy
source .venv/bin/activate
python run.py
# Or run your WSGI server:
# gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```
The core tables include `cameras`, `lpr_records`, and `blacklist_plates` (see `server/src/core/models/*.py`).

- Run development server:
```bash
python run.py
```

- Production with systemd (example):
```ini
[Unit]
Description=LPR Server v3 - Main Flask Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=devuser
Group=devgroup
WorkingDirectory=/opt/monorepo/server
Environment=PATH=/opt/monorepo/server/.venv/bin
Environment=FLASK_CONFIG=production
Environment=PYTHONPATH=/opt/monorepo/server:/opt/monorepo/server/src
ExecStart=/opt/monorepo/server/.venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## 3) Edge setup (Raspberry Pi + Hailo, no Docker)

- Prepare environment (from `edge/README.md`): install Hailo stack and camera support, then:
```bash
cd edge
bash setup_env.sh
# Dev run (adjust as needed):
gunicorn --config gunicorn_config.py v1_3.src.wsgi:app
```

- Systemd (adapted from `edge/systemd_service/aicamera_v1.3.service`):
```ini
[Unit]
Description=AI Camera v1.3 Flask Application
After=network.target
Wants=network.target

[Service]
Type=notify
User=camuser
Group=camuser
WorkingDirectory=/opt/monorepo/edge
Environment=PATH=/opt/monorepo/edge/venv_hailo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=FLASK_ENV=production
Environment=FLASK_APP=v1_3.src.wsgi:app
Environment=PYTHONPATH=/opt/monorepo/edge
ExecStart=/bin/bash -c 'source /opt/monorepo/edge/setup_env.sh && exec gunicorn --config /opt/monorepo/edge/gunicorn_config.py --worker-class gthread --workers 1 --threads 4 v1_3.src.wsgi:app'
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
LimitNOFILE=65536
LimitNPROC=4096
StandardOutput=journal
StandardError=journal
SyslogIdentifier=aicamera_v1.3

[Install]
WantedBy=multi-user.target
```

## 4) Connectivity: protocols and parameters

Primary is WebSocket (Socket.IO), with REST and MQTT as secondary/fallback in the server (`UnifiedCommunicationService`).

- WebSocket (default):
  - Server WS port: `WEBSOCKET_PORT=8765` (set in `server/.env`)
  - Edge should connect to `http://<server-host>:8765` and use events:
    - `camera_register` with `{ camera_id, checkpoint_id, timestamp }`
    - `lpr_data` with detection payloads (see `server/src/services/websocket_service.py`)
    - `health_status` for health reporting

- REST API (secondary):
  - Simple endpoints available under `/api/*` (see `server/README.md`). Use when WS is degraded.

- MQTT (fallback):
  - Configure in server `.env` using `MQTT_*` variables consumed by `server/mqtt_config.py`:
```bash
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TLS_ENABLED=false
MQTT_USERNAME=lpruser
MQTT_PASSWORD=secure_password
MQTT_CLIENT_ID=lprserver_v3
```
  - Topics format (from `mqtt_config.py`):
    - Detection: `lprserver/cameras/{camera_id}/detection`
    - Health: `lprserver/cameras/{camera_id}/health`
    - Config: `lprserver/cameras/{camera_id}/config`
    - Control: `lprserver/cameras/{camera_id}/control`
  - QoS: detection=1, health=0, config=2, control=2. Retain: health=config=true.

Best practice: keep the edge able to send via WS primarily. If needed, add an MQTT client on edge to publish to the topics above.

## 5) Database schema and alignment

Core tables and required fields:
- `cameras` (`camera_id` PK, `name`, `status`, `last_activity`, `ip_address`, `port`)
- `lpr_records` (`camera_id` FK, `plate_number`, `confidence`, `timestamp`, `image_path`, geo fields, blacklist flags)
- `blacklist_plates` (`license_plate_text`, `reason`, `is_active`, `expiry_date`, metadata)

Recommendations:
- Use PostgreSQL in production and set `DATABASE_URL` accordingly.
- Keep schema changes in SQLAlchemy models in `server/src/core/models/*`. If you introduce migrations later, add Alembic.
- Edge should treat `camera_id` and `checkpoint_id` consistently with server expectations in WS messages.

## 6) Environments and secrets

- Never commit real secrets. Copy `server/env.example` to `server/.env` and set strong values.
- For edge, `edge/env.example` currently has GitHub-related variables; add any runtime-specific env as needed beside `setup_env.sh`.

## 7) Development workflow

- Work in isolated areas:
  - Server-only changes inside `server/`
  - Edge-only changes inside `edge/`
  - Shared scripts/libs inside `share/`
- Commit messages with clear scopes: `server:`, `edge:`, `share:`.
- Tests/dev tools:
  - Server: run `python test_system.py`, `test_api.py`, etc. in `server/`.
  - Edge: validate via `gunicorn` run and device tests.

## 8) Deployment updates (pull-based)

- Server script example:
```bash
/opt/monorepo/scripts/deploy_server.sh
```
- Edge script example:
```bash
/opt/monorepo/scripts/deploy_edge.sh
```

## 9) Keeping `edge/` synced with upstream (subtree)

- Pull latest from upstream aicamera:
```bash
git fetch edge-origin
git subtree pull --prefix=edge edge-origin main -m "chore(edge): pull upstream"
```

## 10) Troubleshooting checklist

- Web UI/API not loading:
  - Check `server` logs and ensure `DATABASE_URL` is reachable.
- WS not connecting from edge:
  - Verify server `WEBSOCKET_PORT`, firewall, and that edge connects to the right host.
- Images not saving:
  - Ensure `IMAGE_STORAGE_PATH` exists and is writable by the service user.
- MQTT fallback not working:
  - Verify broker host/port and credentials; confirm topics match `mqtt_config.py`.

## 11) Next steps

- Add `share/libs/` for code shared between server and edge if needed.
- Consider adding Alembic migrations for DB evolution.
- Add CI path filters to run server tests when `server/**` or `share/**` changes, edge checks when `edge/**` or `share/**` changes.