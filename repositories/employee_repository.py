from sqlalchemy.orm import Session
from models import Employee, Department
from datetime import datetime, UTC
import random
import string


class EmployeeRepository:
    def __init__(self, session: Session):
        self.session = session

    def generate_employee_number(self) -> str:
        """Generate a random employee number."""
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def get_by_email(self, email: str) -> Employee | None:
        """Get employee by email."""
        return self.session.query(Employee).filter_by(email=email).first()

    def get_all(self) -> list[Employee]:
        """Get all employees."""
        return self.session.query(Employee).all()

    def create(
        self,
        full_name: str,
        email: str,
        department: Department,
        role: str,
        password: str,
    ) -> Employee:
        """Create a new employee."""
        employee = Employee(
            employee_number=self.generate_employee_number(),
            full_name=full_name,
            email=email,
            department=department,
            role=role,
            created_at=datetime.now(UTC),
        )
        employee.password = password
        self.session.add(employee)
        self.session.commit()
        return employee

    def update(self, email: str, **kwargs) -> Employee | None:
        """Update an employee."""
        employee = self.get_by_email(email)
        if not employee:
            return None

        for key, value in kwargs.items():
            if hasattr(employee, key) and value is not None:
                if key == "department" and isinstance(value, str):
                    value = Department(value)
                setattr(employee, key, value)

        employee.updated_at = datetime.now(UTC)
        self.session.commit()
        return employee

    def delete(self, email: str) -> bool:
        """Delete an employee."""
        employee = self.get_by_email(email)
        if not employee:
            return False

        self.session.delete(employee)
        self.session.commit()
        return True

    def verify_credentials(
        self, email: str, password: str
    ) -> tuple[bool, Employee | None]:
        employee = self.get_by_email(email)
        if employee and employee.verify_password(password):
            return True, employee
        return False, None
