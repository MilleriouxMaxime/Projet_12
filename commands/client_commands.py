import click

from auth import AuthService
from database.connection import DatabaseConnection
from models import Department
from repositories.client_repository import ClientRepository


@click.group()
def client():
    """Client management commands."""
    pass


@client.command()
@click.option(
    "--full-name", prompt="Client full name", required=True, help="Client full name"
)
@click.option("--email", prompt="Client email", required=True, help="Client email")
@click.option("--phone", prompt="Client phone number", help="Client phone number")
@click.option(
    "--company-name", prompt="Client company name", help="Client company name"
)
def create(full_name: str, email: str, phone: str = None, company_name: str = None):
    """Create a new client."""
    auth_service = AuthService()
    if not auth_service.has_permission(Department.COMMERCIAL):
        click.echo("Error: Only commercial users can create clients")
        return

    with DatabaseConnection.get_session() as session:
        repo = ClientRepository(session)

        # Check if client with email already exists
        existing_client = repo.get_by_email(email)
        if existing_client:
            click.echo(f"Error: Client with email {email} already exists")
            return

        # Get current user's ID for commercial_id
        current_user = auth_service.get_current_user()
        if not current_user:
            click.echo("Error: No authenticated user found")
            return

        client_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "company_name": company_name,
            "commercial_id": current_user.id,
        }

        try:
            client = repo.create(client_data)
            click.echo(f"Successfully created client: {client.full_name}")
        except Exception as e:
            click.echo(f"Error creating client: {str(e)}")


@client.command()
@click.option(
    "--client-id",
    prompt="Client ID",
    required=True,
    type=int,
    help="Client ID of the client to update",
)
@click.option(
    "--full-name",
    prompt="New full name (press Enter to skip)",
    default="",
    help="New full name",
)
@click.option(
    "--email", prompt="New email (press Enter to skip)", default="", help="New email"
)
@click.option(
    "--phone",
    prompt="New phone number (press Enter to skip)",
    default="",
    help="New phone number",
)
@click.option(
    "--company-name",
    prompt="New company name (press Enter to skip)",
    default="",
    help="New company name",
)
def update(
    client_id: int,
    full_name: str = "",
    email: str = "",
    phone: str = "",
    company_name: str = "",
):
    """Update an existing client."""
    auth_service = AuthService()
    if not auth_service.has_permission(Department.COMMERCIAL):
        click.echo("Error: Only commercial users can update clients")
        return

    with DatabaseConnection.get_session() as session:
        repo = ClientRepository(session)

        # Get current user
        current_user = auth_service.get_current_user()
        if not current_user:
            click.echo("Error: No authenticated user found")
            return

        # Verify client exists and belongs to current user
        client = repo.get_by_id(client_id)
        if not client:
            click.echo(f"Error: Client with ID {client_id} not found")
            return

        if client.commercial_id != current_user.id:
            click.echo("Error: You can only update clients assigned to you")
            return

        # Check if new email is already taken
        if email and email != client.email:
            existing_client = repo.get_by_email(email)
            if existing_client:
                click.echo(f"Error: Client with email {email} already exists")
                return

        update_data = {}
        if full_name.strip():
            update_data["full_name"] = full_name
        if email.strip():
            update_data["email"] = email
        if phone.strip():
            update_data["phone"] = phone
        if company_name.strip():
            update_data["company_name"] = company_name

        if not update_data:
            click.echo("Error: No update data provided")
            return

        try:
            updated_client = repo.update(client_id, update_data)
            click.echo(f"Successfully updated client: {updated_client.full_name}")
        except Exception as e:
            click.echo(f"Error updating client: {str(e)}")


@client.command()
def list():
    """List all clients assigned to the current commercial user."""
    auth_service = AuthService()
    if not auth_service.has_permission(Department.COMMERCIAL):
        click.echo("Error: Only commercial users can list clients")
        return

    with DatabaseConnection.get_session() as session:
        repo = ClientRepository(session)

        # Get current user
        current_user = auth_service.get_current_user()
        if not current_user:
            click.echo("Error: No authenticated user found")
            return

        clients = repo.get_by_commercial(current_user.id)

        if not clients:
            click.echo("No clients found")
            return

        for client in clients:
            click.echo(f"\nClient ID: {client.id}")
            click.echo(f"Full Name: {client.full_name}")
            click.echo(f"Email: {client.email}")
            click.echo(f"Phone: {client.phone or 'Not provided'}")
            click.echo(f"Company: {client.company_name or 'Not provided'}")
            click.echo(f"Created At: {client.created_at}")
            click.echo("-" * 50)
