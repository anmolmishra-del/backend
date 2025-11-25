# app/modules/food/routers/foods.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.modules.food import crud
from app.modules.food.schemas import FoodRead, FoodCreate

router = APIRouter(prefix="/restaurants/{restaurant_id}/foods", tags=["foods"])

# Async DB dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/", response_model=dict)
async def list_foods(
    restaurant_id: int,
    category: Optional[str] = None,
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    total, items = await crud.get_foods(
        db,
        restaurant_id=restaurant_id,
        category=category,
        q=q,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )
    return {"count": total, "limit": limit, "offset": offset, "results": items}

@router.post("/", response_model=FoodRead, status_code=status.HTTP_201_CREATED)
async def create_food(restaurant_id: int, payload: FoodCreate, db: AsyncSession = Depends(get_db)):
    r = await crud.get_restaurant(db, restaurant_id)
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    f = await crud.create_food(db, restaurant_id, payload)
    return f
