# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Appointment Booking App

## Stack
- Backend: FastAPI (Python), PostgreSQL, SQLAlchemy
- Frontend: React + Vite, shadcn/ui
- Auth: JWT, hashed passwords (bcrypt)
- Local dev: Docker Compose for Postgres
- Deploy: Render (API), Vercel (frontend)

## Domain
Two roles: providers and clients. Providers create availability slots. Clients book open slots. A slot can only be booked once — enforce this with a unique constraint at the database level, not just in application code.

## Conventions
- Keep endpoints in routers/, models in models/, schemas in schemas/
- Write a pytest test for every endpoint
- No secrets in code; use environment variables

## Context
Portfolio project built by a CS student. Prefer clear, readable code over clever abstractions. Explain non-obvious decisions in comments.

## Backend Skeleton

The backend lives in `backend/`. System Python is 3.9 and too old for the pinned dependencies — always create the venv with `python3.12` explicitly (installed via Homebrew at `/opt/homebrew/bin/python3.12`), never plain `python3`.

Setup (first time):
```
cp .env.example .env          # from repo root, then fill in real values
docker compose up -d          # starts Postgres
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API:
```
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload
```
Visit `http://localhost:8000/health` — returns `{"status": "ok", "database": "connected"}` if Postgres is reachable, or a 503 if not.

Run tests (requires Postgres running via `docker compose up -d`):
```
cd backend && source .venv/bin/activate
pytest
```

`config.py` resolves `.env` relative to its own file location (not the process's working directory), so these commands work whether uvicorn/pytest are launched from `backend/` or the repo root.

`requirements.txt` is a full `pip freeze` — exact pins, not just direct dependencies. To add a package: install it in the venv, then re-run `pip freeze > requirements.txt`.
