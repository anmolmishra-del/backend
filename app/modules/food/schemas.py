# app/modules/food/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

# Create / Update schemas
class FoodCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float

    model_config = {"extra": "forbid"}


class FoodRead(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    created_at: datetime

    model_config = {"from_attributes": True}


class RestaurantRead(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# class LocationCreate(BaseModel):
#     user_id: Optional[int] = None
#     latitude: float
#     longitude: float

#     @field_validator("latitude")
#     def latitude_range(cls, v):
#         if not -90 <= v <= 90:
#             raise ValueError("Latitude must be between -90 and 90")
#         return v

#     @field_validator("longitude")
#     def longitude_range(cls, v):
#         if not -180 <= v <= 180:
#             raise ValueError("Longitude must be between -180 and 180")
#         return v


# class LocationRead(BaseModel):
#     id: int
#     user_id: int
#     latitude: float
#     longitude: float
#     timestamp: datetime

#     model_config = {"from_attributes": True}

class RestaurantCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None

    model_config = {"extra": "forbid"}    
