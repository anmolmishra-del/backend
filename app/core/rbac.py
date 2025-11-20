from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user


def require_roles(*roles):
    def role_dependency(user: dict = Depends(get_current_user)) -> dict:
        user_roles = set(user.get("roles", []))
        allowed = any(r in user_roles for r in roles)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user

    return role_dependency