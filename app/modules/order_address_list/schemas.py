from pydantic import BaseModel, Field, validator
from typing import Optional

class AddressBase(BaseModel):
   # resturant_id: int
    is_default: bool = Field(False, description="Is this the default address for the user?")
    user_id: int
    latitude: float
    longitude: float
    tag: Optional[str] = Field(None, description="home, pg, office, other")
    flat: Optional[str] = None
    floor: Optional[str] = None
    locality: Optional[str] = None
    landmark: Optional[str] = None
    your_name: Optional[str] = None
    phone_number: Optional[str] = None
   

    @validator("tag")
    def validate_tag(cls, v):
        if v is None:
            return v
        allowed = {"home", "pg", "office", "other"}
        if v.lower() not in allowed:
            raise ValueError(f"tag must be one of {allowed}")
        return v.lower()

class AddressCreate(AddressBase):
    pass

class AddressOut(BaseModel):
    id: int
    is_default: bool
   # resturant_id: int
    user_id: int
    latitude: float
    longitude: float
    tag: Optional[str]
    flat: Optional[str]
    floor: Optional[str]
    locality: Optional[str]
    landmark: Optional[str]
    your_name: Optional[str]
    phone_number: Optional[str]

    class Config:
        from_attributes = True