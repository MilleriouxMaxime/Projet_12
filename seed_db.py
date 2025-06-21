from database.connection import DatabaseConnection
from models import Employee, Department
from datetime import datetime, UTC
import random
import string


def generate_employee_number():
    """Generate a random employee number."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_email(full_name):
    """Generate an email from full name."""
    name_parts = full_name.lower().split()
    return f"{name_parts[0]}.{name_parts[-1]}@epicevents.com"


def create_employees():
    """Create sample employees for each department."""
    employees = [
        # Commercial Department
        ("John Smith", Department.COMMERCIAL, "Senior Sales"),
        ("Emma Johnson", Department.COMMERCIAL, "Account Manager"),
        ("Michael Brown", Department.COMMERCIAL, "Sales Representative"),
        ("Sophia Davis", Department.COMMERCIAL, "Business Developer"),
        ("William Wilson", Department.COMMERCIAL, "Sales Manager"),
        # Support Department
        ("Olivia Taylor", Department.SUPPORT, "Senior Support"),
        ("James Anderson", Department.SUPPORT, "Technical Support"),
        ("Isabella Martinez", Department.SUPPORT, "Customer Success"),
        ("Benjamin Thompson", Department.SUPPORT, "Support Specialist"),
        ("Mia Garcia", Department.SUPPORT, "Support Manager"),
        # Management Department
        ("Lucas Robinson", Department.MANAGEMENT, "CEO"),
        ("Charlotte Clark", Department.MANAGEMENT, "CFO"),
        ("Henry Rodriguez", Department.MANAGEMENT, "CTO"),
        ("Amelia Lewis", Department.MANAGEMENT, "COO"),
        ("Sebastian Lee", Department.MANAGEMENT, "HR Director"),
    ]

    # Default password for all employees
    default_password = "Password123!"

    with DatabaseConnection.get_session() as session:
        for full_name, department, role in employees:
            employee = Employee(
                employee_number=generate_employee_number(),
                full_name=full_name,
                email=generate_email(full_name),
                department=department,
                role=role,
                created_at=datetime.now(UTC),
            )
            employee.password = default_password
            session.add(employee)

        session.commit()
        print(f"Created {len(employees)} employees")


if __name__ == "__main__":
    try:
        print("Starting database seeding...")
        create_employees()
        print("Database seeding complete!")
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        exit(1)
