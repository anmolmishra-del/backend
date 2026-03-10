from pydantic import BaseModel, EmailStr, validator, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
import re


# Base schemas with ORM mode
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# User related schemas (without username/password)
class UserBase(BaseSchema):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')


class UserCreate(UserBase):
    pass  # No password field - will be handled by auth module


class UserOut(BaseSchema):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    is_active: bool


# Employee schemas
class EmployeeBase(BaseSchema):
    department: Optional[str] = None  # Can be ID or name
    designation: Optional[str] = None  # Can be ID or title


class EmployeeCreate(EmployeeBase, UserCreate):
    pass


class EmployeeUpdate(BaseSchema):
    """Schema for updating employee with all available fields"""
    
    # User fields (from User model)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    
    # Department/Designation (can be ID or name/title)
    department: Optional[str] = None
    designation: Optional[str] = None
    
    # Employment details
    date_of_joining: Optional[date] = None
    date_of_leaving: Optional[date] = None
    is_active: Optional[bool] = None
    manager_id: Optional[int] = None
    
    # Current address
    street1: Optional[str] = Field(None, max_length=256)
    street2: Optional[str] = Field(None, max_length=256)
    city: Optional[str] = Field(None, max_length=128)
    state: Optional[str] = Field(None, max_length=128)
    country: Optional[str] = Field(None, max_length=128)
    zip_code: Optional[str] = Field(None, max_length=20)
    
    # Permanent address
    permanent_street1: Optional[str] = Field(None, max_length=256)
    permanent_street2: Optional[str] = Field(None, max_length=256)
    permanent_city: Optional[str] = Field(None, max_length=128)
    permanent_state: Optional[str] = Field(None, max_length=128)
    permanent_country: Optional[str] = Field(None, max_length=128)
    permanent_zip_code: Optional[str] = Field(None, max_length=20)
    
    # Personal details
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern=r'^(Male|Female|Other|Prefer not to say)$')
    blood_group: Optional[str] = Field(None, pattern=r'^(A|B|AB|O)[+-]$')
    emergency_contact: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    
    # Identification numbers
    uan_number: Optional[str] = Field(None, max_length=50)
    pan_number: Optional[str] = Field(None, max_length=50)
    aadhar_number: Optional[str] = Field(None, max_length=50)
    passport_number: Optional[str] = Field(None, max_length=50)
    esic_number: Optional[str] = Field(None, max_length=50)
    pf_number: Optional[str] = Field(None, max_length=50)
    
    # Bank details
    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=128)
    bank_ifsc_code: Optional[str] = Field(None, max_length=20)
    bank_branch: Optional[str] = Field(None, max_length=128)

    @validator('pan_number')
    def validate_pan(cls, v):
        if v and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v):
            raise ValueError('Invalid PAN number format. Should be: ABCDE1234F')
        return v

    @validator('aadhar_number')
    def validate_aadhar(cls, v):
        if v and not re.match(r'^\d{12}$', v):
            raise ValueError('Invalid Aadhar number. Should be 12 digits')
        return v

    @validator('bank_ifsc_code')
    def validate_ifsc(cls, v):
        if v and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', v):
            raise ValueError('Invalid IFSC code format. Should be: ABCD0123456')
        return v

    @validator('date_of_leaving')
    def validate_leaving_date(cls, v, values):
        if v and 'date_of_joining' in values and values['date_of_joining']:
            if v <= values['date_of_joining']:
                raise ValueError('Date of leaving must be after date of joining')
        return v

    @validator('date_of_birth')
    def validate_dob(cls, v):
        if v and v >= date.today():
            raise ValueError('Date of birth must be in the past')
        return v


class EmployeeOut(BaseSchema):
    id: int
    user_id: int
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    department_name: Optional[str] = None
    designation_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool


class EmployeeDetailOut(BaseSchema):
    id: Optional[int] = None
    user_id: Optional[int] = None
    employee_code: Optional[str] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    date_of_joining: Optional[date] = None
    date_of_leaving: Optional[date] = None
    is_active: Optional[bool] = None
    manager_id: Optional[int] = None

    # User details
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    # Department/Designation names
    department_name: Optional[str] = None
    designation_title: Optional[str] = None

    # Current address
    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None

    # Permanent address
    permanent_street1: Optional[str] = None
    permanent_street2: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_country: Optional[str] = None
    permanent_zip_code: Optional[str] = None

    # Personal details
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None

    # Identification
    uan_number: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None
    esic_number: Optional[str] = None
    pf_number: Optional[str] = None

    # Bank details
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    bank_branch: Optional[str] = None

    @validator('pan_number')
    def validate_pan(cls, v):
        if v and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v):
            raise ValueError('Invalid PAN number format')
        return v

    @validator('bank_ifsc_code')
    def validate_ifsc(cls, v):
        if v and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', v):
            raise ValueError('Invalid IFSC code format')
        return v


class EmployeeListOut(BaseSchema):
    employees: List[EmployeeDetailOut]
    total: int
    page: int
    size: int


# Department schemas
class DepartmentBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=500)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=500)


class DepartmentOut(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    employee_count: Optional[int] = 0


# Designation schemas
class DesignationBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=500)


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=500)


class DesignationOut(DesignationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    employee_count: Optional[int] = 0