from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.auth.security import get_current_user

from app.core.database import SessionLocal
from app.modules.food_delivery.model import MenuCategory, Restaurant, RestaurantLocation
from app.modules.food_delivery.schemas import CreateResturant, MenuCategory, ResturantLocation, ResturantLocation


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


@router.post("/restaurants/location")
def add_restaurant_location(restaurant_id: int, payload: ResturantLocation):
    session = SessionLocal()
    try:
        # Validate restaurant exists
        rest = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not rest:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        location = RestaurantLocation(
            restaurant_id=restaurant_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            address=payload.address,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            postal_code=payload.postal_code,
            location_id=payload.location_id,
            dining_type=payload.dining_type
        )

        session.add(location)
        session.commit()

        return {"message": "Location added successfully"}

    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()
@router.post("/menu/category")
def create_menu_category(payload: MenuCategory):
    session = SessionLocal()
    try:
        category = MenuCategory(
            restaurant_id=payload.resturant_id,
            name=payload.name,
            description=payload.description
        )

        session.add(category)
        session.commit()
        session.refresh(category)

        return {"category_id": category.id, "message": "Category added"}

    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()

# @router.post("/menu/item")
# def create_menu_item(payload: MenuItem):
#     session = SessionLocal()
#     try:
#         item = MenuItem(
#             category_id=payload.category_id,
#             name=payload.name,
#             description=payload.description,
#             price=payload.price,
#             is_available=payload.is_available,
#             image_url=payload.image_url,
#             is_vegetarian=payload.is_vegetarian,
#             cooking_time_minutes=payload.cooking_time_minutes
#         )

#         session.add(item)
#         session.commit()
#         session.refresh(item)

#         return {"item_id": item.id, "message": "Menu item created"}

#     except Exception as exc:
#         session.rollback()
#         raise HTTPException(status_code=500, detail=str(exc))
#     finally:
#         session.close()
