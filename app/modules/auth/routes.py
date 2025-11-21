from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

# avoid module-level import to prevent circular imports
from app.shared.schemas import LocationCreate, UserCreate, UserOut, Token, LoginRequest
from app.shared.services import create_user, authenticate_user_by_email, create_location
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.core.rbac import require_roles
from fastapi.security import OAuth2PasswordBearer

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



@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
    user = authenticate_user_by_email(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The system does not recognize your account!.Please create new account")
    access_token = create_access_token(subject=user["username"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(token: str = Depends(oauth2_scheme)):
    return {"token_return": token}


@router.get("/admin-only")
def admin_only(user: dict = Depends(require_roles("admin"))):
    return {"message": "welcome admin", "user": user["username"]}


@router.post("/locations")
def log_location(location: LocationCreate, user: dict = Depends(get_current_user)):
    # create_location(location, user)
    try:
        from app.core.database import SessionLocal
        from app.core.models import Loaction
        session = SessionLocal()
        try:
            # coerce to float to avoid DB type mismatches (clients may send strings)
            try:
                lat = float(location.latitude)
                lon = float(location.longitude)
            except Exception:
                raise ValueError("latitude and longitude must be numeric")

            uid = location.user_id if getattr(location, 'user_id', None) is not None else user["id"]

            db_location = Loaction(
                user_id=uid,
                latitude=lat,
                longitude=lon,
            )
            session.add(db_location)
            session.commit()
            session.refresh(db_location)
            print(f"✓ Location for user {user['id']} saved to database")
            return {
                "id": db_location.id,
                "user_id": db_location.user_id,
                "latitude": db_location.latitude,
                "longitude": db_location.longitude,
                "timestamp": db_location.timestamp,
            }
        except Exception as db_err:
            session.rollback()
            print(f"⚠ Database error: {db_err}")
            raise
        finally:
            session.close()
    except Exception as e:
        print(f"⚠ Could not save location: {e}")
        raise


@router.get("/locations")
def get_locations(user: dict = Depends(get_current_user)):
    from app.core.database import SessionLocal
    from app.core.models import Loaction
    session = SessionLocal()
    try:
        q = session.query(Loaction).filter(Loaction.user_id == user["id"])
        locations = q.all()
        result = []
        for loc in locations:
            result.append({
                "id": loc.id,
                "user_id": loc.user_id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "timestamp": loc.timestamp,
            })
        return result
    except Exception as e:
        print(f"⚠ Error fetching locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not fetch locations")
    finally:
        session.close()

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

# avoid module-level import to prevent circular imports
from app.shared.schemas import  LocationCreate, UserCreate, UserOut, Token, LoginRequest
from app.shared.services import create_user, authenticate_user_by_email, create_location
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.core.rbac import require_roles
from fastapi.security import OAuth2PasswordBearer
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


@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
    user = authenticate_user_by_email(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The system does not recognize your account!.Please create new account")
    access_token = create_access_token(subject=user["username"], expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(token: str = Depends(oauth2_scheme)):
    return {"token_return":token} 


@router.get("/admin-only")
def admin_only(user: dict = Depends(require_roles("admin"))):
    return {"message": "welcome admin", "user": user["username"]}


@router.post("/locations")
def log_location(location: LocationCreate, user: dict = Depends(get_current_user)):
    # create_location(location, user)
    try:
        from app.core.database import SessionLocal
        from app.core.models import Loaction
        session = SessionLocal()
        try:
            # coerce to float to avoid DB type mismatches (clients may send strings)
            try:
                lat = float(location.latitude)
                lon = float(location.longitude)
            except Exception:
                raise ValueError("latitude and longitude must be numeric")

            db_location = Loaction(
                user_id=user['id'],
                latitude=lat,
                longitude=lon
            )
            session.add(db_location)
            session.commit()
            session.refresh(db_location)
            print(f"✓ Location for user {user['id']} saved to database")
            return {
                "id": db_location.id,
                "user_id": db_location.user_id,
                "latitude": db_location.latitude,
                "longitude": db_location.longitude,
                "timestamp": db_location.timestamp 
            }
        except Exception as db_err:
            session.rollback()
            print(f"⚠ Database error: {db_err}")
            raise
        finally:
            session.close()
    except Exception as e:
        print(f"⚠ Could not save location: {e}")
        raise

@router.get("/locations")
def get_locations(user: dict = Depends(get_current_user)):
    from app.core.database import SessionLocal
    from app.core.models import Loaction
    session = SessionLocal()
    try:
        q = session.query(Loaction).filter(Loaction.user_id == user["id"])
        locations = q.all()
        result = []
        for loc in locations:
            result.append({
                "id": loc.id,
                "user_id": loc.user_id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "timestamp": loc.timestamp
            })
        return result
    except Exception as e:
        print(f"⚠ Error fetching locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not fetch locations")
    finally:
        session.close()