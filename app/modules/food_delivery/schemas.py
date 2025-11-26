# app/modules/food_delivery/schemas.py
from __future__ import annotations
from typing_extensions import Annotated
from pydantic import BaseModel, EmailStr, Field, validator, conint, confloat
from typing import Optional
from datetime import datetime



class RestaurantLocationCreate(BaseModel):
    latitude: float = Field(..., description="Latitude in decimal degrees")
    longitude: float = Field(..., description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, max_length=512)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    location_id: Optional[str] = Field(None, max_length=128)
    postal_code: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    dining_type: Optional[str] = Field(None, max_length=50)  # e.g., dine-in, takeout, delivery

class CreateRestaurant(BaseModel):
    name: str = Field(..., max_length=256)
    owner_id: int
    address: Optional[str] = Field(None, max_length=512)
    phone_number: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    cuisine_type: Optional[str] = Field(None, max_length=128)
    logo_url: Optional[str] = Field(None, max_length=512)
    banner_url: Optional[str] = Field(None, max_length=512)
    status: Optional[str] = Field("open", max_length=50)
    is_favorite: Optional[bool] = False

 
    location: Optional[RestaurantLocationCreate] = None

 
    class Config:
        schema_extra = {
            "example": {
                "name": "Cafe Nirvana",
                "owner_id": 123,
                "address": "12 Example St",
                "phone_number": "+91 98765 43210",
                "email": "owner@example.com",
                "cuisine_type": "Cafe",
                "status": "open",
                "is_favorite": False,
                "location": {
                    "latitude": 12.9715987,
                    "longitude": 77.5945627,
                    "city": "Bengaluru"
                }
            }
        }



class MenuCategoryCreate(BaseModel):
    restaurant_id: int
    name: str = Field(..., max_length=128)
    description: Optional[str] = Field(None, max_length=512)

    class Config:
        schema_extra = {
            "example": {"restaurant_id": 12, "name": "Starters", "description": "Small bites and appetizers"}
        }


class MenuItemCreate(BaseModel):
    category_id: int
    name: str = Field(..., max_length=256)
    description: Optional[str] = Field(None, max_length=1024)
    restaurant_id: int
    price: Annotated[float, Field(ge=0)]
    cooking_time_minutes: Annotated[int | None, Field(ge=0)]
    is_available: Optional[bool] = True
    image_url: Optional[str] = Field(None, max_length=512)
    is_vegetarian: Optional[bool] = False
  

    class Config:
        schema_extra = {
            "example": {
                "category_id": 1,
                "name": "Garlic Bread",
                "restaurant_id": 1,
                "description": "Toasted garlic bread slices",
                "price": 79.0,
                "is_available": True,
                "is_vegetarian": True,
                "cooking_time_minutes": 10
            }
        }


# -------------------------
# Output (response) models
# -------------------------
class RestaurantShort(BaseModel):
    id: int
    name: str
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True


class MenuCategoryOut(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    # include restaurant short info if you eager-load it on queries
    restaurant: Optional[RestaurantShort] = None

    class Config:
        from_attributes = True


class MenuItemOut(BaseModel):
    id: int
    category_id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool
    image_url: Optional[str] = None
    is_vegetarian: bool
    cooking_time_minutes: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
