from typing import Optional, Dict, Any

from sqlalchemy import select

from app.modules.auth.models import User
from app.modules.employee.models import Employee, Department, Designation

# no OTP or random logic here; keep imports focused on the objects we actually use


def _resolve_fk(val, model):
    """Resolve a foreign key field which may be an integer id or a name string.

    Returns the integer id if found, otherwise None.
    """
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        # look up by name attribute
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(model).where(model.name == val)
            obj = session.execute(q).scalars().first()
            return obj.id if obj else None
        finally:
            session.close()


def _generate_employee_code(user_id: int) -> str:
    # simple deterministic code based on user id, padded to six digits
    return f"EMP{user_id:06d}"


def _employee_to_dict(db_emp) -> dict:
    # combine employee-specific fields with related user fields (via relationship)
    out = {
        "id": getattr(db_emp, "id", None),
        "user_id": getattr(db_emp, "user_id", None),
        "employee_code": getattr(db_emp, "employee_code", None),
        "position": getattr(db_emp, "position", None),
        "department_id": getattr(db_emp, "department_id", None),
        "designation_id": getattr(db_emp, "designation_id", None),
        "created_at": getattr(db_emp, "created_at", None),
        "updated_at": getattr(db_emp, "updated_at", None),
    }
    user = getattr(db_emp, "user", None)
    if user is not None:
        out.update({
            "first_name": getattr(user, "first_name", None),
            "last_name": getattr(user, "last_name", None),
            "email": getattr(user, "email", None),
            "username": getattr(user, "username", None),
            "phone_number": getattr(user, "phone_number", None),
        })
    return out


def _department_to_dict(db_dep) -> dict:
    return {
        "id": getattr(db_dep, "id", None),
        "name": getattr(db_dep, "name", None),
        "description": getattr(db_dep, "description", None),
        "created_at": getattr(db_dep, "created_at", None),
        "updated_at": getattr(db_dep, "updated_at", None),
    }


def _designation_to_dict(db_des) -> dict:
    return {
        "id": getattr(db_des, "id", None),
        "title": getattr(db_des, "title", None),
        "description": getattr(db_des, "description", None),
        "created_at": getattr(db_des, "created_at", None),
        "updated_at": getattr(db_des, "updated_at", None),
    }


def create_employee_service(employee) -> dict:
    # first create a user record using the auth module; employee payload should
    # include at least email and password (auth.schemas may enforce this).
    from app.modules.auth.services import create_user

    user_payload = employee
    q = select(User).where((User.email == getattr(user_payload, "email", None)) or (User.phone_number == getattr(user_payload, "phone_number", None)))
    user = session.execute(q).scalars().first()
    if not user:
        user = create_user(user_payload)
    user_id = user.get("id")

    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            # check for an existing employee record for this user
            q = select(Employee).where(Employee.user_id == user_id)
            existing = session.execute(q).scalars().first()
            if existing:
                raise ValueError("Employee record already exists for this user")

            dep_id = _resolve_fk(getattr(employee, "department", None), Department)
            desig_id = _resolve_fk(getattr(employee, "designation", None), Designation)

            new_employee = Employee(
                user_id=user_id,
                employee_code=_generate_employee_code(user_id),
                # employee-specific fields
                position=getattr(employee, "position", None),
                department_id=dep_id,
                designation_id=desig_id,
            )
            session.add(new_employee)
            session.commit()
            session.refresh(new_employee)
            # build output combining employee and user info (user dict from earlier)
            out = _employee_to_dict(new_employee)
            out.update({
                k: user.get(k) for k in (
                    "first_name",
                    "last_name",
                    "email",
                    "username",
                    "phone_number",
                )
            })
            return out
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to create employee: {e}") from e
    
def create_department_service(department) -> dict:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Department).where(Department.name == getattr(department, "name", None))
            existing = session.execute(q).scalars().first()
            if existing:
                raise ValueError("Department with this name already exists")

            new_department = Department(
                name=getattr(department, "name", None),
                description=getattr(department, "description", None)
            )
            session.add(new_department)
            session.commit()
            session.refresh(new_department)
            return _department_to_dict(new_department)
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to create department: {e}") from e

def create_designation_service(designation) -> dict:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Designation).where(Designation.title == getattr(designation, "title", None))
            existing = session.execute(q).scalars().first()
            if existing:
                raise ValueError("Designation with this title already exists")

            new_designation = Designation(
                title=getattr(designation, "title", None),
                description=getattr(designation, "description", None)
            )
            session.add(new_designation)
            session.commit()
            session.refresh(new_designation)
            return _designation_to_dict(new_designation)
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to create designation: {e}") from e
def get_employee_by_id(employee_id: int) -> Optional[Dict[str, Any]]:
    try:
        from app.core.database import SessionLocal
        from sqlalchemy.orm import joinedload
        session = SessionLocal()
        try:
            q = select(Employee).options(joinedload(Employee.user)).where(Employee.id == employee_id)
            employee = session.execute(q).scalars().first()
            if not employee:
                return None
            return _employee_to_dict(employee)
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to retrieve employee: {e}") from e    
    

def list_employees() -> list:
    try:
        from app.core.database import SessionLocal
        from sqlalchemy.orm import joinedload
        session = SessionLocal()
        try:
            q = select(Employee).options(joinedload(Employee.user))
            employees = session.execute(q).scalars().all()
            return [_employee_to_dict(emp) for emp in employees]
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to list employees: {e}") from e

def update_employee(employee_id: int, updates) -> dict:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Employee).where(Employee.id == employee_id)
            employee = session.execute(q).scalars().first()
            if not employee:
                raise ValueError("Employee not found")

            # update employee-specific scalar fields
            for field in ["position"]:
                if hasattr(updates, field) and getattr(updates, field) is not None:
                    setattr(employee, field, getattr(updates, field))

            # handle department/designation as before
            if hasattr(updates, "department") and getattr(updates, "department") is not None:
                employee.department_id = _resolve_fk(getattr(updates, "department"), Department)
            if hasattr(updates, "designation") and getattr(updates, "designation") is not None:
                employee.designation_id = _resolve_fk(getattr(updates, "designation"), Designation)

            # user-related updates: email, username, password, names, phone
            if user_id := getattr(employee, "user_id", None):
                from app.modules.auth.models import User as AuthUser
                q_user = select(AuthUser).where(AuthUser.id == user_id)
                user = session.execute(q_user).scalars().first()
                if user:
                    for field in ["first_name", "last_name", "email", "phone_number", "username"]:
                        if hasattr(updates, field) and getattr(updates, field) is not None:
                            setattr(user, field, getattr(updates, field))
                    if hasattr(updates, "password") and getattr(updates, "password") is not None:
                        from app.modules.auth.security import get_password_hash
                        user.hashed_password = get_password_hash(getattr(updates, "password"))

            # handle foreign keys via resolver
            if hasattr(updates, "department") and getattr(updates, "department") is not None:
                employee.department_id = _resolve_fk(getattr(updates, "department"), Department)
            if hasattr(updates, "designation") and getattr(updates, "designation") is not None:
                employee.designation_id = _resolve_fk(getattr(updates, "designation"), Designation)

            session.commit()
            session.refresh(employee)
            return _employee_to_dict(employee)
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to update employee: {e}") from e
    
def update_department(department_id: int, updates) -> dict:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Department).where(Department.id == department_id)
            department = session.execute(q).scalars().first()
            if not department:
                raise ValueError("Department not found")

            for field in ["name", "description"]:
                if hasattr(updates, field) and getattr(updates, field) is not None:
                    setattr(department, field, getattr(updates, field))

            session.commit()
            session.refresh(department)
            return _department_to_dict(department)
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to update department: {e}") from e
    

def update_designation(designation_id: int, updates) -> dict:
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Designation).where(Designation.id == designation_id)
            designation = session.execute(q).scalars().first()
            if not designation:
                raise ValueError("Designation not found")

            for field in ["title", "description"]:
                if hasattr(updates, field) and getattr(updates, field) is not None:
                    setattr(designation, field, getattr(updates, field))

            session.commit()
            session.refresh(designation)
            return _designation_to_dict(designation)
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to update designation: {e}") from e

def delete_employee(employee_id: int):
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Employee).where(Employee.id == employee_id)
            employee = session.execute(q).scalars().first()
            if not employee:
                raise ValueError("Employee not found")
            session.delete(employee)
            session.commit()
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to delete employee: {e}") from e
    
def delete_department(department_id: int):
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Department).where(Department.id == department_id)
            department = session.execute(q).scalars().first()
            if not department:
                raise ValueError("Department not found")
            session.delete(department)
            session.commit()
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to delete department: {e}") from e

def delete_designation(designation_id: int):    
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        try:
            q = select(Designation).where(Designation.id == designation_id)
            designation = session.execute(q).scalars().first()
            if not designation:
                raise ValueError("Designation not found")
            session.delete(designation)
            session.commit()
        finally:
            session.close()
    except Exception as e:
        raise ValueError(f"Failed to delete designation: {e}") from e