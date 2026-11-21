# Changelog

## v4.0.8-railway.1 (2026-11-21)

This is the template's first release, so there are no breaking changes.

- Calibre-Web Automated v4.0.8 (`crocodilestick/calibre-web-automated:v4.0.8@sha256:5e00373854247750cc3e4479b492ae09293ff5e06ed10177f226634d97888679`, Calibre 9.1).
- One Railway volume at `/config` holds the settings, the library (`/config/calibre-library`) and the ingest folder (`/config/cwa-book-ingest`).
- The `admin` password is set from the generated `ADMIN_PASSWORD` on first boot, and the shared session key from upstream's template database is replaced with a random one. The container refuses to start with the default password.
- A failed startup step exits non-zero, so Railway restarts the service. Health check: `/health` on port 8083.
