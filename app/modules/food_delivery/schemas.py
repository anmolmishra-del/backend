

from pydantic import BaseModel


class CreateResturant(BaseModel):
    name: str
    address: str
    phone_number: int
    owner_id: int
    email: str
    cuisine_type: str
    logo_url: str | None = None
    banner_url: str | None = None       
    status: str | None = "open"
    is_favorite: bool | None = False
    latitude: float
    longitude: float
class ResturantLocation(BaseModel):
    resturant_id: int
    latitude: float
    longitude: float
    address: str | None = None
    state: str | None = None
    country: str | None = None
    location_id: str | None = None
    postal_code: str | None = None
    city: str | None = None
    dining_type: str | None = None  # e.g., dine-in, takeout, delivery
class MenuCategory(BaseModel):
    resturant_id: int
    name: str
    description: str | None = None
class MenuItem(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    price: float
    is_available: bool | None = True
    image_url: str | None = None
    is_vegetarian: bool | None = False
    cooking_time_minutes: int | None = None
        



