# RIVOLIC

RIVOLIC is a student-prototype Water Conservation Recommendation System. It turns self-reported household routines into transparent, deterministic water-use estimates and practical conservation guidance. It does **not** measure meter data and makes no scientific-certification claim.

## Architecture

- `frontend/` — React + Vite UI with Chart.js.
- `backend/` — Flask JSON API with session-based authentication.
- `backend/services/` — calculation, recommendation, scoring, and what-if logic.
- Local development uses SQLite at `backend/database/rivolic.db`.
- Production uses a managed PostgreSQL-compatible database through `DATABASE_URL` (or `POSTGRES_URL`).

## Local development

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

The local frontend calls `http://localhost:5000` by default. Copy `backend/.env.example` to `backend/.env` if you use a local environment file; do not commit secrets.

## Vercel deployment: two projects

The repository is a monorepo. Deploy it as **two Vercel projects** from the same GitHub repository; Vercel does not use the removed root `vercel.json` service configuration.

### 1. Provision a persistent database

Create a managed PostgreSQL database (for example through Vercel Marketplace, Neon, Supabase, or another trusted provider) and retain its connection string. SQLite is intentionally restricted to local development because Vercel Function filesystems are ephemeral and cannot safely retain account or analysis data between invocations.

### 2. Deploy the Flask API

Create a Vercel project using this repository with **Root Directory** set to `backend`. Vercel detects `app.py` as the Flask WSGI entry point. `backend/vercel.json` excludes test and virtual-environment files from the function bundle.

Set these backend environment variables separately for Preview and Production:

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A unique high-entropy random secret; never reuse the example value. |
| `DATABASE_URL` | The managed PostgreSQL connection string. `POSTGRES_URL` is also accepted. |
| `FRONTEND_ORIGIN` | The exact frontend origin, such as `https://your-frontend.vercel.app`, without a trailing slash. Multiple comma-separated origins are supported when needed. |
| `SESSION_COOKIE_SECURE` | `true` |
| `SESSION_COOKIE_SAMESITE` | `None` when the frontend and API are on different sites; `Lax` is suitable only when your deployment topology permits it. |

Copy the deployed API origin, such as `https://rivolic-api.vercel.app`. Do not include `/api` at the end.

### 3. Deploy the Vite frontend

Create a second Vercel project using the same repository with **Root Directory** set to `frontend`. Vercel detects Vite, and `frontend/vercel.json` provides an SPA fallback.

Set this build-time frontend variable in each environment:

| Variable | Value |
| --- | --- |
| `VITE_API_BASE_URL` | The deployed Flask API origin, for example `https://rivolic-api.vercel.app` |

This is a public API URL, not a secret. Redeploy the frontend after changing it. If it is missing in a production build, RIVOLIC now reports a clear configuration error instead of attempting to fetch `localhost`.

### Verify after deployment

1. Open the frontend production URL and create an account.
2. Confirm the register response is successful and the browser receives a session cookie from the API.
3. Reload the page; `GET /api/auth/me` should remain authenticated.
4. Submit an analysis, reload, and confirm it is still listed in the dashboard history.
5. Log out and confirm a protected route such as `/api/dashboard` returns `401`.

Use `vercel dev` within either the `frontend` or `backend` directory to test that individual Vercel project locally after linking it. A production deployment cannot be certified from this repository alone because it requires your Vercel project settings, deployed domains, and a real managed database.

## Engine assumptions

`consumption_engine.py` uses visible prototype constants: shower flow 9 L/min, toilet flush 6 L, bath 120 L, dishwasher load 12 L, laundry 50/90 L, gardening session 80 L and car wash 120 L. These vary by fixture, practice, and locality.

`recommendation_engine.py` uses explainable conditions (for example, showers above eight minutes). `scoring_engine.py` calculates a 0–100 prototype indicator from shower duration, flush frequency, outdoor use, habits and machine type. `what_if_engine.py` reruns the same calculator after selected input changes—there is no contradictory formula or external AI.

## API routes

- Auth: `POST /api/auth/register`, `login`, `logout`; `GET /api/auth/me`
- Data: `GET /api/dashboard`, `POST/GET /api/analysis`, `GET /api/analysis/<id>`, `POST /api/analysis/<id>/what-if`
- Account/content: `GET /api/recommendations`, `GET /api/explore`, `GET/PUT /api/profile`

## Tests

```powershell
cd backend
python -m pytest tests
```

The backend test suite covers consumption calculations, recommendation generation, conservation scoring, and what-if calculations. The frontend build is validated with `npm run build` from `frontend/`.

## Production hardening

This prototype uses parameterized queries, password hashing, session cookies, API authentication checks, and environment-held secrets. Before public production use, add CSRF protection, rate limiting, database migrations, backups, monitoring, and vetted localized water-use constants.