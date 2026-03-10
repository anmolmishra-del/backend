from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets
import re

from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import User, UserStatus, UserRole
from app.modules.auth.schemas import UserCreate, UserUpdate
from app.core.config import settings

import logging
import requests

logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    """Base exception for auth service"""
    pass


class UserNotFoundError(AuthServiceError):
    """User not found"""
    pass


class UserAlreadyExistsError(AuthServiceError):
    """User already exists"""
    pass


class InvalidOTPError(AuthServiceError):
    """Invalid OTP"""
    pass


class AccountLockedError(AuthServiceError):
    """Account is locked"""
    pass


# OTP Store (in production, use Redis)
_otp_store: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Phone Number Utilities
# ============================================================================

def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format"""
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)
    
    # If it's a 10-digit Indian number, add +91
    if len(digits) == 10:
        return f"+91{digits}"
    
    # If it's 12 digits and starts with 91, add +
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    
    # If it already has country code, ensure it has +
    if len(digits) > 10 and not phone.startswith('+'):
        return f"+{digits}"
    
    return phone


# ============================================================================
# User Management Functions
# ============================================================================

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.get(User, user_id)


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """Get user by phone number"""
    normalized = normalize_phone(phone_number)
    return db.execute(
        select(User).where(User.phone_number == normalized)
    ).scalar_one_or_none()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    try:
        normalized_phone = normalize_phone(user_data.phone_number)
        
        # Check if user already exists
        existing = get_user_by_phone(db, normalized_phone)
        if existing:
            raise UserAlreadyExistsError("User with this phone number already exists")
        
        # Create new user
        db_user = User(
            phone_number=normalized_phone,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            username=user_data.username,
            role=UserRole.USER.value,
            status=UserStatus.ACTIVE.value,
            is_phone_verified=True,  # Verified via OTP
            phone_verified_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.flush()
        logger.info(f"User created: {db_user.phone_number}")
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating user: {e}")
        raise UserAlreadyExistsError("User with this phone number already exists")


def update_user(db: Session, user_id: int, updates: UserUpdate) -> User:
    """Update user information"""
    user = db.get(User, user_id)
    if not user:
        raise UserNotFoundError("User not found")
    
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.flush()
    return user


def delete_user(db: Session, user_id: int, soft_delete: bool = True) -> None:
    """Delete user (soft delete by default)"""
    user = db.get(User, user_id)
    if not user:
        raise UserNotFoundError("User not found")
    
    if soft_delete:
        user.deleted_at = datetime.utcnow()
        user.status = UserStatus.INACTIVE.value
    else:
        db.delete(user)
    
    db.flush()


# ============================================================================
# OTP Functions
# ============================================================================

def _generate_otp(length: int = 6) -> str:
    """Generate a secure OTP"""
    # In production, use secrets
    import secrets
    import string
    alphabet = string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_otp(phone_number: str, purpose: str = "login", expire_minutes: int = 5) -> Dict[str, Any]:
    """Send OTP via SMS using MSG91"""
    try:
        normalized_phone = normalize_phone(phone_number)
        
        # Generate OTP
        otp = _generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
        
        # Log OTP for development
        logger.info(f"📱 OTP for {normalized_phone}: {otp}")
        
        # Try to send via MSG91 if configured
        sms_sent = False
        if settings.MSG91_AUTH_KEY and settings.MSG91_TEMPLATE_ID:
            sms_sent = send_otp_via_msg91(normalized_phone, otp, expire_minutes)
            if sms_sent:
                logger.info(f"SMS sent via MSG91 to {normalized_phone}")
        else:
            logger.warning("MSG91 not configured - OTP will not be sent via SMS")
        
        # Store OTP for verification
        _otp_store[normalized_phone] = {
            "otp": otp,
            "expires_at": expires_at,
            "purpose": purpose,
            "attempts": 0,
            "sms_sent": sms_sent
        }
        
        # Prepare response
        response = {
            "ok": True,
            "message": "OTP generated successfully",
            "expires_in": expire_minutes * 60,
            "sms_sent": sms_sent
        }
        
        # Include OTP in debug mode for testing
        if settings.DEBUG:
            response["debug_otp"] = otp
            if not sms_sent:
                response["message"] = "OTP generated (SMS not sent - configure MSG91 for production)"
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate OTP: {e}")
        raise HTTPException(
            # status_code=stat.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OTP"
        )


def verify_otp(phone_number: str, otp: str, purpose: str = "login") -> bool:
    """Verify OTP"""
    try:
        normalized_phone = normalize_phone(phone_number)
        
        # Get stored OTP
        stored = _otp_store.get(normalized_phone)
        if not stored:
            raise InvalidOTPError("No OTP found for this number. Please request a new OTP.")
        
        # Check purpose
        if stored["purpose"] != purpose:
            raise InvalidOTPError("OTP purpose mismatch")
        
        # Check expiry
        if datetime.utcnow() > stored["expires_at"]:
            _otp_store.pop(normalized_phone, None)
            raise InvalidOTPError("OTP has expired. Please request a new one.")
        
        # Increment attempts
        stored["attempts"] = stored.get("attempts", 0) + 1
        
        # Check max attempts (prevent brute force)
        if stored["attempts"] > 3:
            _otp_store.pop(normalized_phone, None)
            raise InvalidOTPError("Too many failed attempts. Please request a new OTP.")
        
        # Verify OTP
        if stored["otp"] != otp:
            raise InvalidOTPError(f"Invalid OTP. {3 - stored['attempts']} attempts remaining.")
        
        # Success - clear OTP
        _otp_store.pop(normalized_phone, None)
        return True
        
    except InvalidOTPError:
        raise
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        raise InvalidOTPError("OTP verification failed")

def send_otp_via_msg91(phone: str, otp: str, expire_minutes: int = 5) -> bool:
    """
    Send OTP via MSG91 OTP API
    Returns True if successful, False otherwise
    """
    if not settings.MSG91_AUTH_KEY or not settings.MSG91_TEMPLATE_ID:
        logger.warning("MSG91 credentials missing")
        return False
    
    try:
        url = "https://control.msg91.com/api/v5/otp"
        mobile = phone.replace('+', '').strip()
        
        params = {
            "authkey": settings.MSG91_AUTH_KEY,
            "template_id": settings.MSG91_TEMPLATE_ID,
            "mobile": mobile,
            "otp": otp,
            "otp_expiry": expire_minutes
        }
        
        headers = {
            "content-type": "application/json",
            "accept": "application/json"
        }
        
        response = requests.post(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("type") == "success":
                logger.info(f"✅ OTP sent to {mobile}")
                return True
        
        logger.error(f"❌ MSG91 failed: {response.text}")
        return False
        
    except Exception as e:
        logger.error(f"❌ MSG91 error: {e}")
        return False

# ============================================================================
# Authentication Functions
# ============================================================================

def authenticate_with_otp(
    db: Session, 
    phone_number: str, 
    otp: str,
    ip_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Authenticate user with phone and OTP
    Returns user and flag indicating if user is new
    """
    try:
        # Verify OTP first
        verify_otp(phone_number, otp, "login")
        
        normalized_phone = normalize_phone(phone_number)
        
        # Find or create user
        user = get_user_by_phone(db, normalized_phone)
        is_new_user = False
        
        if not user:
            # Auto-create user if not exists
            user = User(
                phone_number=normalized_phone,
                role=UserRole.USER.value,
                status=UserStatus.ACTIVE.value,
                is_phone_verified=True,
                phone_verified_at=datetime.utcnow()
            )
            db.add(user)
            db.flush()
            is_new_user = True
            logger.info(f"New user auto-created: {normalized_phone}")
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise AccountLockedError(f"Account locked until {user.locked_until}")
        
        # Update login info
        user.failed_otp_attempts = 0
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address
        
        db.flush()
        
        return {
            "user": user,
            "is_new_user": is_new_user
        }
        
    except InvalidOTPError:
        # Track failed attempt if user exists
        normalized_phone = normalize_phone(phone_number)
        user = get_user_by_phone(db, normalized_phone)
        
        if user:
            user.failed_otp_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_otp_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            db.flush()
        
        raise
    except AccountLockedError:
        raise
    except Exception as e:
        logger.error(f"OTP authentication error: {e}")
        raise AuthServiceError("Authentication failed")


# ============================================================================
# Role and Permission Functions
# ============================================================================

def user_has_role(user: User, role: str) -> bool:
    """Check if user has a specific role"""
    return user.role == role or role in user.roles


def user_has_any_role(user: User, roles: List[str]) -> bool:
    """Check if user has any of the specified roles"""
    return user.role in roles or any(r in user.roles for r in roles)