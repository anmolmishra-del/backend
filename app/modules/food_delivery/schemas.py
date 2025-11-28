# app/modules/food_delivery/schemas.py
from __future__ import annotations
from typing_extensions import Annotated
from pydantic import BaseModel, EmailStr, Field, validator, conint, confloat
from typing import List, Optional
from datetime import datetime

from app.modules.order_address_list.schemas import AddressBase


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


class RestaurantLocationOut(RestaurantLocationCreate):
    id: int
    restaurant_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreateRestaurant(BaseModel):
    name: str = Field(..., max_length=256)
 
    address: Optional[str] = Field(None, max_length=512)
    phone_number: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    cuisine_type: Optional[str] = Field(None, max_length=128)
    logo_url: Optional[str] = Field(None, max_length=512)
    banner_url: Optional[str] = Field(None, max_length=512)
    status: Optional[str] = Field("open", max_length=50)
    is_favorite: Optional[bool] = False
    # many-to-many: list of category ids to attach to restaurant
    categories_id: Optional[List[int]] = None
    # optional initial location to create along with restaurant
    location: Optional[RestaurantLocationCreate] = None

    @validator("categories_id", pre=True, always=False)
    def ensure_categories_list(cls, v):
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("categories_id must be a list of integers")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Cafe Nirvana",
               
                "categories_id": [1, 2, 3],
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
    name: str = Field(..., max_length=128)
    description: Optional[str] = Field(None, max_length=512)

    class Config:
        json_schema_extra = {
            "example": {"name": "Starters", "description": "Small bites and appetizers"}
        }


class MenuCategoryShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MenuItemCreate(BaseModel):
    category_id: int
    # restaurant_id is optional here because you may create an item via a restaurant endpoint
    restaurant_id: Optional[int] = None
    name: str = Field(..., max_length=256)
    description: Optional[str] = Field(None, max_length=1024)
    price: Annotated[float, Field(ge=0)]
    cooking_time_minutes: Optional[Annotated[int, Field(ge=0)]] = None
    is_available: Optional[bool] = True
    image_url: Optional[str] = Field(None, max_length=512)
    is_vegetarian: Optional[bool] = False

    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "restaurant_id": 1,
                "name": "Garlic Bread",
                "description": "Toasted garlic bread slices",
                "price": 79.0,
                "is_available": True,
                "is_vegetarian": True,
                "cooking_time_minutes": 10
            }
        }


class MenuItemOut(BaseModel):
    id: int
    category_id: int
    restaurant_id: int
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


class RestaurantShort(BaseModel):
    id: int
    name: str
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True


class MenuCategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    # include short restaurant info if you eager-load it on queries
    restaurants: Optional[List[RestaurantShort]] = None

    class Config:
        from_attributes = True


class RestaurantOut(BaseModel):
    id: int
    name: str
    
    cuisine_type: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    status: str
    rating: Optional[float] = None
    is_favorite: bool
    created_at: datetime
    updated_at: datetime

    # categories as short objects (many-to-many)
    categories: Optional[List[MenuCategoryShort]] = None

    # locations (if eager-loaded)
    locations: Optional[List[RestaurantLocationOut]] = None

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: Annotated[int, Field(gt=0)]

    class Config:
        json_schema_extra = {"example": {"menu_item_id": 3, "quantity": 2}}


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    price_per_item: float
    total_price: float
    special_instructions: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FoodOrderCreate(BaseModel):
    user_id: int
    restaurant_id: int
    total_amount: Annotated[float, Field(ge=0)]
    delivery_address: Optional[str] = Field(None, max_length=512)
    delivery_instructions: Optional[str] = Field(None, max_length=1024)
    items: List[OrderItemCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 45,
                "restaurant_id": 10,
                "total_amount": 250.75,
                "delivery_address": "12 Example St, Bengaluru",
                "delivery_instructions": "Leave at the doorstep",
                "items": [{"menu_item_id": 1, "quantity": 2}],
            }
        }


class FoodOrderOut(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    total_amount: float
    restaurant_location_id: int
    status: str
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: Optional[List[OrderItemOut]] = None

    class Config:
        from_attributes = True


def format_address(address: AddressBase) -> str:
    """Format address with each component on a new line."""
    parts: List[str] = []

    # typical AddressBase fields used in your project — keep optional checks
    if getattr(address, "flat", None):
        parts.append(address.flat)

    if getattr(address, "floor", None):
        parts.append(address.floor)

    if getattr(address, "locality", None):
        parts.append(address.locality)

    if getattr(address, "landmark", None):
        parts.append(address.landmark)

    # Optional extra info
    if getattr(address, "tag", None):
        parts.append(f"({address.tag})")

    if getattr(address, "your_name", None):
        parts.append(f"Name: {address.your_name}")

    if getattr(address, "phone_number", None):
        parts.append(f"Phone: {address.phone_number}")

    return "\n".join(parts) if parts else ""
