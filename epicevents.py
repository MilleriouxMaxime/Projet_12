import click
from auth import login, logout
from commands.employee_commands import employee


@click.group()
def cli():
    """EpicEvents CRM CLI application."""
    pass


# Authentication commands
cli.add_command(login)
cli.add_command(logout)

# Employee management commands
cli.add_command(employee)


if __name__ == "__main__":
    cli()
