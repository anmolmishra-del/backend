
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.admin.routes import get_user_by_id
from app.shared.schemas import UserCreate, UserOut, Token, LoginRequest
from app.shared.services import create_user, authenticate_user_by_email
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.core.rbac import require_roles

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user: UserCreate):
    try:
        stored = create_user(user)
        return stored
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



@router.get("/users/{user_id}", )
def getUserById(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The system does not recognize your account!.Please create new account")
    # access_token = create_access_token(subject=user["username"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
    user = authenticate_user_by_email(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The system does not recognize your account!.Please create new account")
    access_token = create_access_token(subject=user["username"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return user


@router.get("/admin-only")
def admin_only(user: dict = Depends(require_roles("admin"))):
    return {"message": "welcome admin", "user": user["username"]}
