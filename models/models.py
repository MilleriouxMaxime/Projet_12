from datetime import datetime, UTC
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    Enum,
)
from sqlalchemy.orm import relationship, declarative_base
import enum
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class Department(enum.Enum):
    COMMERCIAL = "commercial"
    SUPPORT = "support"
    MANAGEMENT = "management"


class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)
    employee_number = Column(
        String, unique=True, nullable=False
    )  # Unique employee identifier
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    _password_hash = Column(
        "password", String, nullable=False
    )  # Renamed to indicate it's hashed
    department = Column(Enum(Department), nullable=False)
    role = Column(String, nullable=False)  # Specific role within department
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    clients = relationship("Client", back_populates="commercial")
    contracts = relationship("Contract", back_populates="commercial")
    events = relationship("Event", back_populates="support")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

    def has_permission(self, required_department):
        """Check if employee has permission based on department"""
        if self.department == Department.MANAGEMENT:
            return True
        return self.department == required_department


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    company_name = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    commercial_id = Column(Integer, ForeignKey("employee.id"))

    # Relationships
    commercial = relationship("Employee", back_populates="clients")
    contracts = relationship("Contract", back_populates="client")


class Contract(Base):
    __tablename__ = "contract"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("client.id"))
    commercial_id = Column(Integer, ForeignKey("employee.id"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    remaining_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    is_signed = Column(Boolean, default=False)

    # Relationships
    client = relationship("Client", back_populates="contracts")
    commercial = relationship("Employee", back_populates="contracts")
    events = relationship("Event", back_populates="contract")


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("contract.id"))
    support_id = Column(Integer, ForeignKey("employee.id"))
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)

    # Relationships
    contract = relationship("Contract", back_populates="events")
    support = relationship("Employee", back_populates="events")
