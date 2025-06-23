from datetime import UTC, datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from commands.employee_commands import employee
from models import Department, Employee


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def mock_repository(mock_session):
    """Create a mock employee repository."""
    repository = Mock()
    repository.get_by_email.return_value = None
    repository.create.return_value = Employee(
        employee_number="TEST123",
        full_name="Test User",
        email="test@example.com",
        department=Department.COMMERCIAL,
        role="Test Role",
        created_at=datetime.now(UTC),
    )
    repository.update.return_value = Employee(
        employee_number="TEST123",
        full_name="Updated User",
        email="test@example.com",
        department=Department.SUPPORT,
        role="Updated Role",
        created_at=datetime.now(UTC),
    )
    repository.delete.return_value = True
    repository.get_all.return_value = [
        Employee(
            employee_number="TEST123",
            full_name="Test User",
            email="test@example.com",
            department=Department.COMMERCIAL,
            role="Test Role",
            created_at=datetime.now(UTC),
        )
    ]
    return repository


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


class TestEmployeeCommands:
    """Test employee management commands."""

    @patch("commands.employee_commands.DatabaseConnection.get_session")
    @patch("commands.employee_commands.EmployeeRepository")
    def test_create_employee_success(
        self, mock_repo_class, mock_get_session, runner, mock_repository, mock_session
    ):
        """Test successful employee creation."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository

        result = runner.invoke(
            employee,
            [
                "create",
                "--full-name",
                "Test User",
                "--email",
                "test@example.com",
                "--department",
                "commercial",
                "--role",
                "Test Role",
                "--password",
                "Password123!",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully created employee: Test User" in result.output
        mock_repository.create.assert_called_once()

    @patch("commands.employee_commands.DatabaseConnection.get_session")
    @patch("commands.employee_commands.EmployeeRepository")
    def test_create_employee_duplicate_email(
        self, mock_repo_class, mock_get_session, runner, mock_repository, mock_session
    ):
        """Test employee creation with duplicate email."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_repository.get_by_email.return_value = Employee(
            employee_number="EXIST123",
            full_name="Existing User",
            email="test@example.com",
            department=Department.COMMERCIAL,
            role="Existing Role",
            created_at=datetime.now(UTC),
        )

        result = runner.invoke(
            employee,
            [
                "create",
                "--full-name",
                "Test User",
                "--email",
                "test@example.com",
                "--department",
                "commercial",
                "--role",
                "Test Role",
                "--password",
                "Password123!",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Employee with email test@example.com already exists"
            in result.output
        )
        mock_repository.create.assert_not_called()

    @patch("commands.employee_commands.DatabaseConnection.get_session")
    @patch("commands.employee_commands.EmployeeRepository")
    def test_update_employee_success(
        self, mock_repo_class, mock_get_session, runner, mock_repository, mock_session
    ):
        """Test successful employee update."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository

        result = runner.invoke(
            employee,
            [
                "update",
                "--email",
                "test@example.com",
                "--full-name",
                "Updated User",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully updated employee: Updated User" in result.output
        mock_repository.update.assert_called_once()

    @patch("commands.employee_commands.DatabaseConnection.get_session")
    @patch("commands.employee_commands.EmployeeRepository")
    def test_update_employee_not_found(
        self, mock_repo_class, mock_get_session, runner, mock_repository, mock_session
    ):
        """Test employee update with non-existent email."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_repository.update.return_value = None

        result = runner.invoke(
            employee,
            [
                "update",
                "--email",
                "nonexistent@example.com",
                "--full-name",
                "Updated User",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Employee with email nonexistent@example.com not found"
            in result.output
        )

    @patch("commands.employee_commands.DatabaseConnection.get_session")
    @patch("commands.employee_commands.EmployeeRepository")
    def test_delete_employee_not_found(
        self, mock_repo_class, mock_get_session, runner, mock_repository, mock_session
    ):
        """Test employee deletion with non-existent email."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_repository.delete.return_value = False

        result = runner.invoke(
            employee,
            [
                "delete",
                "--email",
                "nonexistent@example.com",
            ],
            input="y\n",
        )

        assert result.exit_code == 0
        assert (
            "Error: Employee with email nonexistent@example.com not found"
            in result.output
        )

    @patch("commands.employee_commands.DatabaseConnection.get_session")
    @patch("commands.employee_commands.EmployeeRepository")
    @patch("commands.employee_commands.AuthService")
    def test_list_employees_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test successful employee listing."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository

        # Mock AuthService to return a current user
        mock_auth_instance = Mock()
        mock_auth_instance.get_current_user.return_value = Employee(
            employee_number="EMP001",
            full_name="Test User",
            email="test@example.com",
            department=Department.COMMERCIAL,
            role="Test Role",
            created_at=datetime.now(UTC),
        )
        mock_auth.return_value = mock_auth_instance

        result = runner.invoke(employee, ["list"])

        assert result.exit_code == 0
        assert "Employee: Test User" in result.output
        assert "Email: test@example.com" in result.output
        assert "Department: commercial" in result.output
        assert "Role: Test Role" in result.output
        assert "Employee Number: TEST123" in result.output
        mock_repository.get_all.assert_called_once()

    @patch("commands.employee_commands.DatabaseConnection.get_session")
    @patch("commands.employee_commands.EmployeeRepository")
    @patch("commands.employee_commands.AuthService")
    def test_list_employees_empty(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test employee listing with no employees."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_repository.get_all.return_value = []

        # Mock AuthService to return a current user
        mock_auth_instance = Mock()
        mock_auth_instance.get_current_user.return_value = Employee(
            employee_number="EMP001",
            full_name="Test User",
            email="test@example.com",
            department=Department.COMMERCIAL,
            role="Test Role",
            created_at=datetime.now(UTC),
        )
        mock_auth.return_value = mock_auth_instance

        result = runner.invoke(employee, ["list"])

        assert result.exit_code == 0
        assert "No employees found" in result.output
        mock_repository.get_all.assert_called_once()
