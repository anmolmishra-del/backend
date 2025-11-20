
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.shared.schemas import UserCreate, UserOut, Token
from app.shared.services import create_user, authenticate_user
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.core.rbac import require_roles

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user: UserCreate):
    try:
        stored = create_user(user)
        return {"id": stored["id"], "username": stored["username"], "roles": stored.get("roles", []), "email": stored["email"]}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def login(payload: UserCreate):
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(subject=user["username"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "username": user["username"], "roles": user.get("roles", []), "email": user["email"]}


@router.get("/admin-only")
def admin_only(user: dict = Depends(require_roles("admin"))):
    return {"message": "welcome admin", "user": user["username"]}
