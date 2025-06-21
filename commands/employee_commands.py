import click
from models import Employee, Department
from database.connection import DatabaseConnection
from repositories.employee_repository import EmployeeRepository
from datetime import datetime, UTC
import random
import string
from auth import require_role


@click.group()
@require_role(Department.MANAGEMENT.value)
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
        click.echo(f"Successfully created employee: {employee.full_name}")


@employee.command()
@click.argument("email")
@click.option("--full-name", help="New full name")
@click.option(
    "--department",
    type=click.Choice([d.value for d in Department]),
    help="New department",
)
@click.option("--role", help="New role")
@click.option("--password", help="New password", hide_input=True)
def update(email, full_name, department, role, password):
    """Update an existing employee."""
    with DatabaseConnection.get_session() as session:
        repository = EmployeeRepository(session)

        # Update employee
        employee = repository.update(
            email,
            full_name=full_name,
            department=department,
            role=role,
            password=password,
        )

        if not employee:
            click.echo(f"Error: Employee with email {email} not found.")
            return

        click.echo(f"Successfully updated employee: {employee.full_name}")


@employee.command()
@click.argument("email")
@click.confirmation_option(prompt="Are you sure you want to delete this employee?")
def delete(email):
    """Delete an employee."""
    with DatabaseConnection.get_session() as session:
        repository = EmployeeRepository(session)

        if not repository.delete(email):
            click.echo(f"Error: Employee with email {email} not found.")
            return

        click.echo(f"Successfully deleted employee: {email}")


@employee.command()
def list():
    """List all employees."""
    with DatabaseConnection.get_session() as session:
        repository = EmployeeRepository(session)
        employees = repository.get_all()

        if not employees:
            click.echo("No employees found.")
            return

        for emp in employees:
            click.echo(f"\nEmployee: {emp.full_name}")
            click.echo(f"Email: {emp.email}")
            click.echo(f"Department: {emp.department.value}")
            click.echo(f"Role: {emp.role}")
            click.echo(f"Employee Number: {emp.employee_number}")
            click.echo("-" * 50)
