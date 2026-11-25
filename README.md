# Mini Shop API

A small FastAPI backend for a mini shop. This branch currently implements the
**authentication module**: users can register, log in and receive a JWT, and all
registered users can be listed. Products, carts and orders will be added next.

## Tech stack

- Python 3.12
- FastAPI (automatic Swagger docs)
- SQLAlchemy 2.x
- PostgreSQL (driver: `psycopg` 3)
- Pydantic v2 (`EmailStr` for email validation)
- bcrypt (password hashing)
- PyJWT (access tokens)
- python-dotenv (`.env` configuration)

## Project structure

| File | Responsibility |
|---|---|
| `config.py` | Reads settings from `.env` (`DATABASE_URL`, `SECRET_KEY`, token expiry) |
| `database.py` | Creates the SQLAlchemy `engine` and `Base` |
| `models.py` | Database tables — currently the `User` table |
| `schemas.py` | Pydantic request/response shapes shown in Swagger |
| `repository.py` | **Only** file that talks to the database (`with Session(engine) as db`) |
| `services.py` | Business logic: hashing, token creation, login/register rules |
| `routes.py` | API endpoints; calls `services` only |
| `main.py` | Creates the app, creates tables, includes routers |
| `.env.example` | Commit-safe template with placeholder values |
| `requirements.txt` | Pinned dependencies |

Dependency direction: `routes → services → repository → database → config`.
Do not put SQL in `routes.py` or `services.py`, and do not use a database
session outside `repository.py`.

## Setup

### 1. Create and activate a virtual environment (WSL)

```bash
cd ~/Coding/python/infx-mini-shop-backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Create the PostgreSQL database

```bash
sudo -u postgres psql
```

Inside `psql`:

```sql
CREATE USER shop_user WITH PASSWORD 'choose_a_password';
CREATE DATABASE mini_shop OWNER shop_user;
\c mini_shop
GRANT ALL ON SCHEMA public TO shop_user;
\q
```

(PostgreSQL 15+ needs the `GRANT` on `public`.)

You can reuse an existing role instead — the database name must be `mini_shop`.

### 3. Configure `.env`

```bash
cp .env.example .env
```

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/mini_shop
SECRET_KEY=replace-with-a-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a real secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`.env` is gitignored — never commit real credentials. `.env.example` stays in Git with placeholders only.

### 4. Run the app

```bash
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000/docs> for Swagger UI. The `users` table is created
automatically on startup by `Base.metadata.create_all()` in `main.py`.

> `create_all()` only creates **missing** tables. It does not update a table
> after you change a column — use Alembic (already installed) for that later.

## Database schema

`users`

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key, auto increment |
| `name` | varchar(100) | required |
| `email` | varchar(255) | unique, indexed |
| `password_hash` | varchar(100) | bcrypt hash — the plain password is never stored |

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create an account. Body: `name`, `email`, `password` (min 8 chars). Returns `id`, `name`, `email`. |
| `POST` | `/auth/login` | Body: `email`, `password`. Returns a bearer JWT. |
| `GET` | `/users` | Lists all users (`id`, `name`, `email` only). Currently public. |

### Register

```json
{ "name": "Asser", "email": "asser@example.com", "password": "supersecret" }
```

`201 Created` →

```json
{ "id": 1, "name": "Asser", "email": "asser@example.com" }
```

Duplicate email → `409 Conflict`.

### Login

```json
{ "email": "asser@example.com", "password": "supersecret" }
```

`200 OK` →

```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

Wrong email or password → `401 Unauthorized`. Both cases use the same message so
we don't reveal which emails are registered.

## How authentication works

1. **Register** — Pydantic validates the input; `services.py` hashes the password
   with bcrypt (unique salt each time); `repository.py` inserts only the hash.
2. **Login** — the stored hash is checked with `bcrypt.checkpw()`. On success,
   `services.py` signs a JWT containing `sub` (user id), `email` and `exp`.
3. **Responses** — `UserRead` never includes `password_hash`.

JWT is for carrying identity between requests, **not** for hashing passwords.
Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60).

## Planned work

- Protected cart/order endpoints using `get_current_user` from the JWT
- Products menu and checkout flow
- Alembic migrations instead of `create_all()` for schema changes
