# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 5.2 web application for NFC-based attendance tracking. Users badge in/out via NFC card readers; the app tracks presence, generates statistics, and manages visitor badges.

## Common Commands

### Development (local)
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker (recommended for Windows NFC integration)
```bash
docker-compose up --build
# App available at http://localhost:8000
```

### NFC Windows Agent (run separately on the Windows host)
```bash
pip install pyscard requests
python tools/nfc_agent_windows.py
# Exposes http://localhost:8765/uid for the Docker container to query
```

### Database
```bash
python manage.py makemigrations presence
python manage.py migrate
python manage.py shell  # Django REPL
```

## Architecture

### NFC Backend Abstraction (`presence/nfc_service.py`)
Two backends selectable via `NFC_BACKEND` env var:
- `pcsc` — direct PC/SC access via pyscard (Linux/WSL)
- `agent` — HTTP polling to `NFC_AGENT_URL` (default for Docker on Windows, where the reader is on the host)

The service returns UIDs only on new card presentation (edge detection), not on repeated reads of the same card.

### Django App Structure
- **`presence/models.py`** — 4 models: `Utilisateur` (user+NFC UID), `HistoriquePresence` (entry/exit log), `ConfigurationSession` (key-value settings), `BadgeVisiteur` (visitor badges with daily reset)
- **`presence/views.py`** — all business logic: NFC polling, presence toggling, user CRUD, Excel import/export, visitor badge lifecycle, statistics, retention purge
- **`presence/urls.py`** — 40+ routes covering both pages and JSON API endpoints
- **`templates/presence/`** — server-rendered HTML with Bootstrap 5 + Chart.js; no frontend build step

### Key Runtime Behaviors
- **Admin mode** is toggled per-session (no real auth user), protected by a hashed password stored in `ConfigurationSession`
- **Visitor badges** auto-reset daily at 00:00 (checked on each home page load)
- **Retention policies** (history, logs, inactive users) are configurable in Paramètres and run automatically; last run timestamp stored in `ConfigurationSession`
- Default admin password: `admin123`

### Environment Variables
| Variable | Default | Purpose |
|---|---|---|
| `NFC_BACKEND` | `agent` | `pcsc` or `agent` |
| `NFC_AGENT_URL` | `http://host.docker.internal:8765` | URL for agent backend |
| `SECRET_KEY` | hardcoded dev value | Override for production |

### Static Files
Pre-bundled (Bootstrap, Font Awesome, Chart.js) in `static/`. No build pipeline — edit CSS directly in `static/css/`.
