import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from commands.event_commands import event
from models import Department, Event, Contract, Client, Employee
from datetime import datetime, UTC


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def mock_contract_repository(mock_session):
    """Create a mock contract repository."""
    repository = Mock()
    repository.get_by_commercial.return_value = [
        Contract(
            id=1,
            client_id=1,
            commercial_id=1,
            total_amount=1000.00,
            remaining_amount=500.00,
            is_signed=True,
            created_at=datetime.now(UTC),
        )
    ]
    return repository


@pytest.fixture
def mock_repository(mock_session):
    """Create a mock event repository."""
    repository = Mock()
    repository.get_by_id.return_value = Event(
        id=1,
        contract_id=1,
        client_id=1,
        support_id=1,
        name="Test Event",
        start_date=datetime.now(UTC),
        end_date=datetime.now(UTC),
        location="Test Location",
        attendees=10,
        notes="Test Notes",
    )
    repository.create.return_value = Event(
        id=1,
        contract_id=1,
        client_id=1,
        support_id=1,
        name="Test Event",
        start_date=datetime.now(UTC),
        end_date=datetime.now(UTC),
        location="Test Location",
        attendees=10,
        notes="Test Notes",
    )
    repository.update.return_value = Event(
        id=1,
        contract_id=1,
        client_id=1,
        support_id=1,
        name="Updated Event",
        start_date=datetime.now(UTC),
        end_date=datetime.now(UTC),
        location="Updated Location",
        attendees=20,
        notes="Updated Notes",
    )
    repository.get_all.return_value = [
        Event(
            id=1,
            contract_id=1,
            client_id=1,
            support_id=1,
            name="Test Event",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC),
            location="Test Location",
            attendees=10,
            notes="Test Notes",
        )
    ]
    repository.get_by_contract.return_value = [
        Event(
            id=1,
            contract_id=1,
            client_id=1,
            support_id=1,
            name="Test Event",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC),
            location="Test Location",
            attendees=10,
            notes="Test Notes",
        )
    ]
    repository.get_contract.return_value = Contract(
        id=1,
        client_id=1,
        commercial_id=1,
        total_amount=1000.00,
        remaining_amount=500.00,
        is_signed=True,
        created_at=datetime.now(UTC),
    )
    repository.get_client.return_value = Client(
        id=1, full_name="Test Client", email="test@example.com"
    )
    repository.get_support.return_value = Employee(
        id=1,
        employee_number="EMP001",
        full_name="Test Support",
        email="support@example.com",
        department=Department.SUPPORT,
        role="Support",
    )
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


class TestEventCommands:
    """Test event management commands."""

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_create_event_success(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test successful event creation."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(
            event,
            [
                "create",
                "--contract-id",
                "1",
                "--client-id",
                "1",
                "--support-id",
                "1",
                "--name",
                "Test Event",
                "--start-date",
                "2024-03-20 10:00",
                "--end-date",
                "2024-03-20 12:00",
                "--location",
                "Test Location",
                "--attendees",
                "10",
                "--notes",
                "Test Notes",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Successfully created event 'Test Event' for client Test Client"
            in result.output
        )
        mock_repository.create.assert_called_once()

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_create_event_unauthorized(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test event creation with unauthorized user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service
        mock_auth_service.has_permission.return_value = False

        result = runner.invoke(
            event,
            [
                "create",
                "--contract-id",
                "1",
                "--client-id",
                "1",
                "--support-id",
                "1",
                "--name",
                "Test Event",
                "--start-date",
                "2024-03-20 10:00",
                "--end-date",
                "2024-03-20 12:00",
                "--location",
                "Test Location",
                "--attendees",
                "10",
                "--notes",
                "Test Notes",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Only commercial users can create events" in result.output
        mock_repository.create.assert_not_called()

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_create_event_unsigned_contract(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test event creation for unsigned contract."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_contract.return_value = Contract(
            id=1,
            client_id=1,
            commercial_id=1,
            total_amount=1000.00,
            remaining_amount=500.00,
            is_signed=False,
            created_at=datetime.now(UTC),
        )

        result = runner.invoke(
            event,
            [
                "create",
                "--contract-id",
                "1",
                "--client-id",
                "1",
                "--support-id",
                "1",
                "--name",
                "Test Event",
                "--start-date",
                "2024-03-20 10:00",
                "--end-date",
                "2024-03-20 12:00",
                "--location",
                "Test Location",
                "--attendees",
                "10",
                "--notes",
                "Test Notes",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Cannot create event for unsigned contract" in result.output
        mock_repository.create.assert_not_called()

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_update_event_success(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test successful event update."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(
            event,
            [
                "update",
                "--event-id",
                "1",
                "--name",
                "Updated Event",
                "--location",
                "Updated Location",
                "--attendees",
                "20",
                "--notes",
                "Updated Notes",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully updated event 1" in result.output
        mock_repository.update.assert_called_once()

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_update_event_wrong_commercial(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test event update by wrong commercial user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_contract.return_value = Contract(
            id=1,
            client_id=1,
            commercial_id=2,  # Different from current user's ID
            total_amount=1000.00,
            remaining_amount=500.00,
            is_signed=True,
            created_at=datetime.now(UTC),
        )

        # Mock AuthService to simulate a commercial user
        mock_auth_service.get_current_user.return_value = Employee(
            id=2,
            employee_number="EMP002",
            full_name="Commercial User",
            email="commercial@example.com",
            department=Department.COMMERCIAL,
            role="Sales",
        )
        mock_auth_service.has_permission.side_effect = (
            lambda dept: dept == Department.COMMERCIAL
        )

        result = runner.invoke(
            event, ["update", "--event-id", "1", "--name", "Updated Event"]
        )

        assert result.exit_code == 0
        assert (
            "Error: Only management or support users can update events" in result.output
        )
        mock_repository.update.assert_not_called()

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_list_events_success(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test successful event listing."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(event, ["list"])

        assert result.exit_code == 0
        assert "Event ID: 1" in result.output
        assert "Name: Test Event" in result.output
        assert "Contract ID: 1" in result.output
        assert "Client ID: 1" in result.output
        assert "Support ID: 1" in result.output
        assert "Location: Test Location" in result.output
        assert "Attendees: 10" in result.output
        assert "Notes: Test Notes" in result.output

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_list_events_empty(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test event listing with no events."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_all.return_value = []
        mock_repository.get_by_contract.return_value = []
        mock_repository.get_by_client.return_value = []
        mock_repository.get_by_support.return_value = []
        mock_repository.get_without_support.return_value = []

        result = runner.invoke(event, ["list"])

        assert result.exit_code == 0
        assert "No events found" in result.output

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_list_events_without_support(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test listing events without support."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service
        mock_auth_service.get_current_user.return_value = Employee(
            id=1,
            employee_number="EMP001",
            full_name="Test Management",
            email="management@example.com",
            department=Department.MANAGEMENT,
            role="Manager",
        )
        mock_repository.get_without_support.return_value = [
            Event(
                id=1,
                contract_id=1,
                client_id=1,
                support_id=None,
                name="Test Event",
                start_date=datetime.now(UTC),
                end_date=datetime.now(UTC),
                location="Test Location",
                attendees=10,
                notes="Test Notes",
            )
        ]

        result = runner.invoke(event, ["list", "--without-support"])

        assert result.exit_code == 0
        assert "Event ID: 1" in result.output
        assert "Support ID: None" in result.output
        mock_repository.get_without_support.assert_called_once()

    @patch("commands.event_commands.DatabaseConnection.get_session")
    @patch("commands.event_commands.EventRepository")
    @patch("commands.event_commands.ContractRepository")
    @patch("commands.event_commands.AuthService")
    def test_list_my_events_support(
        self,
        mock_auth,
        mock_contract_repo_class,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_contract_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test listing events assigned to support user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_contract_repo_class.return_value = mock_contract_repository
        mock_auth.return_value = mock_auth_service
        mock_auth_service.get_current_user.return_value = Employee(
            id=1,
            employee_number="EMP001",
            full_name="Test Support",
            email="support@example.com",
            department=Department.SUPPORT,
            role="Support",
        )
        mock_repository.get_by_support.return_value = [
            Event(
                id=1,
                contract_id=1,
                client_id=1,
                support_id=1,
                name="Test Event",
                start_date=datetime.now(UTC),
                end_date=datetime.now(UTC),
                location="Test Location",
                attendees=10,
                notes="Test Notes",
            )
        ]

        result = runner.invoke(event, ["list", "--my-events"])

        assert result.exit_code == 0
        assert "Event ID: 1" in result.output
        assert "Support ID: 1" in result.output
        mock_repository.get_by_support.assert_called_once_with(1)
