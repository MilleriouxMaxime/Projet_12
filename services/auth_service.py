from datetime import datetime, UTC, timedelta
import jwt
from pathlib import Path
from repositories.employee_repository import EmployeeRepository
from database.connection import DatabaseConnection
import click


class AuthService:
    def __init__(self):
        self.jwt_secret = "your-secret-key"  # Should be in environment variables
        self.jwt_algorithm = "HS256"
        self.token_expiry = timedelta(days=1)
        self.token_file = Path.home() / ".epicevents_token"

    def authenticate(self, email: str, password: str) -> tuple[bool, str | None]:
        with DatabaseConnection.get_session() as session:
            repository = EmployeeRepository(session)
            is_valid, employee = repository.verify_credentials(email, password)
            if is_valid and employee:
                token = self._generate_token(employee.id, employee.department.value)
                self._save_token(token)
                return True, employee.full_name
            return False, None

    def _generate_token(self, user_id: int, role: str) -> str:
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.now(UTC) + self.token_expiry,
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def _save_token(self, token: str) -> None:
        self.token_file.write_text(token)

    def logout(self) -> bool:
        if self.token_file.exists():
            self.token_file.unlink()
            return True
        return False

    def load_token(self) -> str | None:
        """Load the token from file."""
        if self.token_file.exists():
            return self.token_file.read_text()
        return None

    def verify_token(self, token: str) -> tuple[dict | None, str | None]:
        """Verify the JWT token and return the payload if valid.

        Returns:
            tuple: (payload, error_message)
            - If valid: (payload, None)
            - If expired: (None, "expired")
            - If invalid: (None, "invalid")
        """
        try:
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )
            return payload, None
        except jwt.ExpiredSignatureError:
            if self.token_file.exists():
                self.token_file.unlink()
            return None, "expired"
        except jwt.InvalidTokenError:
            if self.token_file.exists():
                self.token_file.unlink()
            return None, "invalid"
