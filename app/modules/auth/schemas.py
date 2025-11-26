
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime

from app.modules.locations.models import Loaction
from app.modules.locations.schemas import LocationOut





class UserCreate(BaseModel):
	username: str
	password: str
	email: EmailStr 
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	phone_number: str = None
	roles: List[str] = []


class UserOut(BaseModel):
	id: int
	email: EmailStr
	username: str
	first_name: Optional[str]
	last_name: Optional[str]
	phone_number: str
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
	phone_number: str
    #email: EmailStr
    #password: str
class Token(BaseModel):
	
    access_token: str
    token_type: str = "bearer"

class loginOut(BaseModel):
	access_token: str
	token_type: str = "bearer"
	user: UserOut
	location: Optional[LocationOut] = []



class OTPRequest(BaseModel):
    phone_number: str
    otp: str | None = None 


class OTPSender(BaseModel):
    phone_number: str
    
	
