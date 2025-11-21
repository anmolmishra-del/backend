from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.shared.schemas import UserCreate
from app.shared.schemas import LoginRequest
from app.core.models import User


_memory_users = {}

def create_user(user: UserCreate) -> dict:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            # check exists
            q = select(User).where(User.email == user.email)
            
            existing = session.execute(q).scalars().first()
            if existing:
                raise ValueError("User already exists")
            from app.core.security import get_password_hash

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
        # print(f"⚠ Using in-memory storage: {e}")
        # if user.email in _memory_users:
        #     raise ValueError("User already exists")
        # from app.core.security import get_password_hash
        # hashed = get_password_hash(user.password)
        # from datetime import datetime
        # uid = len(_memory_users) + 1
        # now = datetime.utcnow()

        # _memory_users[user.email] = {
        #     "id": uid,
        #     "email": user.email,
        #     "username": user.username,
        #     "first_name": user.first_name,
        #     "last_name": user.last_name,
        #     "phone_number": user.phone_number,
        #     "role": "user",
        #     "status": "active",
        #     "is_email_verified": False,
        #     "roles": user.roles,
        #     "created_at": now,
        #     "updated_at": now,
        #     "last_login": None,
        #     "hashed_password": hashed
        # }
        # return _memory_users[user.email]


def get_user_by_username(username: str) -> Optional[dict]:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(User).where(User.username == username)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                return None
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
        finally:
            session.close()
    except Exception:
        # Fallback to in-memory storage
        return _memory_users.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    from app.core.security import verify_password

    if not verify_password(password, user.get("hashed_password", "")):
        return None
    return user


def get_user_by_email(email: str) -> Optional[dict]:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(User).where(User.email == email)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                return None
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
        finally:
            session.close()
    except Exception:
        # Fallback to in-memory storage (search by email)
        for u in _memory_users.values():
            if u.get("email") == email:
                return u
        return None




def get_user_by_id(user_id: int) -> Optional[dict]:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(User).where(User.id == user_id)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                return None
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
        finally:
            session.close()
    except Exception:
        # Fallback to in-memory storage (search by email)
        for u in _memory_users.values():
            if u.get("email") == email:
                return u
        return None



def authenticate_user_by_email(email: str, password: str) -> Optional[dict]:
    user = get_user_by_email(email)
    if not user:
        return None
    from app.core.security import verify_password

    if not verify_password(password, user.get("hashed_password", "")):
        return None
    return user