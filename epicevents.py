import click
from auth import login, logout
from commands.employee_commands import employee
from commands.contract_commands import contract
from commands.client_commands import client


@click.group()
def cli():
    """EpicEvents CRM CLI application."""
    pass


# Authentication commands
cli.add_command(login)
cli.add_command(logout)

# Employee management commands
cli.add_command(employee)

# Contract management commands (only for management users)
cli.add_command(contract)

# Client management commands (only for commercial users)
cli.add_command(client)


if __name__ == "__main__":
    cli()
