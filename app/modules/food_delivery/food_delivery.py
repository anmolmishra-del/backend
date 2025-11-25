from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.auth.security import get_current_user

from app.core.database import SessionLocal
from app.modules.food_delivery.model import Restaurant, RestaurantLocation
from app.modules.food_delivery.schemas import CreateResturant


router = APIRouter(prefix="/food_delivery", tags=["food_delivery"])


@router.post("/restaurants")
def create_restaurant(payload: CreateResturant,
                       #user: dict = Depends(get_current_user)
                       ):

    session = SessionLocal()
    try:
     
        phone = str(payload.phone_number) if getattr(payload, "phone_number", None) is not None else None

     
        try:
            lat = float(payload.latitude)
            lon = float(payload.longitude)
        except Exception:
            raise HTTPException(status_code=400, detail="latitude and longitude must be numeric")

     
        db_rest = Restaurant(
            name=payload.name,
            description=getattr(payload, "description", None),
            owner_id=payload.owner_id,
            cuisine_type=getattr(payload, "cuisine_type", None),
            phone_number=phone,
            email=getattr(payload, "email", None),
            logo_url=getattr(payload, "logo_url", None),
            banner_url=getattr(payload, "banner_url", None),
            status=payload.status or "open",
            is_favorite=bool(getattr(payload, "is_favorite", False)),
        )

        session.add(db_rest)
        # flush so db_rest.id becomes available without committing yet
        session.flush()

        # Create restaurant location linked to the created restaurant
        loc = RestaurantLocation(
            restaurant_id=db_rest.id,
            latitude=lat,
            longitude=lon,
            address=getattr(payload, "address", None),
        )
        session.add(loc)

        # commit both records together
        session.commit()

        # refresh to get DB-populated fields
        session.refresh(db_rest)

        return {"id": db_rest.id, "name": db_rest.name}

    except HTTPException:
      
        try:
            session.rollback()
        except Exception:
            pass
        raise
    except Exception as exc:
       
        try:
            session.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to create restaurant: {exc}")
    finally:
        session.close()
