from decimal import Decimal

import click

from auth import AuthService
from database.connection import DatabaseConnection
from logging_config import log_contract_signature, log_exception
from models import Department
from repositories.contract_repository import ContractRepository


@click.group()
def contract():
    """Contract management commands."""
    pass


@contract.command()
@click.option(
    "--client-id", prompt="Client ID", required=True, type=int, help="Client ID"
)
@click.option(
    "--commercial-id",
    prompt="Commercial employee ID",
    required=True,
    type=int,
    help="Commercial employee ID",
)
@click.option(
    "--total-amount",
    prompt="Total contract amount",
    required=True,
    help="Total contract amount",
)
@click.option(
    "--remaining-amount",
    prompt="Remaining amount to be paid",
    required=True,
    help="Remaining amount to be paid",
)
def create(
    client_id: int, commercial_id: int, total_amount: str, remaining_amount: str
):
    """Create a new contract."""
    try:
        auth_service = AuthService()
        if not auth_service.has_permission(Department.MANAGEMENT):
            click.echo("Error: Only management users can create contracts")
            return

        with DatabaseConnection.get_session() as session:
            repo = ContractRepository(session)

            # Verify client exists
            client = repo.get_client(client_id)
            if not client:
                click.echo(f"Error: Client with ID {client_id} not found")
                return

            # Verify commercial exists
            commercial = repo.get_commercial(commercial_id)
            if not commercial:
                click.echo(
                    f"Error: Commercial employee with ID {commercial_id} not found"
                )
                return

            contract_data = {
                "client_id": client_id,
                "commercial_id": commercial_id,
                "total_amount": Decimal(total_amount),
                "remaining_amount": Decimal(remaining_amount),
                "is_signed": False,
            }

            contract = repo.create(contract_data)
            click.echo(f"Successfully created contract for client {client.full_name}")
    except Exception as e:
        log_exception(
            e,
            {
                "action": "create_contract",
                "client_id": client_id,
                "commercial_id": commercial_id,
            },
        )
        click.echo(f"Error creating contract: {str(e)}")


@contract.command()
@click.option(
    "--contract-id",
    prompt="Contract ID",
    required=True,
    type=int,
    help="Contract ID of the contract to update",
)
@click.option(
    "--total-amount",
    prompt="New total amount (press Enter to skip)",
    default="",
    help="New total amount",
)
@click.option(
    "--remaining-amount",
    prompt="New remaining amount (press Enter to skip)",
    default="",
    help="New remaining amount",
)
@click.option(
    "--is-signed",
    prompt="Contract signed status (true/false, press Enter to skip)",
    default="",
    help="Contract signed status",
)
def update(
    contract_id: int,
    total_amount: str = "",
    remaining_amount: str = "",
    is_signed: str = "",
):
    """Update an existing contract."""
    try:
        auth_service = AuthService()
        if not (
            auth_service.has_permission(Department.MANAGEMENT)
            or auth_service.has_permission(Department.COMMERCIAL)
        ):
            click.echo(
                "Error: Only management or commercial users can update contracts"
            )
            return

        with DatabaseConnection.get_session() as session:
            repo = ContractRepository(session)

            # Get current user
            current_user = auth_service.get_current_user()
            if not current_user:
                click.echo("Error: No authenticated user found")
                return

            # Verify contract exists
            contract = repo.get_by_id(contract_id)
            if not contract:
                click.echo(f"Error: Contract with ID {contract_id} not found")
                return

            # If commercial user, verify they own the contract
            if (
                current_user.department == Department.COMMERCIAL
                and contract.commercial_id != current_user.id
            ):
                click.echo("Error: You can only update contracts assigned to you")
                return

            update_data = {}
            if total_amount.strip():
                try:
                    update_data["total_amount"] = Decimal(str(total_amount))
                except ValueError:
                    click.echo("Error: Invalid total amount format")
                    return
            if remaining_amount.strip():
                try:
                    update_data["remaining_amount"] = Decimal(str(remaining_amount))
                except ValueError:
                    click.echo("Error: Invalid remaining amount format")
                    return
            if is_signed.strip():
                if is_signed.lower() in ["true", "1", "yes"]:
                    update_data["is_signed"] = True
                elif is_signed.lower() in ["false", "0", "no"]:
                    update_data["is_signed"] = False
                else:
                    click.echo(
                        "Error: Invalid signed status. Use true/false, yes/no, or 1/0"
                    )
                    return

            if not update_data:
                click.echo("Error: No update data provided")
                return

            updated_contract = repo.update(contract_id, update_data)

            # Log contract signature if the contract was just signed
            if (
                "is_signed" in update_data
                and update_data["is_signed"]
                and not contract.is_signed
            ):
                log_contract_signature(
                    {
                        "id": updated_contract.id,
                        "client_id": updated_contract.client_id,
                        "total_amount": float(updated_contract.total_amount),
                    }
                )

            click.echo(f"Successfully updated contract {contract_id}")
    except Exception as e:
        log_exception(
            e,
            {
                "action": "update_contract",
                "contract_id": contract_id,
                "is_signed": is_signed,
            },
        )
        click.echo(f"Error updating contract: {str(e)}")


@contract.command()
@click.option("--unsigned", is_flag=True, help="Show only unsigned contracts")
@click.option(
    "--unpaid", is_flag=True, help="Show only contracts with remaining amount"
)
def list(unsigned: bool = False, unpaid: bool = False):
    """List contracts with optional filters."""
    try:
        auth_service = AuthService()
        if not (
            auth_service.has_permission(Department.MANAGEMENT)
            or auth_service.has_permission(Department.COMMERCIAL)
        ):
            click.echo("Error: Only management or commercial users can list contracts")
            return

        with DatabaseConnection.get_session() as session:
            repo = ContractRepository(session)

            # Get current user
            current_user = auth_service.get_current_user()
            if not current_user:
                click.echo("Error: No authenticated user found")
                return

            # Get contracts based on filters and user role
            if current_user.department == Department.COMMERCIAL:
                if unsigned:
                    contracts = repo.get_unsigned_contracts(current_user.id)
                elif unpaid:
                    contracts = repo.get_unpaid_contracts(current_user.id)
                else:
                    contracts = repo.get_by_commercial(current_user.id)
            else:  # Management user
                if unsigned:
                    contracts = repo.get_unsigned_contracts()
                elif unpaid:
                    contracts = repo.get_unpaid_contracts()
                else:
                    contracts = repo.get_all()

            if not contracts:
                click.echo("No contracts found")
                return

            for contract in contracts:
                click.echo(f"\nContract ID: {contract.id}")
                click.echo(f"Client ID: {contract.client_id}")
                click.echo(f"Commercial ID: {contract.commercial_id}")
                click.echo(f"Total Amount: {contract.total_amount}")
                click.echo(f"Remaining Amount: {contract.remaining_amount}")
                click.echo(f"Signed: {contract.is_signed}")
                click.echo(f"Created At: {contract.created_at}")
                click.echo("-" * 50)
    except Exception as e:
        log_exception(
            e, {"action": "list_contracts", "unsigned": unsigned, "unpaid": unpaid}
        )
        click.echo(f"Error listing contracts: {str(e)}")
