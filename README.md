# Mini Shop API

A small FastAPI backend for a mini shop. Users can register, log in, browse a
public product menu, manage their own cart, and place orders. Swagger UI is the
frontend — no separate UI project.

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

```
.
├── config.py          # settings from .env
├── database.py        # SQLAlchemy engine and Base
├── main.py            # creates tables, includes the routers
├── models/            # database tables
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   └── order.py
├── schemas/           # request/response shapes shown in Swagger
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   └── order.py
├── repository/        # the only folder that talks to PostgreSQL
│   ├── users.py
│   ├── products.py
│   ├── cart.py
│   └── orders.py
├── services/          # business rules: tokens, totals, checkout
│   ├── auth.py
│   ├── users.py
│   ├── products.py
│   ├── cart.py
│   └── orders.py
└── routes/            # thin endpoints; call services only
    ├── auth.py
    ├── users.py
    ├── products.py
    ├── cart.py
    └── orders.py
```

`models/__init__.py` imports all the tables so `create_all()` in `main.py` can
see them. The other folders don't need an `__init__.py` — Python 3 treats them
as packages automatically.

One file = one job. Dependency direction:
`routes → services → repository → database → config`. Do not put SQL in
`routes/` or `services/`, and do not open a database session outside `repository/`.

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

Open <http://127.0.0.1:8000/docs> for Swagger UI. On startup, `main.py` creates
any missing tables. The 5 products are rows in PostgreSQL, not hardcoded in
Python — see [Products in the database](#products-in-the-database).

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

`products`

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `name` | varchar(100) | required |
| `description` | varchar(255) | optional |
| `price` | numeric(10,2) | money as `Decimal`, JSON shows e.g. `"2.50"` |
| `is_available` | boolean | unavailable products cannot be added to cart |

`cart_items` — one row per `(user_id, product_id)`; a user's cart is just their
rows. Columns: `id`, `user_id`, `product_id`, `quantity`.

`orders` — `id`, `user_id`, `total_price`, `created_at` (timestamp with time zone).

`order_items` — one row per product in an order. Columns: `id`, `order_id`,
`product_id`, `name`, `unit_price`, `quantity`, `line_total`. Name and price are
snapshots at checkout, so editing a product later does not rewrite old orders.

## API endpoints

| Method | Path | Token? | Description |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create an account (`name`, `email`, `password` min 8 chars) |
| `POST` | `/auth/login` | No | Returns a bearer JWT (`email`, `password`) |
| `GET` | `/users` | No | Lists users (`id`, `name`, `email` only) |
| `GET` | `/products` | No | Public product menu (the 5 products stored in PostgreSQL) |
| `POST` | `/cart/items` | Yes | Add `{product_id, quantity}`; upserts if already in cart |
| `GET` | `/cart` | Yes | Current user's cart: items, line totals, `total_price` |
| `DELETE` | `/cart/items/{product_id}` | Yes | Remove one product from the current user's cart |
| `POST` | `/orders` | Yes | Checkout: snapshot cart into an order, clear the cart |
| `GET` | `/orders` | Yes | Current user's orders only, newest first, with `created_at` |

### Auth flow

1. **Register** — `POST /auth/register`. Duplicate email → `409 Conflict`.
2. **Login** — `POST /auth/login`. Wrong email/password → `401 Unauthorized`
   (same message for both, so we don't reveal which emails are registered).
3. **Use the token in Swagger** — copy the `access_token` from the login
   response. Click the **Authorize** button (blue lock at the top of Swagger),
   paste **just the token** into the **Value** box (no `Bearer` prefix —
   Swagger adds it), click **Authorize**, then close the dialog. All protected
   endpoints now include the token automatically.

   With curl, pass it as a header:
   ```bash
   curl -H "Authorization: Bearer eyJ..." http://127.0.0.1:8000/cart
   ```
4. **Verification** — the routes use `Depends(get_current_user_id)` from
   `services/auth.py`. FastAPI reads the `Authorization: Bearer <token>` header
   and calls that function before the route. It decodes the JWT with
   `SECRET_KEY` + `HS256`, checks `exp`, and returns the user id from `sub`.
   Missing, expired or invalid token → `401`.

Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60).

### Cart and checkout

- Add items by **product id** (visible in `GET /products`), with an optional
  `quantity` (default 1). Adding the same product twice increases its quantity.
- Unavailable products → `400 Bad Request`. Unknown product id → `404`.
- `GET /cart` shows one line per product with `line_total`, plus the cart's
  `total_price`. Each user sees only their own cart.
- `POST /orders` checks out in one database transaction: it saves each item's
  name/price/quantity into `order_items`, deletes the cart rows, and returns the
  new order including `created_at`. Empty cart → `400 Bad Request`.
- `GET /orders` returns only the current user's orders; other users' orders are
  never visible.

Money uses `Decimal` throughout to avoid float rounding. In JSON it appears as
a string (e.g. `"8.50"`).

## Products in the database

Products are added with SQL directly in `mini_shop`. The app only reads them.
One is marked unavailable so you can test that rejection path:

| id | name | price | available |
|---|---|---|---|
| 1 | Espresso | 2.50 | yes |
| 2 | Latte | 3.50 | yes |
| 3 | Cappuccino | 3.00 | yes |
| 4 | Croissant | 2.00 | yes |
| 5 | Blueberry Muffin | 2.75 | **no** |

```sql
INSERT INTO products (name, description, price, is_available) VALUES
    ('Espresso',         'Strong black coffee',     2.50, TRUE),
    ('Latte',            'Coffee with steamed milk', 3.50, TRUE),
    ('Cappuccino',       'Coffee with foam',        3.00, TRUE),
    ('Croissant',        'Buttery pastry',          2.00, TRUE),
    ('Blueberry Muffin', 'Baked muffin',            2.75, FALSE);
```

To clear test data while keeping the products:

```sql
TRUNCATE TABLE order_items, orders, cart_items, users RESTART IDENTITY CASCADE;
```

## Planned work

- Alembic migrations instead of `create_all()` for schema changes
- Editing products through the API (currently managed directly in PostgreSQL)
