import click

from auth import login, logout
from commands.client_commands import client
from commands.contract_commands import contract
from commands.employee_commands import employee
from commands.event_commands import event
from logging_config import init_sentry


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

# Event management commands (for commercial and management users)
cli.add_command(event)


if __name__ == "__main__":
    init_sentry()
    cli()
