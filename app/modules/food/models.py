# app/modules/food/models.py
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, TIMESTAMP, func, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    foods = relationship("Food", back_populates="restaurant", cascade="all, delete-orphan")


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # If you need a JSON column named 'metadata' in DB, do NOT use attribute name `metadata`.
    # Use attribute name `metadata_json` and map to column "metadata" like:
    # metadata_json = Column("metadata", JSON, nullable=True)

    restaurant = relationship("Restaurant", back_populates="foods")


# class Location(Base):
#     __tablename__ = "locations"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, nullable=False, index=True)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)
#     timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())
