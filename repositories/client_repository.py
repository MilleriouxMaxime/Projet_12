from typing import List, Optional

from sqlalchemy.orm import Session

from models.models import Client, Employee


class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, client_data: dict) -> Client:
        """Create a new client."""
        client = Client(**client_data)
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get a client by ID."""
        return self.session.query(Client).filter(Client.id == client_id).first()

    def get_by_email(self, email: str) -> Optional[Client]:
        """Get a client by email."""
        return self.session.query(Client).filter(Client.email == email).first()

    def get_all(self) -> List[Client]:
        """Get all clients."""
        return self.session.query(Client).all()

    def get_by_commercial(self, commercial_id: int) -> List[Client]:
        """Get all clients for a specific commercial employee."""
        return (
            self.session.query(Client)
            .filter(Client.commercial_id == commercial_id)
            .all()
        )

    def update(self, client_id: int, client_data: dict) -> Optional[Client]:
        """Update a client."""
        client = self.get_by_id(client_id)
        if client:
            for key, value in client_data.items():
                setattr(client, key, value)
            self.session.commit()
            self.session.refresh(client)
        return client

    def delete(self, client_id: int) -> bool:
        """Delete a client."""
        client = self.get_by_id(client_id)
        if client:
            self.session.delete(client)
            self.session.commit()
            return True
        return False

    def get_commercial(self, commercial_id: int) -> Optional[Employee]:
        """Get a commercial employee by ID."""
        return self.session.query(Employee).filter(Employee.id == commercial_id).first()
