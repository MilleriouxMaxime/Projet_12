import click

from services.auth_service import AuthService


@click.command()
@click.option("--email", prompt=True, help="Email for authentication")
@click.option(
    "--password", prompt=True, hide_input=True, help="Password for authentication"
)
def login(email, password):
    """Authenticate user and generate JWT token."""
    auth_service = AuthService()
    success, full_name = auth_service.authenticate(email, password)
    if success:
        click.echo(f"Successfully logged in as {full_name}!")
    else:
        click.echo("Invalid credentials!")


@click.command()
def logout():
    """Logout user by removing the token."""
    auth_service = AuthService()
    if auth_service.logout():
        click.echo("Successfully logged out!")
    else:
        click.echo("You are not logged in.")


if __name__ == "__main__":
    login()
