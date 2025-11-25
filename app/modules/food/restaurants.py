from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import RestaurantCreate, RestaurantRead
from app.core.database import SessionLocal
from . import crud

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=dict)
async def list_restaurants(q: str = Query(None), city: str = Query(None), limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    total, items = await crud.get_restaurants(db, q=q, city=city, limit=limit, offset=offset)
    return {"count": total, "limit": limit, "offset": offset, "results": items}
 
@router.get("/{restaurant_id}", response_model=RestaurantRead)
async def get_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    r = await crud.get_restaurant(db, restaurant_id)
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return r

@router.post("/", response_model=RestaurantRead)
def create_restaurant(restaurant: RestaurantCreate, db: AsyncSession = Depends(get_db)):
    r = crud.create_restaurant(db, restaurant.dict())
    return r