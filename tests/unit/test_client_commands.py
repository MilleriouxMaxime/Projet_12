import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from commands.client_commands import client
from models import Department, Client, Employee
from datetime import datetime, UTC


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def mock_repository(mock_session):
    """Create a mock client repository."""
    repository = Mock()
    repository.get_by_id.return_value = Client(
        id=1,
        full_name="Test Client",
        email="test@example.com",
        phone="1234567890",
        company_name="Test Company",
        commercial_id=1,
        created_at=datetime.now(UTC),
    )
    repository.get_by_email.return_value = None
    repository.create.return_value = Client(
        id=1,
        full_name="Test Client",
        email="test@example.com",
        phone="1234567890",
        company_name="Test Company",
        commercial_id=1,
        created_at=datetime.now(UTC),
    )
    repository.update.return_value = Client(
        id=1,
        full_name="Updated Client",
        email="test@example.com",
        phone="0987654321",
        company_name="Updated Company",
        commercial_id=1,
        created_at=datetime.now(UTC),
    )
    repository.get_by_commercial.return_value = [
        Client(
            id=1,
            full_name="Test Client",
            email="test@example.com",
            phone="1234567890",
            company_name="Test Company",
            commercial_id=1,
            created_at=datetime.now(UTC),
        )
    ]
    return repository


@pytest.fixture
def mock_auth_service():
    """Create a mock auth service."""
    auth_service = Mock()
    auth_service.has_permission.return_value = True
    auth_service.get_current_user.return_value = Employee(
        id=1,
        employee_number="EMP001",
        full_name="Test Commercial",
        email="commercial@example.com",
        department=Department.COMMERCIAL,
        role="Sales",
    )
    return auth_service


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


class TestClientCommands:
    """Test client management commands."""

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_create_client_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test successful client creation."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(
            client,
            [
                "create",
                "--full-name",
                "Test Client",
                "--email",
                "test@example.com",
                "--phone",
                "1234567890",
                "--company-name",
                "Test Company",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully created client: Test Client" in result.output
        mock_repository.create.assert_called_once()

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_create_client_unauthorized(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test client creation with unauthorized user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth_service.has_permission.return_value = False
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(
            client,
            ["create", "--full-name", "Test Client", "--email", "test@example.com"],
        )

        assert result.exit_code == 0
        assert "Error: Only commercial users can create clients" in result.output
        mock_repository.create.assert_not_called()

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_create_client_duplicate_email(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test client creation with duplicate email."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_by_email.return_value = Client(
            id=2, full_name="Existing Client", email="test@example.com", commercial_id=2
        )

        result = runner.invoke(
            client,
            ["create", "--full-name", "Test Client", "--email", "test@example.com"],
        )

        assert result.exit_code == 0
        assert (
            "Error: Client with email test@example.com already exists" in result.output
        )
        mock_repository.create.assert_not_called()

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_update_client_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test successful client update."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(
            client,
            [
                "update",
                "1",
                "--full-name",
                "Updated Client",
                "--phone",
                "0987654321",
                "--company-name",
                "Updated Company",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully updated client: Updated Client" in result.output
        mock_repository.update.assert_called_once()

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_update_client_not_found(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test client update with non-existent client."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_by_id.return_value = None

        result = runner.invoke(
            client, ["update", "999", "--full-name", "Updated Client"]
        )

        assert result.exit_code == 0
        assert "Error: Client with ID 999 not found" in result.output
        mock_repository.update.assert_not_called()

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_update_client_wrong_commercial(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test client update with wrong commercial."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_by_id.return_value = Client(
            id=1,
            full_name="Test Client",
            email="test@example.com",
            commercial_id=2,  # Different from current user's ID
        )

        result = runner.invoke(client, ["update", "1", "--full-name", "Updated Client"])

        assert result.exit_code == 0
        assert "Error: You can only update clients assigned to you" in result.output
        mock_repository.update.assert_not_called()

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_list_clients_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test successful client listing."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(client, ["list"])

        assert result.exit_code == 0
        assert "Client ID: 1" in result.output
        assert "Full Name: Test Client" in result.output
        assert "Email: test@example.com" in result.output
        assert "Phone: 1234567890" in result.output
        assert "Company: Test Company" in result.output
        mock_repository.get_by_commercial.assert_called_once()

    @patch("commands.client_commands.DatabaseConnection.get_session")
    @patch("commands.client_commands.ClientRepository")
    @patch("commands.client_commands.AuthService")
    def test_list_clients_empty(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test client listing with no clients."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_by_commercial.return_value = []

        result = runner.invoke(client, ["list"])

        assert result.exit_code == 0
        assert "No clients found" in result.output
        mock_repository.get_by_commercial.assert_called_once()
