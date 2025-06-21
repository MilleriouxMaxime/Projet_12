import os
import jwt
import click
from datetime import datetime, UTC, timedelta
from pathlib import Path
from functools import wraps
from services.auth_service import AuthService


def require_auth(f):
    """Decorator to require authentication for a command."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_service = AuthService()
        token = auth_service.load_token()
        if not token:
            click.echo("You are not authenticated. Please login first.")
            return

        payload, error = auth_service.verify_token(token)
        if error == "expired":
            click.echo("Token has expired. Please login again.")
            return
        elif error == "invalid":
            click.echo("Invalid token. Please login again.")
            return
        elif not payload:
            return

        kwargs["user_id"] = payload["user_id"]
        kwargs["role"] = payload["role"]
        return f(*args, **kwargs)

    return decorated


def require_role(required_role):
    """Decorator to require specific role for a command."""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_service = AuthService()
            token = auth_service.load_token()
            if not token:
                click.echo("You are not authenticated. Please login first.")
                return

            payload, error = auth_service.verify_token(token)
            if error == "expired":
                click.echo("Token has expired. Please login again.")
                return
            elif error == "invalid":
                click.echo("Invalid token. Please login again.")
                return
            elif not payload:
                return

            if payload["role"] != required_role:
                click.echo(f"This command requires {required_role} role.")
                return

            kwargs["user_id"] = payload["user_id"]
            kwargs["role"] = payload["role"]
            return f(*args, **kwargs)

        return decorated

    return decorator


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
