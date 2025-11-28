
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Table,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


restaurant_category = Table(
    "restaurant_category",
    Base.metadata,
    Column("restaurant_id", Integer, ForeignKey("restaurant.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("menu_category.id"), primary_key=True),
)


class Restaurant(Base):
    __tablename__ = "restaurant"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, index=True, nullable=False)
   
    cuisine_type = Column(String(128), nullable=True)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(256), unique=True, index=True, nullable=True)
    logo_url = Column(String(512), nullable=True)
    banner_url = Column(String(512), nullable=True)
    status = Column(String(50), default="open", nullable=False)
    rating = Column(Float, nullable=True)
    is_favorite = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    
   
    categories = relationship(
        "MenuCategory",
        secondary=restaurant_category,
        back_populates="restaurants",
        lazy="select",
    )

    # one-to-many relationships
    locations = relationship(
        "RestaurantLocation",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        lazy="select",
    )
    orders = relationship(
        "FoodOrder",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        lazy="select",
    )
    items = relationship(
        "MenuItem",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        lazy="select",
    )


class RestaurantLocation(Base):
    __tablename__ = "restaurant_location"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(512), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    location_id = Column(String(128), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    dining_type = Column(String(50), nullable=True)  # e.g., dine-in, takeout, delivery
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationship back to restaurant
    restaurant = relationship("Restaurant", back_populates="locations")


class MenuCategory(Base):
    __tablename__ = "menu_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # many-to-many back to restaurants
    restaurants = relationship(
        "Restaurant",
        secondary=restaurant_category,
        back_populates="categories",
        lazy="select",
    )

    # one-to-many to items
    items = relationship(
        "MenuItem",
        back_populates="category",
        lazy="select",
    )


class MenuItem(Base):
    __tablename__ = "menu_item"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("menu_category.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    description = Column(String(1024), nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    image_url = Column(String(512), nullable=True)
    is_vegetarian = Column(Boolean, default=False, nullable=False)
    cooking_time_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationship back to restaurant and category
    restaurant = relationship("Restaurant", back_populates="items")
    category = relationship("MenuCategory", back_populates="items")


class FoodOrder(Base):
    __tablename__ = "food_order"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    restaurant_location_id = Column(Integer, ForeignKey("restaurant_location.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False)
    delivery_address = Column(String(512), nullable=True)
    delivery_instructions = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    location = relationship("RestaurantLocation")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select",
    )


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("food_order.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_item.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    special_instructions = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    order = relationship("FoodOrder", back_populates="items")
    menu_item = relationship("MenuItem")
