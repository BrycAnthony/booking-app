# booking-app

An appointment booking API: providers publish availability slots, clients book them. Built as a portfolio project.

## Tech stack

- **Backend:** FastAPI (Python), PostgreSQL, SQLAlchemy
- **Auth:** JWT access tokens, passwords hashed with bcrypt
- **Local infra:** Docker Compose (Postgres)
- **Frontend:** React + Vite, shadcn/ui (planned — not yet implemented; only the backend exists today)
- **Deploy:** Render (API), Vercel (frontend)

## Running locally

Requires Python 3.12 (system Python may be older — install 3.12 via Homebrew if needed) and Docker.

```bash
cp .env.example .env          # from repo root, then fill in real values
docker compose up -d          # starts Postgres

cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Visit `http://localhost:8000/health` — returns `{"status": "ok", "database": "connected"}` if Postgres is reachable. Interactive API docs (and a working "Authorize" button for JWT auth) are at `http://localhost:8000/docs`.

## Running tests

```bash
docker compose up -d          # Postgres must be running
cd backend && source .venv/bin/activate
pytest
```

Tests run against a real Postgres database (not mocks), with tables created and cleaned between tests — see `backend/tests/conftest.py`. The same suite runs in CI on every push to `main` and on pull requests (`.github/workflows/ci.yml`).

## API overview

| Method | Path              | Description                                  | Access             |
|--------|-------------------|-----------------------------------------------|--------------------|
| GET    | `/health`         | Service + database health check                | Public             |
| POST   | `/auth/signup`    | Create a provider or client account            | Public             |
| POST   | `/auth/login`     | Exchange email + password for a JWT            | Public             |
| POST   | `/slots`          | Publish an availability slot                    | Provider only      |
| GET    | `/slots`          | List open (unbooked) slots                      | Any authenticated user |
| POST   | `/bookings`       | Book an open slot                               | Client only        |
| DELETE | `/bookings/{id}`  | Cancel your own booking                         | Client only (owner) |

## Environment variables

| Variable                       | Required | Default | Notes                                                        |
|--------------------------------|----------|---------|---------------------------------------------------------------|
| `DATABASE_URL`                 | Yes      | —       | e.g. `postgresql+psycopg://user:pass@host:5432/dbname`         |
| `JWT_SECRET_KEY`                | Yes      | —       | Random secret used to sign access tokens; generate with `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `JWT_ALGORITHM`                 | No       | `HS256` |                                                                 |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | No       | `30`    |                                                                 |
| `ALLOWED_ORIGINS`               | No       | `""` (none) | Comma-separated list of origins allowed to call the API from a browser (e.g. `https://myapp.vercel.app`) |
| `PORT`                          | Set by the platform | —       | Render sets this automatically; the app binds to it. Not needed for local dev (`uvicorn --reload` uses 8000). |

Locally these come from the root `.env` file (`cp .env.example .env`). In CI and on Render, there is no `.env` file — these are set directly as real environment variables.

## Deploying (Render)

The API deploys from `backend/Dockerfile`:

1. Create a new Render Web Service from this repo, with **Root Directory** set to `backend`.
2. Render detects the Dockerfile automatically (Environment: Docker).
3. Set the required environment variables above in the Render dashboard — `DATABASE_URL` (pointing at your Render Postgres instance) and `JWT_SECRET_KEY` at minimum, plus `ALLOWED_ORIGINS` once the frontend has a real deployed URL.
4. Health check path: `/health`.

Render injects `PORT` itself; the Dockerfile's `CMD` binds to `0.0.0.0:$PORT` automatically, so no extra configuration is needed for that.

## Preventing double-booking

A slot can only be booked once, and that guarantee lives in the database, not the application: `bookings.slot_id` has a `UNIQUE` constraint (see `backend/app/models/booking.py`).

This matters under concurrent requests. If the check were "query whether the slot is already booked, then insert if not," two simultaneous requests for the same slot could both pass the check before either one commits — a classic time-of-check-to-time-of-use race that ends in two bookings for one slot. Instead, `POST /bookings` inserts optimistically and lets Postgres enforce uniqueness atomically; the losing request's `IntegrityError` is caught and turned into a clean `409 Conflict` (see `backend/app/routers/bookings.py`) rather than a corrupted double-booking or an unhandled `500`.
