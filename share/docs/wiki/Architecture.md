# Architecture Overview

## Server
- Flask + Flask-SocketIO application (`server/src/app.py`)
- Services: WebSocket, MQTT, database, health
- Models: `cameras`, `lpr_records`, `blacklist_plates`
- Templates: Bootstrap 5-based UI under `server/templates/`
- Config: `server/config.py` + `.env`

## Edge
- Raspberry Pi + Hailo inference pipeline
- Gunicorn single worker with threads
- Systemd for production start

## Connectivity
- Primary: WebSocket (Socket.IO) events
- Secondary: REST API endpoints
- Fallback: MQTT topics (`server/mqtt_config.py`)

See also: Connectivity page for schemas, topics, and QoS.