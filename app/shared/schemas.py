from pydantic import BaseModel,EmailStr
from typing import List


class UserCreate(BaseModel):
	username: str
	password: str
	email: EmailStr 
	roles: List[str] = []


class UserOut(BaseModel):
	id: int
	email: EmailStr
	username: str
	roles: List[str] = []


class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"
