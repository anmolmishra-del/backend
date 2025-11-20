from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.shared.schemas import UserCreate
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
            db_user = User(username=user.username, hashed_password=hashed, roles=user.roles, email=user.email)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return {"id": db_user.id, "username": db_user.username, "hashed_password": db_user.hashed_password, "roles": db_user.roles, "email": db_user.email}
        finally:
            session.close()
    except Exception as e:
        # Fallback to in-memory storage
        if user.username in _memory_users:
            raise ValueError("User already exists")
        from app.core.security import get_password_hash
        hashed = get_password_hash(user.password)
        uid = len(_memory_users) + 1
        _memory_users[user.username] = {
            "id": uid,
            "username": user.username,

            "hashed_password": hashed,
            "roles": user.roles,
            "email": user.email
        }
        return _memory_users[user.username]


def get_user_by_username(username: str) -> Optional[dict]:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(User).where(User.username == username)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                return None
            return {"id": db_user.id, "username": db_user.username, "hashed_password": db_user.hashed_password, "roles": db_user.roles, "email": db_user.email}
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