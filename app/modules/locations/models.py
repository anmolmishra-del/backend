from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.core.database import Base

class Loaction(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)