from sqlalchemy.orm import Session
from models import Contract, Client, Employee
from typing import List, Optional


class ContractRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, contract_data: dict) -> Contract:
        """Create a new contract."""
        contract = Contract(**contract_data)
        self.session.add(contract)
        self.session.commit()
        self.session.refresh(contract)
        return contract

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        """Get a contract by its ID."""
        return self.session.query(Contract).filter(Contract.id == contract_id).first()

    def get_all(self) -> List[Contract]:
        """Get all contracts."""
        return self.session.query(Contract).all()

    def get_by_client(self, client_id: int) -> List[Contract]:
        """Get all contracts for a specific client."""
        return (
            self.session.query(Contract).filter(Contract.client_id == client_id).all()
        )

    def update(self, contract_id: int, contract_data: dict) -> Optional[Contract]:
        """Update a contract."""
        contract = self.get_by_id(contract_id)
        if contract:
            for key, value in contract_data.items():
                setattr(contract, key, value)
            self.session.commit()
            self.session.refresh(contract)
        return contract

    def delete(self, contract_id: int) -> bool:
        """Delete a contract."""
        contract = self.get_by_id(contract_id)
        if contract:
            self.session.delete(contract)
            self.session.commit()
            return True
        return False

    def get_client(self, client_id: int) -> Optional[Client]:
        """Get a client by ID."""
        return self.session.query(Client).filter(Client.id == client_id).first()

    def get_commercial(self, commercial_id: int) -> Optional[Employee]:
        """Get a commercial employee by ID."""
        return self.session.query(Employee).filter(Employee.id == commercial_id).first()
