# Backend API - JWT Auth & RBAC System

A FastAPI-based backend with JWT authentication, role-based access control (RBAC), and PostgreSQL integration.

## Architecture

```
API Gateway → Auth → RBAC → Services
    ↓
[Users | Hotel | Food | Travel | Inventory | Payments ...]
    ↓
[PostgreSQL Database]
```

## Features

- ✅ **JWT Authentication**: Secure token-based auth with bcrypt password hashing
- ✅ **Role-Based Access Control (RBAC)**: Protect routes with role checks
- ✅ **PostgreSQL Integration**: Async-ready with SQLAlchemy ORM
- ✅ **Scalable Architecture**: Modular design with separate auth, hotel, food, travel modules

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
- `DATABASE_URL`: `postgresql+psycopg://postgres:postgres@localhost:5432/backend_db`
- `SECRET_KEY`: `dev-secret`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`

### Run the Server

```bash
# Development (with auto-reload)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Production
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

The server starts on `http://127.0.0.1:8000`.

## API Usage

### 1. Register a User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "username": "alice",
  "password": "secret123",
  "roles": ["user"]
}
```

**Response:**
```json
{
  "id": 1,
  "username": "alice",
  "roles": ["user"]
}
```

### 2. Login

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "username": "alice",
  "password": "secret123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Current User (Protected)

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "alice",
  "roles": ["user"]
}
```

### 4. Admin-Only Endpoint (Role-Protected)

**Endpoint:** `GET /auth/admin-only`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success (user has "admin" role):**
```json
{
  "message": "welcome admin",
  "user": "alice"
}
```

**Error (user lacks "admin" role):**
```json
{
  "detail": "Not enough permissions"
}
```

## Protecting Routes with RBAC

### Example: Protect a route with a specific role

In your route file (e.g., `app/modules/hotel/routes.py`):

```python
from fastapi import APIRouter, Depends
from app.core.rbac import require_roles

router = APIRouter(prefix="/hotel", tags=["hotel"])

@router.post("/rooms")
def create_room(room_data: dict, user: dict = Depends(require_roles("hotel_admin"))):
    """Only users with 'hotel_admin' role can create rooms"""
    return {"message": f"Room created by {user['username']}"}

@router.get("/rooms")
def list_rooms(user: dict = Depends(require_roles("user", "hotel_admin"))):
    """Users with either 'user' or 'hotel_admin' role can list rooms"""
    return {"rooms": [...]}
```

### Register the router in main.py

```python
from app.modules.hotel import router as hotel_router

app.include_router(hotel_router)
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

### 5. Services (`app/shared/services.py`)

- `create_user(user: UserCreate)` — Create new user
- `get_user_by_username(username)` — Fetch user
- `authenticate_user(username, password)` — Validate credentials

## Example Flow

1. **User registers:**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"bob","password":"pass123","roles":["admin"]}'
   ```

2. **User logs in:**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"bob","password":"pass123"}'
   ```
   → Receive `access_token`

3. **User accesses protected route:**
   ```bash
   curl -X GET http://localhost:8000/auth/admin-only \
     -H "Authorization: Bearer <access_token>"
   ```
   → Returns `welcome admin`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── core/
│   │   ├── config.py           # Config (DB URL, SECRET_KEY)
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   ├── models.py           # ORM models (User)
│   │   ├── security.py         # JWT & password utilities
│   │   ├── rbac.py             # Role-based access control
│   │   └── __init__.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── routes.py       # Auth endpoints
│   │   │   └── __init__.py
│   │   ├── hotel/
│   │   ├── food/
│   │   ├── travel/
│   │   └── payment/
│   └── shared/
│       ├── schemas.py          # Pydantic models (UserCreate, Token)
│       ├── services.py         # DB service functions
│       └── __init__.py
├── requirements.txt            # Dependencies
├── .env                        # Environment variables (not in git)
└── README.md                   # This file
```

## Database Initialization

Tables are created automatically on app startup via `init_models()` in `app/main.py`. For production, use Alembic for migrations.

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

1. **Add more modules**: Create routes in `app/modules/hotel/`, `app/modules/food/`, etc.
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