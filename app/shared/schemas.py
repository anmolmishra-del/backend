from pydantic import BaseModel, EmailStr
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

class Location(BaseModel):
	user_id: int
	latitude: str
	longitude: str
	timestamp: datetime

	class Config:
		from_attributes = True



class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"
