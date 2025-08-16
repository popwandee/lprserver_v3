# Connectivity (WS / REST / MQTT)

## WebSocket (Socket.IO)
- Port: `WEBSOCKET_PORT` (default 8765)
- Events:
  - `camera_register`: `{ camera_id, checkpoint_id, timestamp }`
  - `lpr_data`: detection payload with images
  - `health_status`: periodic health data

## REST API
- Read endpoints (examples):
  - `GET /api/records?limit=10`
  - `GET /api/cameras`

## MQTT (fallback)
- Broker env keys: `MQTT_BROKER_HOST`, `MQTT_BROKER_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `MQTT_TLS_ENABLED`
- Topics (see `server/mqtt_config.py`):
  - `lprserver/cameras/{camera_id}/detection`
  - `lprserver/cameras/{camera_id}/health`
  - `lprserver/cameras/{camera_id}/config`
  - `lprserver/cameras/{camera_id}/control`
- QoS: detection=1, health=0, config=2, control=2; retain health/config=true

## Payloads
Standard JSON envelope: `message_id`, `timestamp`, `edge_device_id`, `data_type`, `payload`, `metadata`