import click
from datetime import datetime
from database.connection import DatabaseConnection
from repositories.event_repository import EventRepository
from models import Department
from auth import AuthService


@click.group()
def event():
    """Event management commands."""
    pass


@event.command()
@click.option("--contract-id", required=True, type=int, help="Contract ID")
@click.option("--client-id", required=True, type=int, help="Client ID")
@click.option("--support-id", required=True, type=int, help="Support employee ID")
@click.option("--name", required=True, help="Event name")
@click.option("--start-date", required=True, help="Event start date (YYYY-MM-DD HH:MM)")
@click.option("--end-date", required=True, help="Event end date (YYYY-MM-DD HH:MM)")
@click.option("--location", help="Event location")
@click.option("--attendees", type=int, help="Number of attendees")
@click.option("--notes", help="Event notes")
def create(
    contract_id: int,
    client_id: int,
    support_id: int,
    name: str,
    start_date: str,
    end_date: str,
    location: str = None,
    attendees: int = None,
    notes: str = None,
):
    """Create a new event."""
    auth_service = AuthService()
    if not (
        auth_service.has_permission(Department.COMMERCIAL)
        or auth_service.has_permission(Department.MANAGEMENT)
    ):
        click.echo("Error: Only commercial or management users can create events")
        return

    with DatabaseConnection.get_session() as session:
        repo = EventRepository(session)

        # Get current user
        current_user = auth_service.get_current_user()
        if not current_user:
            click.echo("Error: No authenticated user found")
            return

        # Verify contract exists and is signed
        contract = repo.get_contract(contract_id)
        if not contract:
            click.echo(f"Error: Contract with ID {contract_id} not found")
            return
        if not contract.is_signed:
            click.echo("Error: Cannot create event for unsigned contract")
            return

        # If commercial user, verify they own the contract
        if (
            current_user.department == Department.COMMERCIAL
            and contract.commercial_id != current_user.id
        ):
            click.echo("Error: You can only create events for your own contracts")
            return

        # Verify client exists
        client = repo.get_client(client_id)
        if not client:
            click.echo(f"Error: Client with ID {client_id} not found")
            return

        # Verify support employee exists and is in support department
        support = repo.get_support(support_id)
        if not support:
            click.echo(f"Error: Support employee with ID {support_id} not found")
            return
        if support.department != Department.SUPPORT:
            click.echo("Error: Employee must be from support department")
            return

        try:
            # Parse dates
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")

            event_data = {
                "contract_id": contract_id,
                "client_id": client_id,
                "support_id": support_id,
                "name": name,
                "start_date": start_datetime,
                "end_date": end_datetime,
                "location": location,
                "attendees": attendees,
                "notes": notes,
            }

            event = repo.create(event_data)
            click.echo(
                f"Successfully created event '{name}' for client {client.full_name}"
            )
        except ValueError:
            click.echo("Error: Invalid date format. Use YYYY-MM-DD HH:MM")
        except Exception as e:
            click.echo(f"Error creating event: {str(e)}")


@event.command()
@click.argument("event_id", type=int)
@click.option("--name", help="New event name")
@click.option("--start-date", help="New start date (YYYY-MM-DD HH:MM)")
@click.option("--end-date", help="New end date (YYYY-MM-DD HH:MM)")
@click.option("--location", help="New location")
@click.option("--attendees", type=int, help="New number of attendees")
@click.option("--notes", help="New notes")
def update(
    event_id: int,
    name: str = None,
    start_date: str = None,
    end_date: str = None,
    location: str = None,
    attendees: int = None,
    notes: str = None,
):
    """Update an existing event."""
    auth_service = AuthService()
    if not (
        auth_service.has_permission(Department.COMMERCIAL)
        or auth_service.has_permission(Department.MANAGEMENT)
    ):
        click.echo("Error: Only commercial or management users can update events")
        return

    with DatabaseConnection.get_session() as session:
        repo = EventRepository(session)

        # Get current user
        current_user = auth_service.get_current_user()
        if not current_user:
            click.echo("Error: No authenticated user found")
            return

        # Verify event exists
        event = repo.get_by_id(event_id)
        if not event:
            click.echo(f"Error: Event with ID {event_id} not found")
            return

        # If commercial user, verify they own the contract
        if current_user.department == Department.COMMERCIAL:
            contract = repo.get_contract(event.contract_id)
            if contract.commercial_id != current_user.id:
                click.echo("Error: You can only update events for your own contracts")
                return

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if start_date is not None:
            try:
                update_data["start_date"] = datetime.strptime(
                    start_date, "%Y-%m-%d %H:%M"
                )
            except ValueError:
                click.echo("Error: Invalid start date format. Use YYYY-MM-DD HH:MM")
                return
        if end_date is not None:
            try:
                update_data["end_date"] = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
            except ValueError:
                click.echo("Error: Invalid end date format. Use YYYY-MM-DD HH:MM")
                return
        if location is not None:
            update_data["location"] = location
        if attendees is not None:
            update_data["attendees"] = attendees
        if notes is not None:
            update_data["notes"] = notes

        if not update_data:
            click.echo("Error: No update data provided")
            return

        try:
            updated_event = repo.update(event_id, update_data)
            click.echo(f"Successfully updated event {event_id}")
        except Exception as e:
            click.echo(f"Error updating event: {str(e)}")


@event.command()
@click.option("--contract-id", type=int, help="Filter by contract ID")
@click.option("--client-id", type=int, help="Filter by client ID")
def list(contract_id: int = None, client_id: int = None):
    """List events with optional filters."""
    auth_service = AuthService()
    if not (
        auth_service.has_permission(Department.COMMERCIAL)
        or auth_service.has_permission(Department.MANAGEMENT)
    ):
        click.echo("Error: Only commercial or management users can list events")
        return

    with DatabaseConnection.get_session() as session:
        repo = EventRepository(session)

        # Get current user
        current_user = auth_service.get_current_user()
        if not current_user:
            click.echo("Error: No authenticated user found")
            return

        # Get events based on filters and user role
        if current_user.department == Department.COMMERCIAL:
            # Get all contracts for the commercial user
            contract_repo = ContractRepository(session)
            contracts = contract_repo.get_by_commercial(current_user.id)
            contract_ids = [c.id for c in contracts]

            # Filter events by contract IDs
            events = []
            for contract_id in contract_ids:
                events.extend(repo.get_by_contract(contract_id))
        else:  # Management user
            if contract_id:
                events = repo.get_by_contract(contract_id)
            elif client_id:
                events = repo.get_by_client(client_id)
            else:
                events = repo.get_all()

        if not events:
            click.echo("No events found")
            return

        for event in events:
            click.echo(f"\nEvent ID: {event.id}")
            click.echo(f"Name: {event.name}")
            click.echo(f"Contract ID: {event.contract_id}")
            click.echo(f"Client ID: {event.client_id}")
            click.echo(f"Support ID: {event.support_id}")
            click.echo(f"Start Date: {event.start_date}")
            click.echo(f"End Date: {event.end_date}")
            if event.location:
                click.echo(f"Location: {event.location}")
            if event.attendees:
                click.echo(f"Attendees: {event.attendees}")
            if event.notes:
                click.echo(f"Notes: {event.notes}")
            click.echo("-" * 50)
