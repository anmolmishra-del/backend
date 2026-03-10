from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List
from datetime import date, datetime, time
from enum import Enum

from app.modules.attendance.models import AttendanceStatus, LeaveType, LeaveStatus


# Base schemas with ORM mode
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Attendance Schemas
class AttendanceBase(BaseSchema):
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.PRESENT
    work_description: Optional[str] = Field(None, max_length=1000)
    
    # Location
    check_in_latitude: Optional[float] = None
    check_in_longitude: Optional[float] = None
    check_out_latitude: Optional[float] = None
    check_out_longitude: Optional[float] = None


class AttendanceCreate(AttendanceBase):
    employee_id: int


class AttendanceCheckIn(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_info: Optional[str] = Field(None, max_length=255)
    work_description: Optional[str] = Field(None, max_length=1000)


class AttendanceCheckOut(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_info: Optional[str] = Field(None, max_length=255)
    work_description: Optional[str] = Field(None, max_length=1000)


class AttendanceUpdate(BaseSchema):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None
    work_description: Optional[str] = Field(None, max_length=1000)
    overtime_hours: Optional[float] = Field(None, ge=0)
    late_minutes: Optional[int] = Field(None, ge=0)
    early_exit_minutes: Optional[int] = Field(None, ge=0)


class AttendanceOut(AttendanceBase):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    overtime_hours: float
    late_minutes: int
    early_exit_minutes: int
    created_at: datetime
    updated_at: datetime
    
    @validator('employee_name', always=True)
    def get_employee_name(cls, v, values):
        if 'employee' in values:
            employee = values['employee']
            if employee and hasattr(employee, 'user'):
                return f"{employee.user.first_name} {employee.user.last_name}"
        return v


class AttendanceDetailOut(AttendanceOut):
    check_in_ip: Optional[str] = None
    check_out_ip: Optional[str] = None
    check_in_device: Optional[str] = None
    check_out_device: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class AttendanceSummary(BaseModel):
    employee_id: int
    employee_name: str
    employee_code: str
    total_present: int
    total_absent: int
    total_late: int
    total_half_days: int
    total_leaves: int
    total_overtime_hours: float
    total_working_days: int
    attendance_percentage: float


class DateRange(BaseModel):
    start_date: date
    end_date: date
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v


# Leave Request Schemas
class LeaveRequestBase(BaseSchema):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=5, max_length=1000)
    comments: Optional[str] = Field(None, max_length=500)


class LeaveRequestCreate(LeaveRequestBase):
    employee_id: int


class LeaveRequestUpdate(BaseSchema):
    leave_type: Optional[LeaveType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, min_length=5, max_length=1000)
    comments: Optional[str] = Field(None, max_length=500)


class LeaveRequestApprove(BaseModel):
    approved: bool
    comments: Optional[str] = Field(None, max_length=500)
    rejection_reason: Optional[str] = Field(None, max_length=500)


class LeaveRequestOut(LeaveRequestBase):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    status: LeaveStatus
    total_days: float
    rejection_reason: Optional[str] = None
    approved_by: Optional[int] = None
    approver_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    attachment_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LeaveBalance(BaseModel):
    employee_id: int
    employee_name: str
    employee_code: str
    casual_leave: float
    sick_leave: float
    earned_leave: float
    maternity_leave: float
    paternity_leave: float
    comp_off: float
    total_taken: float
    total_remaining: float


# Holiday Schemas
class HolidayBase(BaseSchema):
    name: str = Field(..., min_length=2, max_length=200)
    date: date
    is_recurring: bool = False
    description: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    date: Optional[date] = None
    is_recurring: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None


class HolidayOut(HolidayBase):
    id: int
    year: int
    created_at: datetime
    updated_at: datetime
    department_name: Optional[str] = None


# Work Shift Schemas
class WorkShiftBase(BaseSchema):
    name: str = Field(..., min_length=2, max_length=100)
    start_time: time
    end_time: time
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    grace_period_check_in: int = 15
    grace_period_check_out: int = 15
    total_working_hours: float
    is_night_shift: bool = False
    applicable_days: str = "1,2,3,4,5"
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class WorkShiftCreate(WorkShiftBase):
    pass


class WorkShiftUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    grace_period_check_in: Optional[int] = Field(None, ge=0)
    grace_period_check_out: Optional[int] = Field(None, ge=0)
    total_working_hours: Optional[float] = Field(None, gt=0)
    is_night_shift: Optional[bool] = None
    applicable_days: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class WorkShiftOut(WorkShiftBase):
    id: int
    created_at: datetime
    updated_at: datetime


class EmployeeShiftAssign(BaseModel):
    employee_id: int
    shift_id: int
    effective_from: date
    effective_to: Optional[date] = None


class EmployeeShiftOut(BaseSchema):
    id: int
    employee_id: int
    employee_name: str
    employee_code: str
    shift_id: int
    shift_name: str
    effective_from: date
    effective_to: Optional[date] = None
    created_at: datetime
    updated_at: datetime


# Monthly Attendance Report
class MonthlyAttendanceReport(BaseModel):
    year: int
    month: int
    employee_id: int
    employee_name: str
    employee_code: str
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    half_days: int
    leave_days: int
    holidays: int
    weekends: int
    work_from_home_days: int
    total_overtime_hours: float
    attendance_details: List[AttendanceOut]