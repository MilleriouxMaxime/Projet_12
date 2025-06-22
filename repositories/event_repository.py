from sqlalchemy.orm import Session
from models import Event, Contract, Client, Employee
from typing import List, Optional
from datetime import datetime


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, event_data: dict) -> Event:
        """Create a new event."""
        event = Event(**event_data)
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Get an event by its ID."""
        return self.session.query(Event).filter(Event.id == event_id).first()

    def get_all(self) -> List[Event]:
        """Get all events."""
        return self.session.query(Event).all()

    def get_by_contract(self, contract_id: int) -> List[Event]:
        """Get all events for a specific contract."""
        return self.session.query(Event).filter(Event.contract_id == contract_id).all()

    def get_by_client(self, client_id: int) -> List[Event]:
        """Get all events for a specific client."""
        return self.session.query(Event).filter(Event.client_id == client_id).all()

    def get_by_support(self, support_id: int) -> List[Event]:
        """Get all events assigned to a specific support employee."""
        return self.session.query(Event).filter(Event.support_id == support_id).all()

    def update(self, event_id: int, event_data: dict) -> Optional[Event]:
        """Update an event."""
        event = self.get_by_id(event_id)
        if event:
            for key, value in event_data.items():
                setattr(event, key, value)
            self.session.commit()
            self.session.refresh(event)
        return event

    def delete(self, event_id: int) -> bool:
        """Delete an event."""
        event = self.get_by_id(event_id)
        if event:
            self.session.delete(event)
            self.session.commit()
            return True
        return False

    def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Get a contract by ID."""
        return self.session.query(Contract).filter(Contract.id == contract_id).first()

    def get_client(self, client_id: int) -> Optional[Client]:
        """Get a client by ID."""
        return self.session.query(Client).filter(Client.id == client_id).first()

    def get_support(self, support_id: int) -> Optional[Employee]:
        """Get a support employee by ID."""
        return self.session.query(Employee).filter(Employee.id == support_id).first()
