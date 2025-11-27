from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import SessionLocal
from app.modules.auth.models import User
from app.modules.food_delivery.model import Restaurant
from app.modules.order_address_list.models import Address
from app.modules.order_address_list.schemas import AddressBase, AddressOut


router = APIRouter(prefix="/address_list", tags=["address_list"])


def get_user_or_404(session: Session, user_id: int) -> User:
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_restaurant_or_404(session: Session, rest_id: int) -> Restaurant:
    rest = session.query(Restaurant).filter(Restaurant.id == rest_id).first()
    if not rest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return rest


def get_address(session: Session, address_id: int):
    return session.query(Address).filter(Address.id == address_id).first()


@router.post("/create_user_address", response_model=AddressOut)
def create_address(payload: AddressBase):
    session = SessionLocal()
    user = get_user_or_404(session, payload.user_id)
    # rest = get_restaurant_or_404(session, payload.resturant_id)

    # addr = None
    # if payload.address_id:
    #     addr = get_address(session, payload.address_id)
    #     if not addr:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    #     if addr.user_id != payload.user_id or addr.resturant_id != payload.resturant_id:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Address does not belong to given user/restaurant")

    your_name = payload.your_name or user.first_name
    phone_number = payload.phone_number or user.phone_number

    
        

      
    explicit_default_provided: bool = payload.is_default is not None
    make_default: bool = bool(payload.is_default)
     
    if make_default:
            session.query(Address).filter(
                Address.user_id == payload.user_id
            ).update({"is_default": False}, synchronize_session=False)

    if not explicit_default_provided:
            existing_count = session.query(Address).filter(Address.user_id == payload.user_id).count()
            if existing_count == 0:
                make_default = True

      

    new_addr = Address(
        is_default=make_default,
        user_id=payload.user_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        tag=payload.tag,
        flat=payload.flat,
        floor=payload.floor,
        locality=payload.locality,
        landmark=payload.landmark,
        your_name=your_name,
        phone_number=phone_number,
        
    )

    session.add(new_addr)
    session.commit()
    session.refresh(new_addr)
    return new_addr


@router.get("/users/{user_id}/addresses", response_model=List[AddressOut])
def list_user_addresses(user_id: int, limit: int = 50, offset: int = 0):
    session = SessionLocal()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    query = (
        session.query(Address)
        .filter(Address.user_id == user_id)
        .order_by(Address.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return query.all()

@router.delete("/delete_address/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int):
    session = SessionLocal()
    addr = get_address(session, address_id)
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    session.delete(addr)
    session.commit()
    return

@router.post("/set_default_address/{address_id}", response_model=AddressOut )   
def set_default_address(address_id: int):
    session = SessionLocal()
    addr = get_address(session, address_id)
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    session.query(Address).filter(
        Address.user_id == addr.user_id
    ).update({"is_default": False}, synchronize_session=False)

    addr.is_default = True
    session.commit()
    session.refresh(addr)
    return addr
@router.put("/update_address/{address_id}", response_model=AddressOut)
def update_address(address_id: int, payload: AddressBase):
    session = SessionLocal()
    addr = get_address(session, address_id)
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(addr, field, value)

    session.commit()
    session.refresh(addr)
    return addr