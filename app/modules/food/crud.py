# app/modules/food/crud.py
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.modules.food.models import Food, Restaurant
from app.modules.food.schemas import FoodCreate, FoodRead
from app.core.database import SessionLocal 
def create_restaurant(db: AsyncSession, payload: dict) -> Restaurant:
    session = SessionLocal()
    db_obj = Restaurant(
        name=payload["name"],
        address=payload.get("address"),
        phone=payload.get("phone"),
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

async def get_restaurant(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
    res = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    return res.scalars().first()

async def create_food(db: AsyncSession, restaurant_id: int, payload: FoodCreate) -> FoodRead:
    db_obj = Food(
        restaurant_id=restaurant_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        price=payload.price,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return FoodRead.from_orm(db_obj)

async def get_foods(
    db: AsyncSession,
    restaurant_id: int,
    category: Optional[str] = None,
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[int, List[FoodRead]]:
    conditions = [Food.restaurant_id == restaurant_id]
    if category:
        conditions.append(Food.category == category)
    if q:
        ilike_q = f"%{q}%"
        conditions.append((Food.name.ilike(ilike_q)) | (Food.description.ilike(ilike_q)))
    if min_price is not None:
        conditions.append(Food.price >= min_price)
    if max_price is not None:
        conditions.append(Food.price <= max_price)

    where_clause = and_(*conditions) if conditions else None

    # total
    count_stmt = select(func.count()).select_from(Food)
    if where_clause is not None:
        count_stmt = count_stmt.where(where_clause)
    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one()

    # items
    items_stmt = select(Food)
    if where_clause is not None:
        items_stmt = items_stmt.where(where_clause)
    items_stmt = items_stmt.order_by(Food.id).limit(limit).offset(offset)
    items_res = await db.execute(items_stmt)
    items = items_res.scalars().all()

    return total, [FoodRead.from_orm(it) for it in items]


# # Location CRUD
# async def create_location(db: AsyncSession, payload: LocationCreate) -> LocationRead:
#     db_obj = Location(
#         user_id=payload.user_id,
#         latitude=payload.latitude,
#         longitude=payload.longitude,
#     )
#     db.add(db_obj)
#     await db.commit()
#     await db.refresh(db_obj)
#     return LocationRead.from_orm(db_obj)

# async def get_locations_for_user(db: AsyncSession, user_id: int):
#     res = await db.execute(select(Location).where(Location.user_id == user_id).order_by(Location.id))
#     return res.scalars().all()
