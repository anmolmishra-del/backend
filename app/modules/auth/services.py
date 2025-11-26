# app/modules/auth/services.py
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from random import randint

from sqlalchemy import select, true

# Import User model at module level (models are safe)
from app.modules.auth.models import User

# in-memory fallback stores (for development/testing)
_memory_users: Dict[str, Dict[str, Any]] = {}
_otp_store: Dict[str, Dict[str, Any]] = {}  # phone -> {"code": str, "expires_at": datetime}


# --------------------------
# Helper: build user dict
# --------------------------
def _user_to_dict(db_user) -> dict:
    return {
        "id": getattr(db_user, "id", None),
        "email": getattr(db_user, "email", None),
        "username": getattr(db_user, "username", None),
        "first_name": getattr(db_user, "first_name", None),
        "last_name": getattr(db_user, "last_name", None),
        "phone_number": getattr(db_user, "phone_number", None),
        "role": getattr(db_user, "role", None),
        "status": getattr(db_user, "status", None),
        "is_email_verified": getattr(db_user, "is_email_verified", False),
        "is_phone_verified": getattr(db_user, "is_phone_verified", False),
        "roles": getattr(db_user, "roles", None),
        "created_at": getattr(db_user, "created_at", None),
        "updated_at": getattr(db_user, "updated_at", None),
        "last_login": getattr(db_user, "last_login", None),
        "hashed_password": getattr(db_user, "hashed_password", None),
    }




def create_user(user) -> dict:
  
 
    try:
        from app.modules.auth.schemas import UserCreate  # type: ignore
    except Exception:
        UserCreate = None  

   
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
         
            q = select(User).where((User.email == getattr(user, "email", None)) or (User.phone_number == getattr(user, "phone_number", None)))
            existing = session.execute(q).scalars().first()
            if existing:
                raise ValueError("User already exists")

            # local import for password hashing (safe)
            from app.modules.auth.security import get_password_hash

            hashed = get_password_hash(getattr(user, "password", None) or "")

            db_user = User(
                email=getattr(user, "email", None),
                username=getattr(user, "username", None),
                hashed_password=hashed,
                first_name=getattr(user, "first_name", None),
                last_name=getattr(user, "last_name", None),
                phone_number=getattr(user, "phone_number", None),
                role="user",
                status="active",
                is_email_verified=False,
                # is_phone_verified=True,
                roles=getattr(user, "roles", []) or []
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return _user_to_dict(db_user)
        except Exception as db_err:
            session.rollback()
            # Re-raise so caller (router) can decide response code
            raise db_err
        finally:
            session.close()
    except Exception as e:
        # fallback to in-memory store for dev/testing
        username = getattr(user, "username", None) or getattr(user, "email", None)
        if not username:
            raise ValueError("Invalid user payload")

        if username in _memory_users:
            raise ValueError("User already exists")

        # local import for password hashing (safe)
        from app.modules.auth.security import get_password_hash

        hashed = get_password_hash(getattr(user, "password", None) or "")
        u = {
            "id": len(_memory_users) + 1,
            "email": getattr(user, "email", None),
            "username": username,
            "first_name": getattr(user, "first_name", None),
            "last_name": getattr(user, "last_name", None),
            "phone_number": getattr(user, "phone_number", None),
            "role": "user",
            "status": "active",
            "is_email_verified": False,
            "is_phone_verified": False,
            "roles": getattr(user, "roles", []) or [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "hashed_password": hashed,
        }
        _memory_users[username] = u
        return u


# --------------------------
# Get user by username
# --------------------------
def get_user_by_username(username: str) -> Optional[dict]:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(User).where(User.username == username)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                return None
            return _user_to_dict(db_user)
        finally:
            session.close()
    except Exception:
        return _memory_users.get(username)


# --------------------------
# Get user by phone number
# --------------------------
def get_user_by_phone_number(phone_number: str) -> Optional[dict]:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(User).where(User.phone_number == phone_number)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                return None
            return _user_to_dict(db_user)
        finally:
            session.close()
    except Exception:
        for u in _memory_users.values():
            if u.get("phone_number") == phone_number:
                return u
        return None


# --------------------------
# Password authentication
# --------------------------
def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    from app.modules.auth.security import verify_password
    if not verify_password(password, user.get("hashed_password", "")):
        return None
    return user


def authenticate_user_by_phone_number(phone_number: str) -> Optional[dict]:
    user = get_user_by_phone_number(phone_number)
    if not user:
        return None
    # Note: this function previously attempted password verification but no password provided;
    # keep as a simple fetch helper
    return user


# --------------------------
# OTP helpers (in same file)
# --------------------------
def _generate_otp(length: int = 6) -> int:
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return randint(start, end)


def _send_via_twilio(phone: str, message: str):
    """Send SMS using Twilio. Local import to avoid extra top-level deps."""
    try:
        from twilio.rest import Client
    except Exception as e:
        raise RuntimeError("twilio package not available") from e

  
    if not (account_sid and auth_token and from_number):
        raise RuntimeError("Twilio credentials not configured")

    client = Client(account_sid, auth_token)
    client.messages.create(body=message, from_=from_number, to=str(phone))


def send_otp(phone_number: str, expire_minutes: int = 5) -> bool:
    code = _generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
    message = f"Your OTP is {code}. Valid for {expire_minutes} minutes."

    try:
        _send_via_twilio(phone_number, message)
        _otp_store[phone_number] = {"code": str(code), "expires_at": expires_at}
        return True
    except Exception as err:
        # log and still store OTP for dev/testing
        print("SMS send failed:", err)
        _otp_store[phone_number] = {"code": str(code), "expires_at": expires_at}
        return True


def verify_otp(phone_number: str, otp_code: str) -> bool:
    entry = _otp_store.get(phone_number)
    if not entry:
        return False
    if datetime.utcnow() > entry["expires_at"]:
        _otp_store.pop(phone_number, None)
        return False
    if str(entry["code"]) == str(otp_code):
        _otp_store.pop(phone_number, None)
        return True
    return False


def authenticate_user_by_phone_otp(phone_number: str, otp: str) -> Optional[dict]:
    ok = verify_otp(phone_number, otp)
    if not ok:
        return None
    return get_user_by_phone_number(phone_number)
