from sqlalchemy.orm import Session
from models import Employee


class EmployeeRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> Employee:
        return self.session.query(Employee).filter(Employee.email == email).first()

    def verify_credentials(
        self, email: str, password: str
    ) -> tuple[bool, Employee | None]:
        employee = self.find_by_email(email)
        if employee and employee.verify_password(password):
            return True, employee
        return False, None
