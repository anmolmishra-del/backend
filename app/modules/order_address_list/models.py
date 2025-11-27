from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Address(Base):
    __tablename__ = "address_list"   # FIXED
    is_default = Column(Boolean, default=False, nullable=False)
    id = Column(Integer, primary_key=True, index=True)
   # resturant_id = Column(Integer, ForeignKey("restaurant.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
   
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    tag = Column(String, nullable=True)
    flat = Column(String, nullable=True)
    floor = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    landmark = Column(String, nullable=True)
    your_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    # Relations
    user = relationship("User")

    # restaurant = relationship(
    #     "app.modules.food_delivery.model.Restaurant",
    #     back_populates="addresses",
    #     foreign_keys=[resturant_id],
    # )
