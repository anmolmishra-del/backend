from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, index=True, nullable=False)
    username = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    # Phone numbers can exceed integer range and may include formatting
    # characters (+, -, spaces). Store as string to be safe.
    phone_number = Column(String(32), nullable=True)
    role = Column(String(50), default="user", nullable=False)
    status = Column(String(50), default="active", nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    roles = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)


class Loaction(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

