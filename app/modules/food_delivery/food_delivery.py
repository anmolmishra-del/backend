from fastapi import APIRouter, Depends, HTTPException, status
from requests import Session
from sqlalchemy import insert
from app.modules.auth.security import get_current_user

from app.core.database import SessionLocal
from app.modules.food_delivery.model import  Restaurant, RestaurantLocation
from app.modules.food_delivery.schemas import CreateRestaurant, FoodOrderCreate, format_address 

from app.modules.food_delivery import model as m
from app.modules.food_delivery import schemas as s
from app.modules.order_address_list.models import Address
router = APIRouter(prefix="/food_delivery", tags=["food_delivery"])


@router.post("/restaurants")
def create_restaurant(payload: CreateRestaurant,
                       #user: dict = Depends(get_current_user)
                       ):

    session = SessionLocal()
    try:
     
        phone = str(payload.phone_number) if getattr(payload, "phone_number", None) is not None else None

     
        # try:
        #     lat = float(payload.latitude)
        #     lon = float(payload.longitude)
        # except Exception:
        #     raise HTTPException(status_code=400, detail="latitude and longitude must be numeric")

     
        db_rest = Restaurant(
            name=payload.name,
            
            cuisine_type=getattr(payload, "cuisine_type", None),
            phone_number=phone,
            email=getattr(payload, "email", None),
            logo_url=getattr(payload, "logo_url", None),
            banner_url=getattr(payload, "banner_url", None),
            status=payload.status or "open",
            is_favorite=bool(getattr(payload, "is_favorite", False)),
        )


        session.add(db_rest)
       
        session.flush()
        # many-to-many: associate categories
        from app.modules.food_delivery.model import restaurant_category
        rest_categories = (
            insert(restaurant_category).values([
                {"restaurant_id": db_rest.id, "category_id": cat_id}
                for cat_id in (payload.categories_id or [])
            ])
        )
        session.execute(rest_categories)

       
        loc = RestaurantLocation(
            restaurant_id=db_rest.id,
            latitude=payload.location.latitude,
            longitude=payload.location.longitude,
            address=payload.location.address,
            city=payload.location.city,
            state=payload.location.state,
            country=payload.location.country,
            postal_code=payload.location.postal_code,
            location_id=payload.location.location_id,
            dining_type=payload.location.dining_type
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



@router.post("/menu/category")
def create_menu_category(payload: s.MenuCategoryCreate):
    session: Session = SessionLocal()
    try:
       
        # restaurant = session.query(m.Restaurant).filter(m.Restaurant.id == payload.restaurant_id).first()
        # if not restaurant:
        #     raise HTTPException(status_code=404, detail="Restaurant not found")

       
        category = m.MenuCategory(
          #  restaurant_id=payload.restaurant_id,
            name=payload.name,
            description=payload.description
        )

        session.add(category)
        session.commit()
        session.refresh(category)

        return {"category_id": category.id, "message": "Category added"}

    except HTTPException:
        # re-raise fastapi HTTP exceptions
        session.rollback()
        raise
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()

@router.post("/menu/item")
def create_menu_item(payload: s.MenuItemCreate):
    session = SessionLocal()
    
    try:
        restaurant = session.query(m.Restaurant).filter(m.Restaurant.id == payload.restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        # category = session.query(m.MenuCategory).filter(m.MenuCategory.id == payload.category_id,
        #                                                m.MenuCategory.restaurant_id == payload.restaurant_id).first()
        item = m. MenuItem(
            category_id=payload.category_id,
            restaurant_id=payload.restaurant_id,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            is_available=payload.is_available,
            image_url=payload.image_url,
            is_vegetarian=payload.is_vegetarian,
            cooking_time_minutes=payload.cooking_time_minutes
        )

        session.add(item)
        session.commit()
        session.refresh(item)

        return {"item_id": item.id, "message": "Menu item created"}

    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()

@router.get("/restaurants_data/{restaurant_id}")
def get_restaurant(restaurant_id: int):
    session = SessionLocal()
    try:
        restaurant = session.query(m.Restaurant).filter(m.Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        res = {
            "id": restaurant.id,
            "name": restaurant.name,
            "cuisine_type": restaurant.cuisine_type,
            "phone_number": restaurant.phone_number,
            "email": restaurant.email,
            "logo_url": restaurant.logo_url,
            "banner_url": restaurant.banner_url,
            "status": restaurant.status,
            "is_favorite": restaurant.is_favorite,
            "created_at": restaurant.created_at,
            "locations": [],
            "categories": [],
        }
        for loc in restaurant.locations:
             res["locations"].append({
                "id": loc.id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "address": loc.address,
                "city": loc.city,
                "state": loc.state,
                "country": loc.country,
                "postal_code": loc.postal_code,
                "location_id": loc.location_id,
                "dining_type": loc.dining_type,
                "created_at": loc.created_at
            })
        for cat in restaurant.categories:
            cat_data = {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "created_at": cat.created_at,
                "items": []
            }
            for item in cat.items:
                cat_data["items"].append({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "price": item.price,
                    "is_available": item.is_available,
                    "image_url": item.image_url,
                    "is_vegetarian": item.is_vegetarian,
                    "cooking_time_minutes": item.cooking_time_minutes,
                    "created_at": item.created_at
                })  
            res["categories"].append(cat_data)

        return res

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()

@router.get("/all_restaurants")
def get_all_restaurants():
    session = SessionLocal()
    try:
        restaurants = session.query(m.Restaurant).all()
        res_list = []
        for restaurant in restaurants:
            res_list.append({
                "id": restaurant.id,
                "name": restaurant.name,
                "cuisine_type": restaurant.cuisine_type,
                "phone_number": restaurant.phone_number,
                "email": restaurant.email,
                "logo_url": restaurant.logo_url,
                "banner_url": restaurant.banner_url,
                "status": restaurant.status,
                "is_favorite": restaurant.is_favorite,
                "created_at": restaurant.created_at
            })
        return res_list

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()    


router.get("/all_items")  
def get_all_menu_items():
    session = SessionLocal()
    try:
        items = session.query(m.MenuItem).all()
        item_list = []
        for item in items:
            item_list.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "is_available": item.is_available,
                "image_url": item.image_url,
                "is_vegetarian": item.is_vegetarian,
                "cooking_time_minutes": item.cooking_time_minutes,
                "created_at": item.created_at
            })
        return item_list

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()

@router.post("/food_order")
def create_food_order(payload: FoodOrderCreate) -> dict:
    """
    payload: FoodOrderCreate
    SessionLocal: SQLAlchemy session factory (callable)
    m: module containing ORM models (MenuItem, FoodOrder, FoodOrderItem, Restaurant)
    """
    # collect menu item ids
    menu_item_ids = [it.menu_item_id for it in payload.items]
    if not menu_item_ids:
        raise HTTPException(status_code=400, detail="No order items provided")

    # Use session context manager if available
    with SessionLocal() as session:  # assumes SessionLocal() returns a context-manageable Session
        try:
            # validate that all menu items belong to the same restaurant
            restaurant_id = session.query(m.MenuItem.restaurant_id).filter(m.MenuItem.id.in_(menu_item_ids) and m.MenuItem.restaurant_id == payload.restaurant_id).first()
            if not restaurant_id:
                raise HTTPException(status_code=400, detail="Invalid menu items")

            address = session.query(Address).filter(Address.user_id == payload.user_id and Address.is_default == True).first()
            delivery_addr_str = format_address(address) if payload.delivery_address else None

            # create order
            food_order = m.FoodOrder(
                user_id=payload.user_id,
                restaurant_id=payload.restaurant_id,
                total_amount=payload.total_amount,
                delivery_address=delivery_addr_str,
                delivery_instructions=payload.delivery_instructions,
            )
            session.add(food_order)
            session.flush()  # populate food_order.id

            # create all order items
            order_items = [
                m.FoodOrderItem(
                    order_id=food_order.id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                )
                for item in payload.items
            ]
            session.add_all(order_items)

            session.commit()
            session.refresh(food_order)

            return {"order_id": food_order.id, "message": "Food order placed successfully"}

        except HTTPException:
            session.rollback()
            raise
        except Exception as exc:
            session.rollback()
            raise HTTPException(status_code=500, detail=str(exc))