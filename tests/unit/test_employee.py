import pytest
from models import Employee, Department
from werkzeug.security import check_password_hash


@pytest.fixture
def employee():
    """Fixture to create a test employee"""
    return Employee(
        employee_number="EMP001",
        full_name="Test User",
        email="test@example.com",
        department=Department.COMMERCIAL,
        role="Test Role",
    )


def test_password_hashing(employee):
    """Test that password is properly hashed when set"""
    test_password = "secure_password123"
    employee.password = test_password

    # Check that the stored password is hashed
    assert employee._password_hash != test_password
    assert check_password_hash(employee._password_hash, test_password)


def test_password_verification(employee):
    """Test password verification"""
    test_password = "secure_password123"
    employee.password = test_password

    # Test correct password
    assert employee.verify_password(test_password)

    # Test incorrect password
    assert not employee.verify_password("wrong_password")


def test_password_not_readable(employee):
    """Test that password is not directly readable"""
    test_password = "secure_password123"
    employee.password = test_password

    # Attempting to read password should raise AttributeError
    with pytest.raises(AttributeError):
        _ = employee.password


def test_password_update(employee):
    """Test that password can be updated"""
    initial_password = "initial_password"
    new_password = "new_password"

    employee.password = initial_password
    initial_hash = employee._password_hash

    employee.password = new_password

    # Check that hash has changed
    assert initial_hash != employee._password_hash
    # Check that new password works
    assert employee.verify_password(new_password)
    # Check that old password doesn't work
    assert not employee.verify_password(initial_password)


def test_password_hash_uniqueness(employee):
    """Test that different passwords generate different hashes"""
    employee.password = "password1"
    hash1 = employee._password_hash

    employee.password = "password2"
    hash2 = employee._password_hash

    assert hash1 != hash2
