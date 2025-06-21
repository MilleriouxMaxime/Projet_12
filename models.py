from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # commercial, support, or management
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    clients = relationship("Client", back_populates="commercial")
    contracts = relationship("Contract", back_populates="commercial")
    events = relationship("Event", back_populates="support")


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
    events = relationship("Event", back_populates="client")


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
    client_id = Column(Integer, ForeignKey("client.id"))
    support_id = Column(Integer, ForeignKey("employee.id"))
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)

    # Relationships
    contract = relationship("Contract", back_populates="events")
    client = relationship("Client", back_populates="events")
    support = relationship("Employee", back_populates="events")
