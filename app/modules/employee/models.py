from sqlalchemy import BigInteger, Column, Float, Integer, String, Boolean, DateTime, false, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base
from app.modules.auth.models import User

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Designation(Base):
    __tablename__ = "designations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), unique=True, nullable=False)
    description = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, nullable=True)
    designation_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    employee_code = Column(String(50), unique=True, nullable=False)
    date_of_joining = Column(DateTime, nullable=True)
    date_of_leaving = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)       
    manager_id = Column(Integer, nullable=True)
    street1 = Column(String(256), nullable=True)
    street2 = Column(String(256), nullable=True)
    city = Column(String(128), nullable=True)
    state = Column(String(128), nullable=True)
    country = Column(String(128), nullable=True)
    zip_code = Column(String(20), nullable=True)
    permanent_street1 = Column(String(256), nullable=True)
    permanent_street2 = Column(String(256), nullable=True)
    permanent_city = Column(String(128), nullable=True)
    permanent_state = Column(String(128), nullable=True)
    permanent_country = Column(String(128), nullable=True)  
    permanent_zip_code = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    uan_number = Column(String(50), unique=True, nullable=True)
    pan_number = Column(String(50), unique=True, nullable=True)
    aadhar_number = Column(String(50), unique=True, nullable=True)
    passport_number = Column(String(50), unique=True, nullable=True)
    esic_number = Column(String(50), unique=True, nullable=True)
    pf_number = Column(String(50), unique=True, nullable=True)
    bank_account_number = Column(String(50), unique=True, nullable=True)
    bank_name = Column(String(128), nullable=True)
    bank_ifsc_code = Column(String(20), nullable=True)
    bank_branch = Column(String(128), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="employee", uselist=False)

    

