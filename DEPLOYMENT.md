# AEGIS TERMINAL Deployment

## Docker + SQLite (default)

```bash
docker compose up --build
```

Open `http://localhost:8000`.

SQLite is persisted in the `aegis_data` Docker volume.

## PostgreSQL / TimescaleDB

Use the optional production database compose file:

```bash
docker compose -f docker-compose.postgres.yml up --build
```

This sets `AEGIS_DATABASE_URL` to PostgreSQL and keeps the database in the `timescale_data` volume. The application database layer supports SQLite for local development and PostgreSQL for scale-out deployments.

## Background telemetry

The FastAPI lifespan starts a managed collector. The interval is controlled by `AEGIS_COLLECT_INTERVAL` and defaults to 15 seconds. Host telemetry, process summaries and lawful open-data tracking are collected without blocking HTTP requests.

The dashboard receives collector updates through:

`/ws/telemetry`

REST polling remains available as a fallback.

## SIEM / log export

Structured events are available as JSON Lines through:

`GET /api/logs/json`

Optional Syslog forwarding is enabled with:

- `AEGIS_SYSLOG_HOST`
- `AEGIS_SYSLOG_PORT` (default `514`)

Check configuration with `GET /api/logs/syslog/status` and send a test event with `POST /api/logs/syslog/test`.

The event schema contains timestamp, source, event type, severity and data so the stream can be adapted to ELK, Splunk or another SIEM pipeline.

## Security boundary

Aegis remains a defensive platform. Tracking adapters use lawful public/open data only, file inspection never executes selected files, and the platform exposes no credential theft, exploitation, persistence or unauthorized intrusion functionality.
