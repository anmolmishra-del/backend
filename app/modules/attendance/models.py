from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Float, Boolean, ForeignKey, Text, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"
    WORK_FROM_HOME = "work_from_home"


class LeaveType(enum.Enum):
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"
    COMP_OFF = "compensatory"
    BEREAVEMENT = "bereavement"
    MARRIAGE = "marriage"
    OTHER = "other"


class LeaveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False)
    
    # Location tracking (optional)
    check_in_latitude = Column(Float, nullable=True)
    check_in_longitude = Column(Float, nullable=True)
    check_out_latitude = Column(Float, nullable=True)
    check_out_longitude = Column(Float, nullable=True)
    check_in_ip = Column(String(45), nullable=True)  # IPv6 compatible
    check_out_ip = Column(String(45), nullable=True)
    
    # Device info
    check_in_device = Column(String(255), nullable=True)
    check_out_device = Column(String(255), nullable=True)
    
    # Work details
    work_description = Column(Text, nullable=True)
    overtime_hours = Column(Float, default=0.0)
    late_minutes = Column(Integer, default=0)
    early_exit_minutes = Column(Integer, default=0)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    employee = relationship("Employee", backref="attendances")
    creator = relationship("User", foreign_keys=[created_by], backref="created_attendances")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_attendances")

    __table_args__ = (
        # Ensure one attendance record per employee per day
        UniqueConstraint('employee_id', 'date', name='unique_employee_attendance'),
    )


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type = Column(Enum(LeaveType), nullable=False)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    
    # Leave duration
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Float, nullable=False)  # Support half days
    
    # Reason and comments
    reason = Column(Text, nullable=False)
    comments = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Approval tracking
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Documents
    attachment_path = Column(String(500), nullable=True)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", backref="leave_requests")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_leaves")

    __table_args__ = (
        # Ensure no overlapping leave requests
        Index('idx_leave_overlap', 'employee_id', 'start_date', 'end_date'),
        UniqueConstraint('employee_id', 'start_date', 'end_date', name='unique_employee_leave'),
    )


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    is_recurring = Column(Boolean, default=False)  # For holidays that repeat every year
    description = Column(Text, nullable=True)
    
    # Optional: For company-specific or location-specific holidays
    location = Column(String(100), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department", backref="holidays")

    __table_args__ = (
        # Unique holiday per date (optionally per location/department)
        UniqueConstraint('date', 'location', name='unique_holiday_date_location'),
    )


class WorkShift(Base):
    __tablename__ = "work_shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # Shift timings
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    break_start = Column(Time, nullable=True)
    break_end = Column(Time, nullable=True)
    
    # Grace periods (in minutes)
    grace_period_check_in = Column(Integer, default=15)
    grace_period_check_out = Column(Integer, default=15)
    
    # Working hours
    total_working_hours = Column(Float, nullable=False)  # e.g., 8.5 for 8.5 hours
    is_night_shift = Column(Boolean, default=False)
    
    # Applicable days (bitmask or JSON)
    applicable_days = Column(String(20), default="1,2,3,4,5")  # 1=Monday, 7=Sunday
    
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class EmployeeShift(Base):
    __tablename__ = "employee_shifts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id = Column(Integer, ForeignKey("work_shifts.id", ondelete="CASCADE"), nullable=False)
    
    # Validity period
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)  # NULL means ongoing
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", backref="shift_assignments")
    shift = relationship("WorkShift", backref="employee_assignments")

    __table_args__ = (
        # Ensure no overlapping shift assignments
        Index('idx_shift_overlap', 'employee_id', 'effective_from', 'effective_to'),
    )