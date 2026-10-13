# FastAPI Starter

A FastAPI learning project built around a Todos application with JWT authentication, user and admin routes, and SQLAlchemy persistence (SQLite by default, PostgreSQL optional).

## Tech Stack

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for dependency and environment management
- FastAPI, SQLAlchemy, Alembic
- passlib + bcrypt, python-jose (JWT)
- pytest, pytest-asyncio, httpx2

## Project Structure

```
src/
├── fastapi_starter/                 # Minimal FastAPI "hello world" app
├── fastapi_oop/                     # FastAPI OOP examples
├── fastapi_todos_app/               # Todos app (routers: auth, todos, admin, users)
└── fastapi_todos_app_with_alembic/  # Todos app with Alembic migrations and tests
```

The application entrypoint is configured in [pyproject.toml](pyproject.toml) under `[tool.fastapi]` (currently `fastapi_todos_app.main:app`).

## Getting Started

Install dependencies:

```bash
uv sync
```

## Run the Application

```bash
uv run fastapi dev
```

The API is served at http://127.0.0.1:8000, with interactive docs at http://127.0.0.1:8000/docs.

## Database

By default the app uses SQLite (`todosapp.db`, created in the working directory). To use PostgreSQL, change `SQLALCHEMY_DATABASE_URL` in the app's `database.py`.

### Migrations (`fastapi_todos_app_with_alembic`)

```bash
cd src/fastapi_todos_app_with_alembic
uv run alembic upgrade head
```

## Run Tests

```bash
uv run pytest
```

## Export Requirements

```bash
uv pip freeze > requirements.txt
```

## Documentation

See [FASTAPI_GUIDE.md](FASTAPI_GUIDE.md) for a summary of the FastAPI implementation patterns used in this repo (GET/POST/PUT/DELETE routes, request validation, dependency injection, database access, and JWT authentication), with code snippets from the source.
