from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rbac import require_roles, get_current_user
from app.modules.employee import services
from app.modules.employee.schemas import (
    EmployeeCreate, EmployeeOut, EmployeeDetailOut, 
    EmployeeUpdate, DepartmentCreate, DepartmentOut,
    DepartmentUpdate, DesignationCreate, DesignationOut,
    DesignationUpdate
)

router = APIRouter(prefix="/emp", tags=["Employee"])


# Employee endpoints
@router.post("/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new employee"""
    try:
        employee = services.create_employee_service(db, payload)
        db.commit()
        return employee
    except services.NotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.DuplicateError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/employees/{employee_id}", response_model=EmployeeDetailOut)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Get employee by ID"""
    try:
        employee = services.get_employee_by_id(db, employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return employee
    except services.EmployeeServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/employees", response_model=List[EmployeeDetailOut])
def get_all_employees(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all employees with optional filters"""
    try:
        return services.get_all_employees(
            db=db,
            skip=offset, 
            limit=limit, 
            department_id=department_id,
            is_active=is_active
        )
    except services.EmployeeServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int, 
    payload: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """Update employee information with all available fields"""
    try:
        employee = services.update_employee(db, employee_id, payload)
        db.commit()
        return employee
    except services.NotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.DuplicateError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    

    
@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Soft delete employee"""
    try:
        services.delete_employee(db, employee_id)
        db.commit()
        return None
    except services.NotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Department endpoints
@router.post("/departments", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new department"""
    try:
        department = services.create_department_service(db, payload)
        db.commit()
        return department
    except services.DuplicateError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/departments", response_model=List[DepartmentOut])
def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all departments"""
    try:
        departments = services.list_departments(db, skip=skip, limit=limit)
        
        # Add employee count
        result = []
        for dept in departments:
            dept_dict = {
                "id": dept.id,
                "name": dept.name,
                "description": dept.description,
                "created_at": dept.created_at,
                "updated_at": dept.updated_at,
                "employee_count": dept.employees.count() if hasattr(dept, 'employees') else 0
            }
            result.append(DepartmentOut.model_validate(dept_dict))
        
        return result
    except services.EmployeeServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/departments/{department_id}", response_model=DepartmentOut)
def get_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Get department by ID"""
    try:
        department = services.get_department_by_id(db, department_id)
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        
        dept_dict = {
            "id": department.id,
            "name": department.name,
            "description": department.description,
            "created_at": department.created_at,
            "updated_at": department.updated_at,
            "employee_count": department.employees.count() if hasattr(department, 'employees') else 0
        }
        return DepartmentOut.model_validate(dept_dict)
    except services.EmployeeServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/departments/{department_id}", response_model=DepartmentOut)
def update_department(
    department_id: int, 
    payload: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    """Update department information"""
    try:
        department = services.update_department(db, department_id, payload)
        db.commit()
        
        dept_dict = {
            "id": department.id,
            "name": department.name,
            "description": department.description,
            "created_at": department.created_at,
            "updated_at": department.updated_at,
            "employee_count": department.employees.count() if hasattr(department, 'employees') else 0
        }
        return DepartmentOut.model_validate(dept_dict)
    except services.NotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.DuplicateError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Delete department"""
    try:
        services.delete_department(db, department_id)
        db.commit()
        return None
    except services.NotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Designation endpoints
@router.post("/designations", response_model=DesignationOut, status_code=status.HTTP_201_CREATED)
def create_designation(
    payload: DesignationCreate,
    db: Session = Depends(get_db)
):
    """Create a new designation"""
    try:
        designation = services.create_designation_service(db, payload)
        db.commit()
        return designation
    except services.DuplicateError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/designations", response_model=List[DesignationOut])
def list_designations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all designations"""
    try:
        designations = services.list_designations(db, skip=skip, limit=limit)
        
        # Add employee count
        result = []
        for des in designations:
            des_dict = {
                "id": des.id,
                "title": des.title,
                "description": des.description,
                "created_at": des.created_at,
                "updated_at": des.updated_at,
                "employee_count": des.employees.count() if hasattr(des, 'employees') else 0
            }
            result.append(DesignationOut.model_validate(des_dict))
        
        return result
    except services.EmployeeServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/designations/{designation_id}", response_model=DesignationOut)
def get_designation(
    designation_id: int,
    db: Session = Depends(get_db)
):
    """Get designation by ID"""
    try:
        designation = services.get_designation_by_id(db, designation_id)
        if not designation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Designation not found")
        
        des_dict = {
            "id": designation.id,
            "title": designation.title,
            "description": designation.description,
            "created_at": designation.created_at,
            "updated_at": designation.updated_at,
            "employee_count": designation.employees.count() if hasattr(designation, 'employees') else 0
        }
        return DesignationOut.model_validate(des_dict)
    except services.EmployeeServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/designations/{designation_id}", response_model=DesignationOut)
def update_designation(
    designation_id: int, 
    payload: DesignationUpdate,
    db: Session = Depends(get_db)
):
    """Update designation information"""
    try:
        designation = services.update_designation(db, designation_id, payload)
        db.commit()
        
        des_dict = {
            "id": designation.id,
            "title": designation.title,
            "description": designation.description,
            "created_at": designation.created_at,
            "updated_at": designation.updated_at,
            "employee_count": designation.employees.count() if hasattr(designation, 'employees') else 0
        }
        return DesignationOut.model_validate(des_dict)
    except services.NotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.DuplicateError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/designations/{designation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_designation(
    designation_id: int,
    db: Session = Depends(get_db)
):
    """Delete designation"""
    try:
        services.delete_designation(db, designation_id)
        db.commit()
        return None
    except services.NotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.EmployeeServiceError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")