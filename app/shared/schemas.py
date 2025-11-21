from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    roles: List[str] = []


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    role: str
    status: str
    is_email_verified: bool
    roles: List[str] = []
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
	username: str
	password: str
	email: EmailStr 
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	phone_number: Optional[int] = None
	roles: List[str] = []


class UserOut(BaseModel):
	id: int
	email: EmailStr
	username: str
	first_name: Optional[str]
	last_name: Optional[str]
	phone_number: Optional[int]
	role: str
	status: str
	is_email_verified: bool
	roles: List[str] = []
	created_at: datetime
	updated_at: datetime
	last_login: Optional[datetime]

	class Config:
		from_attributes = True



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
	# class Config:
	# 	from_attributes = True



class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"
