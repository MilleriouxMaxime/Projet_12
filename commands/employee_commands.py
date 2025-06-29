import click

from auth import AuthService
from database.connection import DatabaseConnection
from logging_config import log_employee_change, log_exception
from models import Department
from repositories.employee_repository import EmployeeRepository


@click.group()
def employee():
    """Employee management commands."""
    pass


@employee.command()
@click.option("--full-name", prompt="Full name", help="Employee full name")
@click.option("--email", prompt="Email", help="Employee email")
@click.option(
    "--department",
    type=click.Choice([d.value for d in Department]),
    prompt="Department",
    help="Employee department",
)
@click.option("--role", prompt="Role", help="Employee role")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Employee password",
)
def create(full_name, email, department, role, password):
    """Create a new employee."""
    try:
        auth_service = AuthService()
        if not auth_service.has_permission(Department.MANAGEMENT):
            click.echo("Error: Only management users can create employees")
            return

        with DatabaseConnection.get_session() as session:
            repository = EmployeeRepository(session)

            # Check if email already exists
            if repository.get_by_email(email):
                click.echo(f"Error: Employee with email {email} already exists.")
                return

            # Create new employee
            employee = repository.create(
                full_name=full_name,
                email=email,
                department=Department(department),
                role=role,
                password=password,
            )

            # Log employee creation
            log_employee_change(
                "created",
                {
                    "employee_number": employee.employee_number,
                    "full_name": employee.full_name,
                    "department": employee.department.value,
                    "role": employee.role,
                },
            )

            click.echo(f"Successfully created employee: {employee.full_name}")
    except Exception as e:
        log_exception(e, {"action": "create_employee", "email": email})
        click.echo(f"Error creating employee: {str(e)}")


@employee.command()
@click.option(
    "--email",
    prompt="Employee email",
    required=True,
    help="Email of the employee to update",
)
@click.option(
    "--full-name",
    prompt="New full name (press Enter to skip)",
    default="",
    help="New full name",
)
@click.option(
    "--department",
    type=click.Choice([d.value for d in Department] + [""]),
    prompt="New department (press Enter to skip)",
    default="",
    help="New department",
)
@click.option(
    "--role", prompt="New role (press Enter to skip)", default="", help="New role"
)
@click.option(
    "--password",
    prompt="New password (press Enter to skip)",
    default="",
    help="New password",
    hide_input=True,
)
def update(email, full_name, department, role, password):
    """Update an existing employee."""
    try:
        auth_service = AuthService()
        if not auth_service.has_permission(Department.MANAGEMENT):
            click.echo("Error: Only management users can update employees")
            return

        with DatabaseConnection.get_session() as session:
            repository = EmployeeRepository(session)

            # Préparer les données de mise à jour
            update_data = {}
            if full_name.strip():
                update_data["full_name"] = full_name
            if department.strip():
                update_data["department"] = department
            if role.strip():
                update_data["role"] = role
            if password.strip():
                update_data["password"] = password

            if not update_data:
                click.echo("Error: No update data provided")
                return

            # Mettre à jour l'employé
            employee = repository.update(email, **update_data)

            if not employee:
                click.echo(f"Error: Employee with email {email} not found.")
                return

            # Log employee update
            log_employee_change(
                "updated",
                {
                    "employee_number": employee.employee_number,
                    "full_name": employee.full_name,
                    "department": employee.department.value,
                    "role": employee.role,
                },
            )

            click.echo(f"Successfully updated employee: {employee.full_name}")
    except Exception as e:
        log_exception(e, {"action": "update_employee", "email": email})
        click.echo(f"Error updating employee: {str(e)}")


@employee.command()
@click.option(
    "--email",
    prompt="Employee email",
    required=True,
    help="Email of the employee to delete",
)
@click.confirmation_option(prompt="Are you sure you want to delete this employee?")
def delete(email):
    """Delete an employee."""
    try:
        auth_service = AuthService()
        if not auth_service.has_permission(Department.MANAGEMENT):
            click.echo("Error: Only management users can delete employees")
            return

        with DatabaseConnection.get_session() as session:
            repository = EmployeeRepository(session)

            # Get employee before deletion for logging
            employee = repository.get_by_email(email)
            if not employee:
                click.echo(f"Error: Employee with email {email} not found.")
                return

            if not repository.delete(email):
                click.echo(f"Error: Employee with email {email} not found.")
                return

            # Log employee deletion
            log_employee_change(
                "deleted",
                {
                    "employee_number": employee.employee_number,
                    "full_name": employee.full_name,
                    "department": employee.department.value,
                    "role": employee.role,
                },
            )

            click.echo(f"Successfully deleted employee: {email}")
    except Exception as e:
        log_exception(e, {"action": "delete_employee", "email": email})
        click.echo(f"Error deleting employee: {str(e)}")


@employee.command()
def list():
    """List all employees."""
    auth_service = AuthService()
    if not auth_service.get_current_user():
        click.echo("Error: Only authenticated users can list employees.")
        return
    with DatabaseConnection.get_session() as session:
        repository = EmployeeRepository(session)
        employees = repository.get_all()

        if not employees:
            click.echo("No employees found.")
            return

        for emp in employees:
            click.echo(f"\nEmployee ID: {emp.id}")
            click.echo(f"Employee: {emp.full_name}")
            click.echo(f"Email: {emp.email}")
            click.echo(f"Department: {emp.department.value}")
            click.echo(f"Role: {emp.role}")
            click.echo(f"Employee Number: {emp.employee_number}")
            click.echo("-" * 50)
