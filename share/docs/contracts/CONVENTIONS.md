# Shared Conventions (Server ↔ Edge)

Version: 1.0.0

- Identifiers
  - `camera_id`: string (alphanumeric + underscore), unique per camera
  - `checkpoint_id`: string (alphanumeric + underscore), unique per location
  - `edge_device_id`: string identifier of the edge device (optional for WS, required for MQTT envelope)

- Timestamps
  - ISO-8601 with timezone: `YYYY-MM-DDTHH:MM:SS.sssZ`
  - Example: `2025-01-15T12:34:56.789Z`

- Images
  - Base64-encoded JPEG strings
  - Respect server `MAX_IMAGE_SIZE` (bytes) from `.env` (default 10MB)

- Connectivity Priority
  - Primary: WebSocket events
  - Secondary: REST API
  - Fallback: MQTT

- Message Envelope (optional for WS inbound, recommended for outbound and MQTT)
  - Fields: `message_id` (uuid), `timestamp`, `protocol`, `edge_device_id`, `data_type`, `payload`, `metadata`

- JSON Serialization
  - UTF-8, no BOM; keys in snake_case

- Versioning
  - Semantic versioning for contracts: MAJOR.MINOR.PATCH
  - Breaking changes bump MAJOR and require migration notes in CHANGELOG.md