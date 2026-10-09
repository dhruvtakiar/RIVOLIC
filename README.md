# RIVOLIC

RIVOLIC is a student-prototype Water Conservation Recommendation System. It turns self-reported household routines into transparent, deterministic water-use estimates and practical conservation guidance. It does **not** measure meter data and makes no scientific-certification claim.

## Architecture

- `frontend/` — React + Vite UI with Chart.js doughnut breakdown.
- `backend/` — Flask JSON API with session-based authentication.
- `backend/database/rivolic.db` — SQLite database, created automatically on backend start.
- `backend/services/` — calculation, recommendation, scoring, and what-if logic.

## Run locally

Backend (PowerShell):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Frontend (a second terminal):

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). Copy `backend/.env.example` to `backend/.env` and set a unique `SECRET_KEY` before any shared deployment. For development the backend has a fallback key; production must not use it.

## Engine assumptions

`consumption_engine.py` uses visible prototype constants: shower flow 9 L/min, toilet flush 6 L, bath 120 L, dishwasher load 12 L, laundry 50/90 L, gardening session 80 L and car wash 120 L. These vary by fixture, practice, and locality.

`recommendation_engine.py` uses explainable conditions (for example, showers above eight minutes). `scoring_engine.py` calculates a 0–100 prototype indicator from shower duration, flush frequency, outdoor use, habits and machine type. `what_if_engine.py` reruns the same calculator after selected input changes—there is no contradictory formula or external AI.

## API routes

- Auth: `POST /api/auth/register`, `login`, `logout`; `GET /api/auth/me`
- Data: `GET /api/dashboard`, `POST/GET /api/analysis`, `GET /api/analysis/<id>`, `POST /api/analysis/<id>/what-if`
- Account/content: `GET /api/recommendations`, `GET /api/explore`, `GET/PUT /api/profile`

## Data and tests

SQLite stores users (hashed passwords), profiles, analyses, input snapshots, derived totals/breakdowns, scores, potential reductions and associated recommendation snapshots. Explore content is static prototype data. No external APIs are used.

Run logic tests from `backend/` with:

```powershell
python -m pytest tests
```

For production, add a non-development secret manager, HTTPS/cookie configuration, CSRF protection, rate limiting, migrations, robust validation/logging, a production WSGI server, backups, and vetted localized water-use constants.
