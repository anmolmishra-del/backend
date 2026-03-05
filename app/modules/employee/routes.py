from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

# avoid module-level import to prevent circular imports
from app.core.rbac import require_roles
from fastapi.security import OAuth2PasswordBearer
from app.modules.employee.schemas import EmployeeCreate, EmployeeOut, EmployeeDetailOut, EmployeeListOut, EmployeeUpdate, DesignationCreate, DesignationOut, DepartmentCreate, DepartmentOut

router = APIRouter(prefix="/emp", tags=["Employee"])

@router.post("/employees", response_model=EmployeeOut)
def create_employee(payload: EmployeeCreate):
    from app.modules.employee.services import create_employee_service
    try:
        return create_employee_service(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/employees/{employee_id}", response_model=EmployeeDetailOut)
def get_employee(employee_id: int):
    # import inside the function to avoid circular import at module import time
    from app.modules.employee.services import get_employee_by_id

    employee = get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@router.get("/employees", response_model=EmployeeListOut)
def list_employees():
    from app.modules.employee.services import list_employees
    return list_employees()

@router.put("/employees/{employee_id}", response_model=EmployeeDetailOut)
def update_employee(employee_id: int, payload: EmployeeUpdate):
    from app.modules.employee.services import update_employee
    try:
        return update_employee(employee_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/departments", response_model=DepartmentOut)
def create_department(payload: DepartmentCreate):
    from app.modules.employee.services import create_department_service
    try:
        return create_department_service(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/departments/{department_id}", response_model=DepartmentOut)    
def update_department(department_id: int, payload: DepartmentCreate):
    from app.modules.employee.services import update_department
    try:
        return update_department(department_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/designations", response_model=DesignationOut)
def create_designation(payload: DesignationCreate):
    from app.modules.employee.services import create_designation_service
    try:
        return create_designation_service(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 
   

@router.put("/designations/{designation_id}", response_model=DesignationOut)    
def update_designation(designation_id: int, payload: DesignationCreate):
    from app.modules.employee.services import update_designation
    try:
        return update_designation(designation_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    from app.modules.employee.services import delete_employee
    try:
        delete_employee(employee_id)
        return {"detail": "Employee deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/departments/{department_id}")
def delete_department(department_id: int):  
    from app.modules.employee.services import delete_department
    try:
        delete_department(department_id)
        return {"detail": "Department deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    


@router.delete("/designations/{designation_id}")
def delete_designation(designation_id: int):    
    from app.modules.employee.services import delete_designation
    try:
        delete_designation(designation_id)
        return {"detail": "Designation deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))