
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

# avoid module-level import to prevent circular imports
from app.modules.locations.schemas import  LocationCreate
from app.modules.locations.services import create_location
from app.modules.auth.security import  get_current_user
from app.core.rbac import require_roles
from fastapi.security import OAuth2PasswordBearer
router = APIRouter(prefix="/place", tags=["place"])


@router.post("/locations")
def log_location(location: LocationCreate, user: dict = Depends(get_current_user)):
    # create_location(location, user)
    try:
        from app.core.database import SessionLocal
        from app.modules.locations.models import Loaction
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