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

## Preventing double-booking

A slot can only be booked once, and that guarantee lives in the database, not the application: `bookings.slot_id` has a `UNIQUE` constraint (see `backend/app/models/booking.py`).

This matters under concurrent requests. If the check were "query whether the slot is already booked, then insert if not," two simultaneous requests for the same slot could both pass the check before either one commits — a classic time-of-check-to-time-of-use race that ends in two bookings for one slot. Instead, `POST /bookings` inserts optimistically and lets Postgres enforce uniqueness atomically; the losing request's `IntegrityError` is caught and turned into a clean `409 Conflict` (see `backend/app/routers/bookings.py`) rather than a corrupted double-booking or an unhandled `500`.
