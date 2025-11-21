from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.shared.schemas import UserOut
from app.core.security import get_current_user
from app.core.rbac import require_roles
from app.core.models import User
from app.core.database import SessionLocal
from sqlalchemy import select

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_user(user: dict = Depends(require_roles("admin"))):
    """Dependency to ensure user is admin."""
    return user


@router.get("/users", response_model=List[UserOut])
def list_all_users(admin: dict = Depends(get_admin_user)):
    """List all users (admin only)."""
    try:
        session = SessionLocal()
        try:
            users = session.query(User).all()
            return [
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.username,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "phone_number": u.phone_number,
                    "role": u.role,
                    "status": u.status,
                    "is_email_verified": u.is_email_verified,
                    "roles": u.roles,
                    "created_at": u.created_at,
                    "updated_at": u.updated_at,
                    "last_login": u.last_login,
                }
                for u in users
            ]
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, admin: dict = Depends(get_admin_user)):
    """Get a specific user by ID (admin only)."""
    try:
        session = SessionLocal()
        try:
            q = select(User).where(User.id == user_id)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
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
            }
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/users/{user_id}")
def update_user(user_id: int, updates: dict, admin: dict = Depends(get_admin_user)):
    """Update user fields (admin only)."""
    try:
        session = SessionLocal()
        try:
            q = select(User).where(User.id == user_id)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            # Update allowed fields
            for key, value in updates.items():
                if key in ["first_name", "last_name", "phone_number", "role", "status", "is_email_verified"]:
                    setattr(db_user, key, value)
            
            session.commit()
            session.refresh(db_user)
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
            }
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: dict = Depends(get_admin_user)):
    """Delete a user (admin only)."""
    try:
        session = SessionLocal()
        try:
            q = select(User).where(User.id == user_id)
            db_user = session.execute(q).scalars().first()
            if not db_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            session.delete(db_user)
            session.commit()
            return {"message": "User deleted successfully", "user_id": user_id}
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
