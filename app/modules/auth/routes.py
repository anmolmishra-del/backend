
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

# avoid module-level import to prevent circular imports
from app.modules.auth.schemas import   OTPRequest, OTPSender, UserCreate, UserOut, Token, LoginRequest, loginOut
from app.modules.auth.services import authenticate_user_by_phone_number, authenticate_user_by_phone_number, create_user
from app.modules.auth.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.core.rbac import require_roles
from fastapi.security import OAuth2PasswordBearer

from app.modules.locations.models import Loaction
router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserOut)
def register(user: UserCreate):
    try:
        stored = create_user(user)
        return stored
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



@router.get("/users/{user_id}", )
def getUserById(user_id: int):
    # import inside the function to avoid circular import at module import time
    from app.modules.admin.routes import get_user_by_id

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The system does not recognize your account!.Please create new account")
    # access_token = create_access_token(subject=user["username"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return user


# @router.post("/login", response_model=loginOut)
# def login(payload: LoginRequest):
#     from app.core.database import SessionLocal 
#     db = SessionLocal()
#     user = authenticate_user_by_phone_number(payload.phone_number)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The system does not recognize your account!.Please create new account")
#     access_token = create_access_token(subject=user["email"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#    # location = db.query(Loaction).filter(Loaction.user_id == user['id']).first()  or []

#     re = {"access_token": access_token, "token_type": "bearer", "user":user,
#         #  "location":location
#           }

#     return re


@router.get("/me", response_model=UserOut)
def me(token: str = Depends(oauth2_scheme)):
    return {"token_return":token} 


@router.get("/admin-only")
def admin_only(user: dict = Depends(require_roles("admin"))):
    return {"message": "welcome admin", "user": user["username"]}


from fastapi import APIRouter, HTTPException
from app.modules.auth.services import send_otp, verify_otp, get_user_by_phone_number



@router.post("/send-otp")
def api_send_otp(body: OTPSender):
    ok = send_otp(body.phone_number)
    if not ok:
        raise HTTPException(400, "Could not send OTP")
    return {"ok": True, "message": "OTP sent"}

@router.post("/verify-otp")
def api_verify_otp(body: OTPRequest):
    user = get_user_by_phone_number(body.phone_number)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The system does not recognize your account!.Please create new account")
    ok = verify_otp(body.phone_number, body.otp)
    if not ok:
        raise HTTPException(400, "Invalid or expired OTP")
    
  
    access_token = create_access_token(subject=user["phone_number"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
   # location = db.query(Loaction).filter(Loaction.user_id == user['id']).first()  or []

    re = {"access_token": access_token, "token_type": "bearer", "user":user,
        #  "location":location
          }
    return {"ok": True, "user": re}
