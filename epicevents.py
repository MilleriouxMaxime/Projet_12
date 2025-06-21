import click
from auth import login, logout, require_auth, require_role


@click.group()
def cli():
    """EpicEvents CLI application."""
    pass


# Add authentication commands
cli.add_command(login)
cli.add_command(logout)


@cli.command()
@require_auth
def list_events(user_id, role):
    """List all events (requires authentication)."""
    click.echo(f"Listing events for user {user_id}...")
    # Add your event listing logic here


@cli.command()
@require_role("admin")
def create_event(user_id, role):
    """Create a new event (requires admin role)."""
    click.echo(f"Creating event as admin {user_id}...")
    # Add your event creation logic here


@cli.command()
@require_auth
def view_profile(user_id, role):
    """View user profile (requires authentication)."""
    click.echo(f"Viewing profile for user {user_id}...")
    # Add your profile viewing logic here


if __name__ == "__main__":
    cli()
