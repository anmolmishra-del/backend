from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime



class LocationCreate(BaseModel):
    user_id: Optional[int] = None
    latitude: float
    longitude: float

    @validator("latitude")
    def latitude_range(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v
    @validator("longitude")
    def longitude_range(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v
    


class LocationOut(BaseModel):
    user_id: Optional[int] = None
    latitude: float
    longitude: float

    class Config:
        from_attributes = True