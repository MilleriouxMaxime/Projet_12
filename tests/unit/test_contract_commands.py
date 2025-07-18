import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from commands.contract_commands import contract
from models.models import Department, Contract, Client, Employee
from decimal import Decimal
from datetime import datetime, UTC


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def mock_repository(mock_session):
    """Create a mock contract repository."""
    repository = Mock()
    repository.get_by_id.return_value = Contract(
        id=1,
        client_id=1,
        commercial_id=1,
        total_amount=Decimal("1000.00"),
        remaining_amount=Decimal("500.00"),
        is_signed=False,
        created_at=datetime.now(UTC),
    )
    repository.create.return_value = Contract(
        id=1,
        client_id=1,
        commercial_id=1,
        total_amount=Decimal("1000.00"),
        remaining_amount=Decimal("500.00"),
        is_signed=False,
        created_at=datetime.now(UTC),
    )
    repository.update.return_value = Contract(
        id=1,
        client_id=1,
        commercial_id=1,
        total_amount=Decimal("2000.00"),
        remaining_amount=Decimal("1000.00"),
        is_signed=True,
        created_at=datetime.now(UTC),
    )
    repository.get_all.return_value = [
        Contract(
            id=1,
            client_id=1,
            commercial_id=1,
            total_amount=Decimal("1000.00"),
            remaining_amount=Decimal("500.00"),
            is_signed=False,
            created_at=datetime.now(UTC),
        )
    ]
    repository.get_by_commercial.return_value = [
        Contract(
            id=1,
            client_id=1,
            commercial_id=1,
            total_amount=Decimal("1000.00"),
            remaining_amount=Decimal("500.00"),
            is_signed=False,
            created_at=datetime.now(UTC),
        )
    ]
    repository.get_unsigned_contracts.return_value = [
        Contract(
            id=1,
            client_id=1,
            commercial_id=1,
            total_amount=Decimal("1000.00"),
            remaining_amount=Decimal("500.00"),
            is_signed=False,
            created_at=datetime.now(UTC),
        )
    ]
    repository.get_unpaid_contracts.return_value = [
        Contract(
            id=1,
            client_id=1,
            commercial_id=1,
            total_amount=Decimal("1000.00"),
            remaining_amount=Decimal("500.00"),
            is_signed=False,
            created_at=datetime.now(UTC),
        )
    ]
    repository.get_client.return_value = Client(
        id=1, full_name="Test Client", email="test@example.com"
    )
    repository.get_commercial.return_value = Employee(
        id=1,
        employee_number="EMP001",
        full_name="Test Commercial",
        email="commercial@example.com",
        department=Department.COMMERCIAL,
        role="Sales",
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


class TestContractCommands:
    """Test contract management commands."""

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_create_contract_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test successful contract creation."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "create",
                "--client-id",
                "1",
                "--commercial-id",
                "1",
                "--total-amount",
                "1000.00",
                "--remaining-amount",
                "500.00",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully created contract for client Test Client" in result.output
        mock_repository.create.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_create_contract_unauthorized(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract creation with unauthorized user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = False

        result = runner.invoke(
            contract,
            [
                "create",
                "--client-id",
                "1",
                "--commercial-id",
                "1",
                "--total-amount",
                "1000.00",
                "--remaining-amount",
                "500.00",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Only management users can create contracts" in result.output
        mock_repository.create.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_create_contract_invalid_total_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract creation with invalid total amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "create",
                "--client-id",
                "1",
                "--commercial-id",
                "1",
                "--total-amount",
                "invalid",
                "--remaining-amount",
                "500.00",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Invalid total amount format. Please enter a valid number"
            in result.output
        )
        mock_repository.create.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_create_contract_invalid_remaining_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract creation with invalid remaining amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "create",
                "--client-id",
                "1",
                "--commercial-id",
                "1",
                "--total-amount",
                "1000.00",
                "--remaining-amount",
                "invalid",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Invalid remaining amount format. Please enter a valid number"
            in result.output
        )
        mock_repository.create.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_create_contract_negative_total_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract creation with negative total amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "create",
                "--client-id",
                "1",
                "--commercial-id",
                "1",
                "--total-amount",
                "-1000.00",
                "--remaining-amount",
                "500.00",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Total amount must be greater than 0" in result.output
        mock_repository.create.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_create_contract_negative_remaining_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract creation with negative remaining amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "create",
                "--client-id",
                "1",
                "--commercial-id",
                "1",
                "--total-amount",
                "1000.00",
                "--remaining-amount",
                "-500.00",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Remaining amount cannot be negative" in result.output
        mock_repository.create.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_create_contract_remaining_greater_than_total(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract creation with remaining amount greater than total amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "create",
                "--client-id",
                "1",
                "--commercial-id",
                "1",
                "--total-amount",
                "1000.00",
                "--remaining-amount",
                "1500.00",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Remaining amount cannot be greater than total amount"
            in result.output
        )
        mock_repository.create.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test successful contract update."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository

        # Mock AuthService to return a current user
        mock_auth_instance = Mock()
        mock_auth_instance.has_permission.return_value = True
        mock_auth_instance.get_current_user.return_value = Employee(
            id=1,
            employee_number="EMP001",
            full_name="Test Commercial",
            email="commercial@example.com",
            department=Department.COMMERCIAL,
            role="Sales",
        )
        mock_auth.return_value = mock_auth_instance

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--total-amount",
                "2000.00",
                "--remaining-amount",
                "1000.00",
                "--is-signed",
                "true",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully updated contract 1" in result.output
        mock_repository.update.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_not_found(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract update with non-existent contract."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True
        mock_repository.get_by_id.return_value = None

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "999",
                "--total-amount",
                "2000.00",
                "--remaining-amount",
                "1000.00",
                "--is-signed",
                "false",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Contract with ID 999 not found" in result.output
        mock_repository.update.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_list_contracts_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test successful contract listing."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(contract, ["list"])

        assert result.exit_code == 0
        assert "Contract ID: 1" in result.output
        assert "Client ID: 1" in result.output
        assert "Commercial ID: 1" in result.output
        assert "Total Amount: 1000.00" in result.output
        assert "Remaining Amount: 500.00" in result.output
        assert "Signed: False" in result.output
        mock_repository.get_all.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_list_contracts_empty(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract listing with no contracts."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True
        mock_repository.get_all.return_value = []

        result = runner.invoke(contract, ["list"])

        assert result.exit_code == 0
        assert "No contracts found" in result.output
        mock_repository.get_all.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_commercial_success(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test successful contract update by commercial user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--total-amount",
                "2000.00",
                "--remaining-amount",
                "1000.00",
                "--is-signed",
                "true",
            ],
        )

        assert result.exit_code == 0
        assert "Successfully updated contract 1" in result.output
        mock_repository.update.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_wrong_commercial(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test contract update by wrong commercial user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service
        mock_repository.get_by_id.return_value = Contract(
            id=1,
            client_id=1,
            commercial_id=2,  # Different from current user's ID
            total_amount=Decimal("1000.00"),
            remaining_amount=Decimal("500.00"),
            is_signed=False,
            created_at=datetime.now(UTC),
        )

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--total-amount",
                "2000.00",
                "--remaining-amount",
                "1000.00",
                "--is-signed",
                "false",
            ],
        )

        assert result.exit_code == 0
        assert "Error: You can only update contracts assigned to you" in result.output
        mock_repository.update.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_list_contracts_unsigned(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test listing unsigned contracts."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(contract, ["list", "--unsigned"])

        assert result.exit_code == 0
        assert "Contract ID: 1" in result.output
        assert "Signed: False" in result.output
        mock_repository.get_unsigned_contracts.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_list_contracts_unpaid(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test listing unpaid contracts."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(contract, ["list", "--unpaid"])

        assert result.exit_code == 0
        assert "Contract ID: 1" in result.output
        assert "Remaining Amount: 500.00" in result.output
        mock_repository.get_unpaid_contracts.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_list_contracts_commercial(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
        mock_auth_service,
    ):
        """Test listing contracts for commercial user."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value = mock_auth_service

        result = runner.invoke(contract, ["list"])

        assert result.exit_code == 0
        assert "Contract ID: 1" in result.output
        assert "Commercial ID: 1" in result.output
        mock_repository.get_all.assert_called_once()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_invalid_total_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract update with invalid total amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--total-amount",
                "invalid",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Invalid total amount format. Please enter a valid number"
            in result.output
        )
        mock_repository.update.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_invalid_remaining_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract update with invalid remaining amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--remaining-amount",
                "invalid",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Invalid remaining amount format. Please enter a valid number"
            in result.output
        )
        mock_repository.update.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_negative_total_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract update with negative total amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--total-amount",
                "-1000.00",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Total amount must be greater than 0" in result.output
        mock_repository.update.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_negative_remaining_amount(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract update with negative remaining amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--remaining-amount",
                "-500.00",
            ],
        )

        assert result.exit_code == 0
        assert "Error: Remaining amount cannot be negative" in result.output
        mock_repository.update.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_remaining_greater_than_total(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract update with remaining amount greater than total amount."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--remaining-amount",
                "1500.00",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Remaining amount cannot be greater than total amount"
            in result.output
        )
        mock_repository.update.assert_not_called()

    @patch("commands.contract_commands.DatabaseConnection.get_session")
    @patch("commands.contract_commands.ContractRepository")
    @patch("commands.contract_commands.AuthService")
    def test_update_contract_both_amounts_remaining_greater_than_total(
        self,
        mock_auth,
        mock_repo_class,
        mock_get_session,
        runner,
        mock_repository,
        mock_session,
    ):
        """Test contract update with both amounts where remaining is greater than total."""
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_repo_class.return_value = mock_repository
        mock_auth.return_value.has_permission.return_value = True

        result = runner.invoke(
            contract,
            [
                "update",
                "--contract-id",
                "1",
                "--total-amount",
                "1000.00",
                "--remaining-amount",
                "1500.00",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Error: Remaining amount cannot be greater than total amount"
            in result.output
        )
        mock_repository.update.assert_not_called()
