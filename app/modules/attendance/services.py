from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import calendar
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.modules.employee.models import Employee
from app.modules.attendance.models import (
    Attendance, AttendanceStatus, LeaveRequest, LeaveType, LeaveStatus,
    Holiday, WorkShift, EmployeeShift
)
from app.modules.attendance.schemas import (
    AttendanceCreate, AttendanceSummary, AttendanceUpdate, AttendanceCheckIn, AttendanceCheckOut, LeaveBalance,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestApprove,
    HolidayCreate, HolidayUpdate, WorkShiftCreate, WorkShiftUpdate,
    DateRange, EmployeeShiftAssign
)

import logging

logger = logging.getLogger(__name__)


class AttendanceServiceError(Exception):
    """Base exception for attendance service"""
    pass


class NotFoundError(AttendanceServiceError):
    """Resource not found"""
    pass


class DuplicateError(AttendanceServiceError):
    """Duplicate resource"""
    pass


class ValidationError(AttendanceServiceError):
    """Validation error"""
    pass


# Helper functions
def _get_current_shift(db: Session, employee_id: int, attendance_date: date) -> Optional[WorkShift]:
    """Get the shift assigned to an employee for a given date"""
    shift_assignment = db.execute(
        select(EmployeeShift)
        .where(
            and_(
                EmployeeShift.employee_id == employee_id,
                EmployeeShift.effective_from <= attendance_date,
                or_(
                    EmployeeShift.effective_to.is_(None),
                    EmployeeShift.effective_to >= attendance_date
                )
            )
        )
        .order_by(EmployeeShift.effective_from.desc())
    ).scalar_one_or_none()
    
    return shift_assignment.shift if shift_assignment else None


def _calculate_work_hours(check_in: datetime, check_out: datetime) -> float:
    """Calculate total work hours"""
    if not check_in or not check_out:
        return 0.0
    delta = check_out - check_in
    return round(delta.total_seconds() / 3600, 2)


def _determine_attendance_status(
    check_in: Optional[datetime],
    check_out: Optional[datetime],
    shift: Optional[WorkShift],
    date: date,
    is_holiday: bool = False,
    is_weekend: bool = False
) -> AttendanceStatus:
    """Determine attendance status based on check-in/out times and shift"""
    
    if is_holiday:
        return AttendanceStatus.HOLIDAY
    
    if is_weekend:
        return AttendanceStatus.WEEKEND
    
    if not check_in:
        return AttendanceStatus.ABSENT
    
    if shift:
        # Check if late
        shift_start = datetime.combine(date, shift.start_time)
        grace_end = shift_start + timedelta(minutes=shift.grace_period_check_in)
        
        if check_in > grace_end:
            return AttendanceStatus.LATE
    
    return AttendanceStatus.PRESENT


def _is_weekend(date: date) -> bool:
    """Check if given date is weekend (Saturday=5, Sunday=6)"""
    return date.weekday() >= 5


def _is_holiday(db: Session, date: date, employee_id: Optional[int] = None) -> bool:
    """Check if given date is a holiday"""
    query = select(Holiday).where(Holiday.date == date)
    
    # If employee_id provided, check department-specific holidays
    if employee_id:
        employee = db.get(Employee, employee_id)
        if employee and employee.department_id:
            query = query.where(
                or_(
                    Holiday.department_id.is_(None),
                    Holiday.department_id == employee.department_id
                )
            )
    
    holiday = db.execute(query).scalar_one_or_none()
    return holiday is not None


# Attendance Services
def check_in(db: Session, employee_id: int, data: AttendanceCheckIn) -> Attendance:
    """Record employee check-in"""
    today = date.today()
    
    # Check if already checked in today
    existing = db.execute(
        select(Attendance).where(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date == today
            )
        )
    ).scalar_one_or_none()
    
    if existing:
        if existing.check_in_time:
            raise ValidationError("Already checked in today")
        existing.check_in_time = datetime.utcnow()
        existing.check_in_latitude = data.latitude
        existing.check_in_longitude = data.longitude
        existing.check_in_device = data.device_info
        existing.work_description = data.work_description or existing.work_description
        db.flush()
        return existing
    
    # Determine status
    is_weekend = _is_weekend(today)
    is_holiday = _is_holiday(db, today, employee_id)
    
    shift = _get_current_shift(db, employee_id, today)
    status = _determine_attendance_status(
        datetime.utcnow(), None, shift, today, is_holiday, is_weekend
    )
    
    attendance = Attendance(
        employee_id=employee_id,
        date=today,
        check_in_time=datetime.utcnow(),
        check_in_latitude=data.latitude,
        check_in_longitude=data.longitude,
        check_in_device=data.device_info,
        work_description=data.work_description,
        status=status
    )
    
    db.add(attendance)
    db.flush()
    return attendance


def check_out(db: Session, employee_id: int, data: AttendanceCheckOut) -> Attendance:
    """Record employee check-out"""
    today = date.today()
    
    attendance = db.execute(
        select(Attendance).where(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date == today
            )
        )
    ).scalar_one_or_none()
    
    if not attendance:
        raise NotFoundError("No check-in record found for today")
    
    if attendance.check_out_time:
        raise ValidationError("Already checked out today")
    
    attendance.check_out_time = datetime.utcnow()
    attendance.check_out_latitude = data.latitude
    attendance.check_out_longitude = data.longitude
    attendance.check_out_device = data.device_info
    
    if data.work_description:
        attendance.work_description = data.work_description
    
    # Calculate work hours
    work_hours = _calculate_work_hours(attendance.check_in_time, attendance.check_out_time)
    
    # Check if shift exists and calculate overtime
    shift = _get_current_shift(db, employee_id, today)
    if shift and work_hours > shift.total_working_hours:
        attendance.overtime_hours = round(work_hours - shift.total_working_hours, 2)
    
    db.flush()
    return attendance


def create_attendance(db: Session, attendance_data: AttendanceCreate) -> Attendance:
    """Create attendance record manually"""
    # Check for existing record
    existing = db.execute(
        select(Attendance).where(
            and_(
                Attendance.employee_id == attendance_data.employee_id,
                Attendance.date == attendance_data.date
            )
        )
    ).scalar_one_or_none()
    
    if existing:
        raise DuplicateError("Attendance record already exists for this date")
    
    attendance = Attendance(**attendance_data.model_dump())
    db.add(attendance)
    db.flush()
    return attendance


def get_attendance_by_id(db: Session, attendance_id: int) -> Optional[Attendance]:
    """Get attendance by ID"""
    return db.get(Attendance, attendance_id)


def get_employee_attendance(
    db: Session,
    employee_id: int,
    date_range: DateRange
) -> List[Attendance]:
    """Get attendance records for an employee within date range"""
    return db.execute(
        select(Attendance)
        .where(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= date_range.start_date,
                Attendance.date <= date_range.end_date
            )
        )
        .order_by(Attendance.date.desc())
    ).scalars().all()


def get_all_attendance(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[AttendanceStatus] = None
) -> List[Attendance]:
    """Get all attendance records with filters"""
    query = select(Attendance).options(joinedload(Attendance.employee))
    
    if employee_id:
        query = query.where(Attendance.employee_id == employee_id)
    
    if start_date:
        query = query.where(Attendance.date >= start_date)
    
    if end_date:
        query = query.where(Attendance.date <= end_date)
    
    if status:
        query = query.where(Attendance.status == status)
    
    query = query.order_by(Attendance.date.desc()).offset(skip).limit(limit)
    return db.execute(query).scalars().all()


def update_attendance(db: Session, attendance_id: int, updates: AttendanceUpdate) -> Attendance:
    """Update attendance record"""
    attendance = db.get(Attendance, attendance_id)
    
    if not attendance:
        raise NotFoundError("Attendance record not found")
    
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(attendance, field, value)
    
    db.flush()
    return attendance


def delete_attendance(db: Session, attendance_id: int) -> None:
    """Delete attendance record"""
    attendance = db.get(Attendance, attendance_id)
    
    if not attendance:
        raise NotFoundError("Attendance record not found")
    
    db.delete(attendance)
    db.flush()


def get_attendance_summary(
    db: Session,
    employee_id: int,
    year: int,
    month: int
) -> AttendanceSummary:
    """Get attendance summary for an employee for a specific month"""
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])
    
    attendances = get_employee_attendance(
        db, employee_id, DateRange(start_date=start_date, end_date=end_date)
    )
    
    employee = db.get(Employee, employee_id)
    if not employee:
        raise NotFoundError("Employee not found")
    
    summary = {
        "employee_id": employee_id,
        "employee_name": f"{employee.user.first_name} {employee.user.last_name}",
        "employee_code": employee.employee_code,
        "total_present": 0,
        "total_absent": 0,
        "total_late": 0,
        "total_half_days": 0,
        "total_leaves": 0,
        "total_overtime_hours": 0,
        "total_working_days": 0,
        "attendance_percentage": 0
    }
    
    for att in attendances:
        summary["total_overtime_hours"] += att.overtime_hours or 0
        
        if att.status == AttendanceStatus.PRESENT:
            summary["total_present"] += 1
        elif att.status == AttendanceStatus.ABSENT:
            summary["total_absent"] += 1
        elif att.status == AttendanceStatus.LATE:
            summary["total_late"] += 1
        elif att.status == AttendanceStatus.HALF_DAY:
            summary["total_half_days"] += 1
        elif att.status == AttendanceStatus.ON_LEAVE:
            summary["total_leaves"] += 1
    
    total_days = calendar.monthrange(year, month)[1]
    working_days = total_days - len([a for a in attendances if a.status in [AttendanceStatus.WEEKEND, AttendanceStatus.HOLIDAY]])
    
    summary["total_working_days"] = working_days
    if working_days > 0:
        present_days = summary["total_present"] + summary["total_late"] + summary["total_half_days"] * 0.5
        summary["attendance_percentage"] = round((present_days / working_days) * 100, 2)
    
    return AttendanceSummary(**summary)


# Leave Request Services
def create_leave_request(db: Session, leave_data: LeaveRequestCreate) -> LeaveRequest:
    """Create a new leave request"""
    # Check for overlapping leaves
    overlapping = db.execute(
        select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == leave_data.employee_id,
                LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
                or_(
                    and_(
                        leave_data.start_date <= LeaveRequest.end_date,
                        leave_data.end_date >= LeaveRequest.start_date
                    )
                )
            )
        )
    ).first()
    
    if overlapping:
        raise ValidationError("Leave request overlaps with existing leave")
    
    # Calculate total days
    total_days = (leave_data.end_date - leave_data.start_date).days + 1
    
    leave_request = LeaveRequest(
        **leave_data.model_dump(),
        total_days=total_days
    )
    
    db.add(leave_request)
    db.flush()
    return leave_request


def get_leave_request(db: Session, leave_id: int) -> Optional[LeaveRequest]:
    """Get leave request by ID"""
    return db.get(LeaveRequest, leave_id)


def get_employee_leave_requests(
    db: Session,
    employee_id: int,
    status: Optional[LeaveStatus] = None
) -> List[LeaveRequest]:
    """Get leave requests for an employee"""
    query = select(LeaveRequest).where(LeaveRequest.employee_id == employee_id)
    
    if status:
        query = query.where(LeaveRequest.status == status)
    
    query = query.order_by(LeaveRequest.created_at.desc())
    return db.execute(query).scalars().all()


def get_pending_leave_requests(db: Session) -> List[LeaveRequest]:
    """Get all pending leave requests"""
    return db.execute(
        select(LeaveRequest)
        .where(LeaveRequest.status == LeaveStatus.PENDING)
        .order_by(LeaveRequest.created_at)
    ).scalars().all()


def approve_leave_request(
    db: Session,
    leave_id: int,
    approver_id: int,
    decision: LeaveRequestApprove
) -> LeaveRequest:
    """Approve or reject a leave request"""
    leave_request = db.get(LeaveRequest, leave_id)
    
    if not leave_request:
        raise NotFoundError("Leave request not found")
    
    if leave_request.status != LeaveStatus.PENDING:
        raise ValidationError(f"Leave request is already {leave_request.status.value}")
    
    if decision.approved:
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by = approver_id
        leave_request.approved_at = datetime.utcnow()
        leave_request.comments = decision.comments
    else:
        leave_request.status = LeaveStatus.REJECTED
        leave_request.rejection_reason = decision.rejection_reason
        leave_request.comments = decision.comments
    
    db.flush()
    return leave_request


def update_leave_request(db: Session, leave_id: int, updates: LeaveRequestUpdate) -> LeaveRequest:
    """Update leave request"""
    leave_request = db.get(LeaveRequest, leave_id)
    
    if not leave_request:
        raise NotFoundError("Leave request not found")
    
    if leave_request.status != LeaveStatus.PENDING:
        raise ValidationError("Cannot update non-pending leave request")
    
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(leave_request, field, value)
    
    # Recalculate total days if dates changed
    if updates.start_date or updates.end_date:
        start = updates.start_date or leave_request.start_date
        end = updates.end_date or leave_request.end_date
        leave_request.total_days = (end - start).days + 1
    
    db.flush()
    return leave_request


def cancel_leave_request(db: Session, leave_id: int) -> None:
    """Cancel leave request"""
    leave_request = db.get(LeaveRequest, leave_id)
    
    if not leave_request:
        raise NotFoundError("Leave request not found")
    
    if leave_request.status != LeaveStatus.PENDING:
        raise ValidationError("Cannot cancel non-pending leave request")
    
    leave_request.status = LeaveStatus.CANCELLED
    db.flush()


def get_leave_balance(db: Session, employee_id: int, year: int) -> LeaveBalance:
    """Calculate leave balance for an employee"""
    # This is a simplified version - actual implementation depends on company policy
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # Get all approved leaves in the year
    leaves = db.execute(
        select(LeaveRequest)
        .where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status == LeaveStatus.APPROVED,
                LeaveRequest.start_date >= start_date,
                LeaveRequest.end_date <= end_date
            )
        )
    ).scalars().all()
    
    # Calculate totals by type (simplified - actual limits depend on policy)
    leave_totals = {
        LeaveType.CASUAL: 0,
        LeaveType.SICK: 0,
        LeaveType.EARNED: 0,
        LeaveType.MATERNITY: 0,
        LeaveType.PATERNITY: 0,
        LeaveType.COMP_OFF: 0,
    }
    
    total_taken = 0
    for leave in leaves:
        leave_totals[leave.leave_type] += leave.total_days
        total_taken += leave.total_days
    
    # Get employee
    employee = db.get(Employee, employee_id)
    if not employee:
        raise NotFoundError("Employee not found")
    
    # Calculate remaining (simplified - actual limits depend on policy)
    return LeaveBalance(
        employee_id=employee_id,
        employee_name=f"{employee.user.first_name} {employee.user.last_name}",
        employee_code=employee.employee_code,
        casual_leave=max(12 - leave_totals[LeaveType.CASUAL], 0),
        sick_leave=max(10 - leave_totals[LeaveType.SICK], 0),
        earned_leave=max(15 - leave_totals[LeaveType.EARNED], 0),
        maternity_leave=max(180 - leave_totals[LeaveType.MATERNITY], 0) if leave_totals[LeaveType.MATERNITY] > 0 else 180,
        paternity_leave=max(15 - leave_totals[LeaveType.PATERNITY], 0) if leave_totals[LeaveType.PATERNITY] > 0 else 15,
        comp_off=leave_totals[LeaveType.COMP_OFF],  # Comp off is earned, not allocated
        total_taken=total_taken,
        total_remaining=0  # Calculate based on policy
    )


# Holiday Services
def create_holiday(db: Session, holiday_data: HolidayCreate) -> Holiday:
    """Create a new holiday"""
    # Check for existing holiday on same date
    existing = db.execute(
        select(Holiday).where(
            and_(
                Holiday.date == holiday_data.date,
                Holiday.location == holiday_data.location
            )
        )
    ).scalar_one_or_none()
    
    if existing:
        raise DuplicateError("Holiday already exists for this date")
    
    holiday = Holiday(
        **holiday_data.model_dump(),
        year=holiday_data.date.year
    )
    
    db.add(holiday)
    db.flush()
    return holiday


def get_holiday(db: Session, holiday_id: int) -> Optional[Holiday]:
    """Get holiday by ID"""
    return db.get(Holiday, holiday_id)


def get_holidays_by_year(
    db: Session,
    year: int,
    location: Optional[str] = None
) -> List[Holiday]:
    """Get all holidays for a specific year"""
    query = select(Holiday).where(Holiday.year == year)
    
    if location:
        query = query.where(
            or_(
                Holiday.location == location,
                Holiday.location.is_(None)
            )
        )
    
    query = query.order_by(Holiday.date)
    return db.execute(query).scalars().all()


def update_holiday(db: Session, holiday_id: int, updates: HolidayUpdate) -> Holiday:
    """Update holiday"""
    holiday = db.get(Holiday, holiday_id)
    
    if not holiday:
        raise NotFoundError("Holiday not found")
    
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(holiday, field, value)
    
    if updates.date:
        holiday.year = updates.date.year
    
    db.flush()
    return holiday


def delete_holiday(db: Session, holiday_id: int) -> None:
    """Delete holiday"""
    holiday = db.get(Holiday, holiday_id)
    
    if not holiday:
        raise NotFoundError("Holiday not found")
    
    db.delete(holiday)
    db.flush()


# Work Shift Services
def create_work_shift(db: Session, shift_data: WorkShiftCreate) -> WorkShift:
    """Create a new work shift"""
    # Check for existing shift with same name
    existing = db.execute(
        select(WorkShift).where(WorkShift.name == shift_data.name)
    ).scalar_one_or_none()
    
    if existing:
        raise DuplicateError("Shift with this name already exists")
    
    shift = WorkShift(**shift_data.model_dump())
    db.add(shift)
    db.flush()
    return shift


def get_work_shift(db: Session, shift_id: int) -> Optional[WorkShift]:
    """Get work shift by ID"""
    return db.get(WorkShift, shift_id)


def get_all_work_shifts(db: Session, active_only: bool = True) -> List[WorkShift]:
    """Get all work shifts"""
    query = select(WorkShift)
    
    if active_only:
        query = query.where(WorkShift.is_active == True)
    
    return db.execute(query).scalars().all()


def update_work_shift(db: Session, shift_id: int, updates: WorkShiftUpdate) -> WorkShift:
    """Update work shift"""
    shift = db.get(WorkShift, shift_id)
    
    if not shift:
        raise NotFoundError("Work shift not found")
    
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(shift, field, value)
    
    db.flush()
    return shift


def delete_work_shift(db: Session, shift_id: int) -> None:
    """Delete work shift"""
    shift = db.get(WorkShift, shift_id)
    
    if not shift:
        raise NotFoundError("Work shift not found")
    
    # Check if shift is assigned to any employees
    assignments = db.execute(
        select(EmployeeShift).where(EmployeeShift.shift_id == shift_id)
    ).first()
    
    if assignments:
        raise ValidationError("Cannot delete shift assigned to employees")
    
    db.delete(shift)
    db.flush()


# Employee Shift Assignment
def assign_shift_to_employee(db: Session, assignment: EmployeeShiftAssign) -> EmployeeShift:
    """Assign a shift to an employee"""
    # Check for overlapping assignments
    overlapping = db.execute(
        select(EmployeeShift).where(
            and_(
                EmployeeShift.employee_id == assignment.employee_id,
                or_(
                    and_(
                        assignment.effective_from <= EmployeeShift.effective_to,
                        assignment.effective_to >= EmployeeShift.effective_from
                    )
                )
            )
        )
    ).first()
    
    if overlapping:
        raise ValidationError("Shift assignment overlaps with existing assignment")
    
    employee_shift = EmployeeShift(**assignment.model_dump())
    db.add(employee_shift)
    db.flush()
    return employee_shift


def get_employee_current_shift(db: Session, employee_id: int) -> Optional[EmployeeShift]:
    """Get current shift assignment for an employee"""
    today = date.today()
    
    return db.execute(
        select(EmployeeShift)
        .where(
            and_(
                EmployeeShift.employee_id == employee_id,
                EmployeeShift.effective_from <= today,
                or_(
                    EmployeeShift.effective_to.is_(None),
                    EmployeeShift.effective_to >= today
                )
            )
        )
        .order_by(EmployeeShift.effective_from.desc())
    ).scalar_one_or_none()


def get_employee_shift_history(db: Session, employee_id: int) -> List[EmployeeShift]:
    """Get shift assignment history for an employee"""
    return db.execute(
        select(EmployeeShift)
        .where(EmployeeShift.employee_id == employee_id)
        .order_by(EmployeeShift.effective_from.desc())
    ).scalars().all()


def end_shift_assignment(db: Session, assignment_id: int, end_date: date) -> EmployeeShift:
    """End a shift assignment"""
    assignment = db.get(EmployeeShift, assignment_id)
    
    if not assignment:
        raise NotFoundError("Shift assignment not found")
    
    assignment.effective_to = end_date
    db.flush()
    return assignment