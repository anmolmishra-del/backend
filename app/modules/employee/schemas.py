from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: Optional[str] = None
    password: str
    phone_number: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None  # name or id
    designation: Optional[str] = None  # name or id

class EmployeeOut(BaseModel):
    id: int
    user_id: int
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    username: Optional[str] = None
    phone_number: Optional[str] = None
    position: Optional[str] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DesignationCreate(BaseModel):
    title: str
    description: Optional[str] = None   

class DesignationOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
class EmployeeDetailOut(EmployeeOut):
    department: Optional[DepartmentOut] = None
    designation: Optional[DesignationOut] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    position: Optional[str] = None  
    date_of_joining: Optional[datetime] = None
    date_of_leaving: Optional[datetime] = None
    is_active: bool
    manager_id: Optional[int] = None
    street1: Optional[str] = None   
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None   
    zip_code: Optional[str] = None
    permanent_street1: Optional[str] = None
    permanent_street2: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_country: Optional[str] = None
    permanent_zip_code: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None       
    emergency_contact: Optional[str] = None
    uan_number: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None
    esic_number: Optional[str] = None
    pf_number: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    bank_branch: Optional[str] = None   

class EmployeeListOut(BaseModel):
    employees: List[EmployeeDetailOut]
    
