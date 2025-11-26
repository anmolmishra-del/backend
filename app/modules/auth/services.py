# from typing import Optional
# from sqlalchemy import select
# from sqlalchemy.orm import Session

# from app.modules.auth.schemas import UserCreate
# from app.modules.auth.schemas import LoginRequest
# from app.modules.auth.models import User


# _memory_users = {}

def create_user(user: UserCreate) -> dict:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            # check exists
            q = select(User).where((User.phone_number == user.phone_number)) 
                                   #and (User.phone_number == user.phone_number))
            
            existing = session.execute(q).scalars().first()
            if existing:
                raise ValueError("User already exists")
            from app.modules.auth.security import get_password_hash

            hashed = get_password_hash(user.password)
            db_user = User(
                email=user.email,
                username=user.username,
                hashed_password=hashed,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number,
                role="user",
                status="active",
                is_email_verified=False,
                roles=user.roles
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            print(f"✓ User {user.email} saved to database")
            return {
                "id": db_user.id,
                "email": db_user.email,
                "username": db_user.username,
                "first_name": db_user.first_name,
                "last_name": db_user.last_name,
                "phone_number": db_user.phone_number,
                "role": db_user.role,
                "status": db_user.status,
                "is_email_verified": db_user.is_email_verified,
                "roles": db_user.roles,
                "created_at": db_user.created_at,
                "updated_at": db_user.updated_at,
                "last_login": db_user.last_login,
                "hashed_password": db_user.hashed_password
            }
        except Exception as db_err:
            session.rollback()
            print(f"⚠ Database error: {db_err}")
            raise
        finally:
            session.close()
    except Exception as e:
        # Fallback to in-memory storage
         raise ValueError("User already exists")
      


# def get_user_by_username(username: str) -> Optional[dict]:
#     try:
#         from app.core.database import SessionLocal
#         session = SessionLocal()
#         try:
#             q = select(User).where(User.username == username)
#             db_user = session.execute(q).scalars().first()
#             if not db_user:
#                 return None
#             return {
#                 "id": db_user.id,
#                 "email": db_user.email,
#                 "username": db_user.username,
#                 "first_name": db_user.first_name,
#                 "last_name": db_user.last_name,
#                 "phone_number": db_user.phone_number,
#                 "role": db_user.role,
#                 "status": db_user.status,
#                 "is_email_verified": db_user.is_email_verified,
#                 "roles": db_user.roles,
#                 "created_at": db_user.created_at,
#                 "updated_at": db_user.updated_at,
#                 "last_login": db_user.last_login,
#                 "hashed_password": db_user.hashed_password
#             }
#         finally:
#             session.close()
#     except Exception:
#         # Fallback to in-memory storage
#         return _memory_users.get(username)


# def authenticate_user(username: str, password: str) -> Optional[dict]:
#     user = get_user_by_username(username)
#     if not user:
#         return None
#     from app.modules.auth.security import verify_password

#     if not verify_password(password, user.get("hashed_password", "")):
#         return None
#     return user


# def get_user_by_phone_number(phone_number: str) -> Optional[dict]:
#     try:
#         from app.core.database import SessionLocal
#         session = SessionLocal()
#         try:
#             q = select(User).where(User.phone_number == phone_number)
#             db_user = session.execute(q).scalars().first()
#             if not db_user:
#                 return None
#             return {
#                 "id": db_user.id,
#                 "email": db_user.email,
#                 "username": db_user.username,
#                 "first_name": db_user.first_name,
#                 "last_name": db_user.last_name,
#                 "phone_number": db_user.phone_number,
#                 "role": db_user.role,
#                 "status": db_user.status,
#                 "is_email_verified": db_user.is_email_verified,
#                 "roles": db_user.roles,
#                 "created_at": db_user.created_at,
#                 "updated_at": db_user.updated_at,
#                 "last_login": db_user.last_login,
#                 "hashed_password": db_user.hashed_password
#             }
#         finally:
#             session.close()
#     except Exception:
#         # Fallback to in-memory storage (search by email)
#         for u in _memory_users.values():
#             if u.get("phone_number") == phone_number:
#                 return u
#         return None


# def authenticate_user_by_phone_number(phone_number: str, password: str) -> Optional[dict]:
#     user = get_user_by_phone_number(phone_number)
#     if not user:
#         return None
#     from app.modules.auth.security import verify_password

#     if not verify_password(password, user.get("hashed_password", "")):
#         return None
#     return user



from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import select

from app.modules.auth.models import User

# in-memory fallback stores (for development/testing)
_memory_users = {}
_otp_store = {}  # phone -> {"code": str, "expires_at": datetime}

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



# def create_user(user: UserCreate) -> dict:
#     try:
#         from app.core.database import SessionLocal
#         session = SessionLocal()
#         try:
#             # check exists by email or phone (avoid duplicates)
#             q = select(User).where((User.email == user.email) | (User.phone_number == user.phone_number))
#             existing = session.execute(q).scalars().first()
#             if existing:
#                 raise ValueError("User already exists")

#             from app.modules.auth.security import get_password_hash
#             hashed = get_password_hash(user.password)

#             db_user = User(
#                 email=user.email,
#                 username=user.username,
#                 hashed_password=hashed,
#                 first_name=user.first_name,
#                 last_name=user.last_name,
#                 phone_number=user.phone_number,
#                 role="user",
#                 status="active",
#                 is_email_verified=False,
#                 is_phone_verified=False,
#                 roles=user.roles or []
#             )
#             session.add(db_user)
#             session.commit()
#             session.refresh(db_user)
#             print(f"✓ User {user.email} saved to database")
#             return _user_to_dict(db_user)
#         except Exception as db_err:
#             session.rollback()
#             print(f"⚠ Database error: {db_err}")
#             raise
#         finally:
#             session.close()
#     except Exception as e:
#         # fallback to in-memory
#         if user.username in _memory_users:
#             raise ValueError("User already exists")
#         from app.modules.auth.security import get_password_hash
#         hashed = get_password_hash(user.password)
#         u = {
#             "id": len(_memory_users) + 1,
#             "email": user.email,
#             "username": user.username,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "phone_number": user.phone_number,
#             "role": "user",
#             "status": "active",
#             "is_email_verified": False,
#             "is_phone_verified": False,
#             "roles": user.roles or [],
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow(),
#             "last_login": None,
#             "hashed_password": hashed,
#         }
#         _memory_users[user.username] = u
#         return u

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
# Password authentication (unchanged)
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
    from app.modules.auth.security import verify_password
    # if not verify_password(password, user.get("hashed_password", "")):
    #     return None
    return user


# file: app/modules/auth/otp.py
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from random import randint

# In-memory OTP store: phone(int) -> {code(int), expires_at(datetime)}
_otp_store: Dict[int, Dict[str, Any]] = {}


def generate_otp(length: int = 6) -> int:
    """Generate a numeric OTP as an integer."""
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return randint(start, end)


def _send_via_twilio(phone: int, message: str):
    """Send SMS using Twilio."""
    from twilio.rest import Client
    
  

    if not (account_sid and auth_token and from_number):
        raise RuntimeError("Twilio credentials not configured")

    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_=from_number,
        to=str(phone)  # Twilio requires string, phone remains int internally
    )


def send_otp(phone_number: str, expire_minutes: int = 5) -> bool:
    """
    Generate OTP (int), send SMS, and store in memory.
    """
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)

    message = f"Your OTP is {code}. Valid for {expire_minutes} minutes."

    try:
        # send SMS (convert to string only for sending)
        _send_via_twilio(phone_number, message)

     
        _otp_store[phone_number] = {
            "code": str(code),
            "expires_at": expires_at
        }

        return True

    except Exception as err:
        print("SMS send failed:", err)

        # still store OTP for testing/fallback
        _otp_store[phone_number] = {
            "code": code,
            "expires_at": expires_at
        }

        return True

def verify_otp(phone_number: str, otp_code: str) -> bool:
    entry = _otp_store.get(phone_number)
    if not entry:
        return False

    # expired
    if datetime.utcnow() > entry["expires_at"]:
        _otp_store.pop(phone_number, None)
        return False

    # compare as strings
    if str(entry["code"]) == str(otp_code):
        _otp_store.pop(phone_number, None)
        return True

    return False

def authenticate_user_by_phone_otp(phone_number: str, otp: str  ) -> Optional[dict]:
    ok = verify_otp(phone_number, otp)
    if not ok:
        return None
    return get_user_by_phone_number(phone_number)
