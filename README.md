# MindGarden AI

MindGarden AI is a mental wellness companion for students preparing for high-pressure exams like JEE, NEET, UPSC, CAT, GATE, CA, and SSC. It combines daily journaling, mood tracking, evolving memory, and a personalized AI companion to help students understand patterns, reduce burnout, and build healthier study routines.

## What is included in Phase 1

- Secure authentication with access and refresh tokens
- Student onboarding and profile personalization
- AI companion chat with Gemini-first provider abstraction
- Safe fallback mock companion when `GEMINI_API_KEY` is not configured
- Journal and mood logging with encrypted sensitive text storage
- Memory extraction and retrieval to make the companion feel persistent
- Wellness dashboard APIs and a polished responsive frontend shell
- Emotional timeline, emotional heatmap, mood forecast, and weekly reflection reporting
- Goal tracking and habit intelligence with persistent progress logging
- Privacy operations for export, memory reset, journal/conversation deletion, and account deletion
- Forgot-password and demo email-verification flows
- Docker and local development setup

## Stack

- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL in Docker, SQLite fallback for local offline development
- Cache/limits: Redis in Docker, in-memory fallback in local development
- AI: Gemini primary, mock companion fallback

## Repository Layout

```text
apps/
  api/   FastAPI backend
  web/   Next.js frontend
```

## Quick Start

### 1. Configure environment

Copy the example file and fill in secrets:

```powershell
Copy-Item .env.example .env
```

Minimum recommended values:

- `JWT_SECRET`
- `REFRESH_SECRET`
- `ENCRYPTION_KEY`
- `GEMINI_API_KEY` for live AI responses

### 2. Run with Docker Compose

```powershell
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### 3. Run locally without Docker

Backend:

```powershell
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd apps/web
npm.cmd install
npm.cmd run dev
```

## Environment Variables

See `.env.example` for the full list. A few important ones:

- `DATABASE_URL`
- `JWT_SECRET`
- `REFRESH_SECRET`
- `ENCRYPTION_KEY`
- `GEMINI_API_KEY`
- `NEXT_PUBLIC_API_BASE_URL`

## Safety Notes

The companion is designed to be empathetic and supportive, but it is not a doctor or therapist. The backend includes a lightweight safety classifier that escalates sensitive language and recommends reaching out to trusted people or qualified professionals when risk signals appear.

## Verification

Backend code can be sanity-checked offline with:

```powershell
python -m compileall apps/api/app
cd apps/api
python -m unittest discover tests
```

Frontend package installation and runtime verification require dependency installation, which is not bundled into this workspace.

## Do You Need To Do Anything?

For a local demo with the mock companion, no. The app can run without a Gemini key.

For live Gemini responses, you only need to:

- copy `.env.example` to `.env`
- set `GEMINI_API_KEY`
- set strong values for `JWT_SECRET`, `REFRESH_SECRET`, and `ENCRYPTION_KEY`

If you want PostgreSQL and Redis instead of the lightweight local fallback, run through Docker Compose.
