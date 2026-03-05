# HRMS Backend API (FastAPI)

This repository implements a modular human‑resources management backend
built with FastAPI, SQLAlchemy and PostgreSQL. It provides:

- user registration and JWT-based login
- per‑user roles and RBAC dependencies
- phone‑number OTP login (MSG91 integration)
- employee entity management linked to the auth system
- department/designation CRUD
- database migrations with Alembic

## Architecture overview

```text
client → FastAPI app
           ├─ /auth      (user/OTP/login)
           ├─ /emp       (employee/department/designation)
           └─ ... other modules ...

↓
PostgreSQL via SQLAlchemy ORM
```

## Key features

- ✅ **JWT Authentication** with bcrypt password hashing
- ✅ **Role‑Based Access Control (RBAC)** via `require_roles` dependency
- ✅ **OTP support** using MSG91 Flow API for phone verification
- ✅ **Employee module** that creates a `User` then an `Employee` record
- ✅ **Database migrations** powered by Alembic
- ✅ Clean separation of modules and in‑memory fallbacks for testing

## Setup

### Prerequisites

- Python 3.11 or 3.12 (⚠️ Python 3.14 has early compatibility issues with SQLAlchemy 2.0.x)
- PostgreSQL 12+

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate venv (Windows)
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/backend_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

If not set, defaults are:
- `DATABASE_URL`: `postgresql+psycopg://postgres:postgres@localhost:5432/backend_db` *(change the username/password to match your local PostgreSQL setup)*
- `SECRET_KEY`: `dev-secret`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`

> **Note:** a mismatched `DATABASE_URL` will cause migrations to fail with a
> password authentication error. The startup logic will catch this and fall
> back to `init_models()` so tables may still be created (useful for quick
> development), but you should correct your URL before deploying or running
> tests.

### Run the Server

```bash
# Activate virtual environment first
source hrms/bin/activate

# Development (with auto-reload)
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --port 8000
```

The server is available at `http://127.0.0.1:8000` by default.

## API Usage

### Core Authentication Endpoints

#### Register a User

- **POST** `/auth/register`
- Body must include `username`, `password` and optional `roles`/`email`/`phone_number`.
- Creates a new user entry and returns the user dict.

#### Username/Password Login

- **POST** `/auth/login`
- Supply `username` and `password`.
- Returns an `access_token` (Bearer JWT) on success.

#### OTP Login

- **POST** `/auth/send-otp` with `phone_number` to generate a one-time code.
- **POST** `/auth/verify-otp` with `phone_number` and `otp` to authenticate.
- SMS is sent via MSG91 Flow; configuration requires `MSG91_AUTH_KEY` and
  `MSG91_OTP_TEMPLATE_ID` environment variables.

#### Get Current User

- **GET** `/auth/me`; requires `Authorization: Bearer <token>` header.
- Returns the currently authenticated user object.

#### Role‑Restricted Endpoint Example

Any route using `Depends(require_roles(...))` enforces the presence of the
specified roles in the user’s `roles` array. A built‑in admin example is
`GET /auth/admin-only`.

## Protecting Routes with RBAC

### Example: Protect a route with a specific role

Use `require_roles` to protect any endpoint based on roles.

```python
from fastapi import APIRouter, Depends
from app.core.rbac import require_roles

router = APIRouter(prefix="/emp", tags=["employee"])

@router.post("/employees")
def create_employee(data: dict, user: dict = Depends(require_roles("hr_admin"))):
    """Only HR admins may add employees."""
    return {"message": "employee created"}

@router.get("/employees")
def list_employees(user: dict = Depends(require_roles("user", "hr_admin"))):
    """Users with 'user' or 'hr_admin' role can view employees."""
    return {"employees": []}
```

### Register the router in `main.py`

```python
from app.modules.employee import routes as emp_routes
app.include_router(emp_routes.router)
```

## Core Components

### 1. Security (`app/core/security.py`)

- `get_password_hash(password)` — Hash a password with bcrypt
- `verify_password(plain, hashed)` — Verify a password against hash
- `create_access_token(subject)` — Create a JWT token
- `decode_token(token)` — Decode and validate JWT
- `get_current_user(token)` — FastAPI dependency to extract user from token

### 2. RBAC (`app/core/rbac.py`)

- `require_roles(*roles)` — Dependency factory to check user roles

```python
# Usage in routes
user: dict = Depends(require_roles("admin"))
user: dict = Depends(require_roles("admin", "moderator"))  # Either role OK
```

### 3. Database (`app/core/database.py`)

- Sync SQLAlchemy engine with psycopg (PostgreSQL)
- `SessionLocal` — Session factory for DB queries
- `init_models()` — Create tables on startup

### 4. Models (`app/core/models.py`)

```python
class User(Base):
    __tablename__ = "users"
    id: int (primary key)
    username: str (unique)
    hashed_password: str
    roles: list (JSONB, e.g., ["user", "admin"])
```


## Employee Module

Employees are modelled separately from users but linked by a foreign key.
Creating an employee performs two actions:

1. creates a corresponding user account (via `auth.services.create_user`)
2. inserts an `employees` record with an autogenerated `employee_code` and
   optional department/designation.

**Endpoints:**

- **POST** `/emp/employees` (body `EmployeeCreate`, contains `email`,
  `password`, plus `position`/`department`/`designation`). Returns
  `EmployeeOut` including `user_id` and `employee_code`.
- **GET** `/emp/employees/{id}` – detailed view with department/designation
  objects.
- **GET** `/emp/employees` – list all employees.
- **PUT** `/emp/employees/{id}` – modify user or employee fields via
  `EmployeeUpdate`.
- **DELETE** `/emp/employees/{id}` – remove employee record.

Departments and designations have their own CRUD endpoints under `/emp`.

### Sample cURL

```bash
curl -X POST http://localhost:8000/emp/employees \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Alice","last_name":"Smith","email":"alice@example.com","password":"secret","position":"Engineer"}'
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── core/
│   │   ├── config.py           # Config (DB URL, SECRET_KEY)
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   ├── models.py           # ORM models (User, Employee, etc.)
│   │   ├── security.py         # JWT & password utilities
│   │   ├── rbac.py             # Role-based access control
│   │   └── __init__.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── routes.py       # Auth + OTP endpoints
│   │   │   └── __init__.py
│   │   ├── employee/           # Employee/department/designation
│   │   │   ├── routes.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── services.py
│   │   └── ... other modules as needed ...
├── requirements.txt            # Dependencies
├── .env                        # Environment variables (not in git)
└── README.md                   # This file
```

## Database Initialization & Migrations

At startup the app invokes `init_models()` which runs `Base.metadata.create_all`
– this is handy for throwing away the database during development. **It
does not perform schema migrations**, so any structural change to models
requires manual intervention or you'll see errors like
`relation "employees" does not exist`.

To manage schema evolution we use **Alembic**:

1. `pip install alembic`
2. `alembic init alembic`
3. Edit `alembic/env.py` to load `app.core.database.Base.metadata` and the
   modules containing models (`auth.models`, `employee.models`, etc.).
4. `alembic revision --autogenerate -m "describe change"`
5. `alembic upgrade head`

Each model change should be followed by a new revision. This keeps dev,
testing and production databases in sync without losing data.

> **Note:** you may still call `init_models()` for ephemeral databases
> (tests, local experiments) but avoid it in environments where data
> matters.

## Troubleshooting

### "Could not connect to database"
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env` matches your PostgreSQL credentials
- Create the database: `createdb backend_db` (psql)

### "User not found" after login
- Ensure user was registered first
- Check username/password match exactly

### "Not enough permissions"
- User's role does not match required role(s)
- Register user with correct roles: `roles: ["admin"]`

## Next Steps

1. **Add more modules**: Create routes under `app/modules/` for new features (e.g. payroll, attendance).
2. **Add migrations**: Use Alembic for schema versioning
3. **Add tests**: Create test suite in `tests/`
4. **Deploy**: Use Docker + production database

## License

MIT






 .\.venv\Scripts\python.exe scripts\check_users.py


.\.venv\Scripts\python.exe -c "from app.core.database import init_models; init_models(); from app.core.database import SessionLocal; from app.core.models import User; s = SessionLocal(); users = s.query(User).all(); print(f'Total users in DB: {len(users)}'); [print(f'  - {u.username} ({u.email})') for u in users]"



 Email: admin@example.com
  Username: admin
  Password: admin123