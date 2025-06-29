#!/usr/bin/env python3
"""
Event seeding script for EpicEvents CRM
Creates sample clients, contracts, and events for testing
"""

from database.connection import DatabaseConnection
from models.models import Employee, Client, Contract, Event, Department
from datetime import datetime, UTC, timedelta
import random
import string


def generate_employee_number():
    """Generate a random employee number."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_email(full_name):
    """Generate an email from full name."""
    name_parts = full_name.lower().split()
    return f"{name_parts[0]}.{name_parts[-1]}@example.com"


def clean_database():
    """Clean all tables except employees."""
    with DatabaseConnection.get_session() as session:
        try:
            # Delete all events first (due to foreign key constraints)
            session.query(Event).delete()
            print("Cleaned events table")

            # Delete all contracts
            session.query(Contract).delete()
            print("Cleaned contracts table")

            # Delete all clients
            session.query(Client).delete()
            print("Cleaned clients table")

            session.commit()
            print("Database cleaned successfully")
        except Exception as e:
            session.rollback()
            print(f"Error cleaning database: {str(e)}")
            raise


def create_sample_data():
    """Create sample clients, contracts, and events."""

    with DatabaseConnection.get_session() as session:
        # Get existing employees
        commercial_employees = (
            session.query(Employee)
            .filter(Employee.department == Department.COMMERCIAL)
            .all()
        )

        support_employees = (
            session.query(Employee)
            .filter(Employee.department == Department.SUPPORT)
            .all()
        )

        if not commercial_employees:
            print("No commercial employees found. Please run seed_db.py first.")
            return

        if not support_employees:
            print("No support employees found. Please run seed_db.py first.")
            return

        print(f"Found {len(commercial_employees)} commercial employees")
        print(f"Found {len(support_employees)} support employees")

        # Create sample clients
        clients_data = [
            ("Acme Corporation", "john.doe@acme.com", "+1-555-0101", "Acme Corp"),
            ("TechStart Inc", "jane.smith@techstart.com", "+1-555-0102", "TechStart"),
            (
                "Global Solutions",
                "bob.wilson@globalsolutions.com",
                "+1-555-0103",
                "Global Solutions",
            ),
            (
                "Innovation Labs",
                "alice.brown@innovationlabs.com",
                "+1-555-0104",
                "Innovation Labs",
            ),
            (
                "Future Systems",
                "charlie.davis@futuresystems.com",
                "+1-555-0105",
                "Future Systems",
            ),
            (
                "Digital Dynamics",
                "diana.miller@digitaldynamics.com",
                "+1-555-0106",
                "Digital Dynamics",
            ),
            (
                "Smart Solutions",
                "edward.garcia@smartsolutions.com",
                "+1-555-0107",
                "Smart Solutions",
            ),
            (
                "NextGen Tech",
                "fiona.rodriguez@nextgentech.com",
                "+1-555-0108",
                "NextGen Tech",
            ),
        ]

        clients = []
        for full_name, email, phone, company_name in clients_data:
            # Assign random commercial employee
            commercial = random.choice(commercial_employees)

            client = Client(
                full_name=full_name,
                email=email,
                phone=phone,
                company_name=company_name,
                commercial_id=commercial.id,
                created_at=datetime.now(UTC),
            )
            session.add(client)
            clients.append(client)

        session.commit()
        print(f"Created {len(clients)} clients")

        # Create sample contracts
        contracts_data = [
            # Signed contracts (can have events)
            (10000.00, 0.00, True),  # Fully paid
            (15000.00, 5000.00, True),  # Partially paid
            (20000.00, 20000.00, True),  # Not paid
            (8000.00, 0.00, True),  # Fully paid
            (12000.00, 6000.00, True),  # Partially paid
            (18000.00, 9000.00, True),  # Partially paid
            (25000.00, 0.00, True),  # Fully paid
            (16000.00, 16000.00, True),  # Not paid
            (14000.00, 7000.00, True),  # Partially paid
            (22000.00, 0.00, True),  # Fully paid
            (19000.00, 19000.00, True),  # Not paid
            (11000.00, 5500.00, True),  # Partially paid
            (17000.00, 0.00, True),  # Fully paid
            (13000.00, 13000.00, True),  # Not paid
            # Unsigned contracts (cannot have events)
            (30000.00, 30000.00, False),
            (24000.00, 24000.00, False),
            (28000.00, 28000.00, False),
        ]

        contracts = []
        for total_amount, remaining_amount, is_signed in contracts_data:
            # Assign random client and commercial employee
            client = random.choice(clients)
            commercial = random.choice(commercial_employees)

            contract = Contract(
                client_id=client.id,
                commercial_id=commercial.id,
                total_amount=total_amount,
                remaining_amount=remaining_amount,
                is_signed=is_signed,
                created_at=datetime.now(UTC),
            )
            session.add(contract)
            contracts.append(contract)

        session.commit()
        print(f"Created {len(contracts)} contracts")

        # Create sample events
        events_data = [
            # Events with support assigned
            (
                "Annual Tech Conference",
                "2024-12-15 09:00",
                "2024-12-15 17:00",
                "Convention Center",
                150,
                "Annual technology conference for all clients",
            ),
            (
                "Product Launch Event",
                "2024-12-20 10:00",
                "2024-12-20 16:00",
                "Grand Hotel",
                80,
                "Launch of new product line",
            ),
            (
                "Client Workshop",
                "2024-12-25 14:00",
                "2024-12-25 18:00",
                "Office Building",
                30,
                "Hands-on workshop for clients",
            ),
            (
                "Networking Dinner",
                "2024-12-30 19:00",
                "2024-12-30 22:00",
                "Luxury Restaurant",
                50,
                "Annual networking dinner",
            ),
            (
                "Training Session",
                "2025-01-05 09:00",
                "2025-01-05 17:00",
                "Training Center",
                25,
                "Staff training session",
            ),
            (
                "Demo Day",
                "2025-01-10 13:00",
                "2025-01-10 17:00",
                "Showroom",
                40,
                "Product demonstration day",
            ),
            # Events without support assigned (for testing --without-support filter)
            (
                "Open House",
                "2025-01-15 10:00",
                "2025-01-15 16:00",
                "Main Office",
                60,
                "Open house event - support needed",
            ),
            (
                "Industry Meetup",
                "2025-01-20 18:00",
                "2025-01-20 21:00",
                "Community Center",
                35,
                "Industry networking meetup - support needed",
            ),
            (
                "Client Presentation",
                "2025-01-25 14:00",
                "2025-01-25 16:00",
                "Conference Room",
                20,
                "Client presentation - support needed",
            ),
            (
                "Team Building Event",
                "2025-01-30 09:00",
                "2025-01-30 17:00",
                "Outdoor Park",
                45,
                "Team building activities - support needed",
            ),
            (
                "Product Demo",
                "2025-02-05 14:00",
                "2025-02-05 16:00",
                "Client Office",
                15,
                "Product demonstration at client site - support needed",
            ),
            (
                "Annual Review Meeting",
                "2025-02-10 10:00",
                "2025-02-10 12:00",
                "Board Room",
                12,
                "Annual client review meeting - support needed",
            ),
            (
                "Technology Workshop",
                "2025-02-15 13:00",
                "2025-02-15 18:00",
                "Training Facility",
                28,
                "Advanced technology workshop - support needed",
            ),
            (
                "Client Onboarding",
                "2025-02-20 09:00",
                "2025-02-20 11:00",
                "Conference Room A",
                8,
                "New client onboarding session - support needed",
            ),
        ]

        events = []
        signed_contracts = [c for c in contracts if c.is_signed]

        for i, (name, start_date, end_date, location, attendees, notes) in enumerate(
            events_data
        ):
            # Only create events for signed contracts
            if i < len(signed_contracts):
                contract = signed_contracts[i]
                client = contract.client

                # For the first 6 events, assign support. For the rest, leave support as None
                support_id = None
                if i < 6:
                    support = random.choice(support_employees)
                    support_id = support.id

                # Parse dates
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")

                event = Event(
                    contract_id=contract.id,
                    support_id=support_id,
                    name=name,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    location=location,
                    attendees=attendees,
                    notes=notes,
                )
                session.add(event)
                events.append(event)

        session.commit()
        print(f"Created {len(events)} events")

        # Print summary
        print("\n" + "=" * 50)
        print("DATABASE SEEDING SUMMARY")
        print("=" * 50)
        print(f"Commercial employees: {len(commercial_employees)}")
        print(f"Support employees: {len(support_employees)}")
        print(f"Clients created: {len(clients)}")
        print(f"Contracts created: {len(contracts)}")
        print(f"  - Signed contracts: {len(signed_contracts)}")
        print(f"  - Unsigned contracts: {len(contracts) - len(signed_contracts)}")
        print(f"Events created: {len(events)}")
        print(
            f"  - Events with support: {len([e for e in events if e.support_id is not None])}"
        )
        print(
            f"  - Events without support: {len([e for e in events if e.support_id is None])}"
        )
        print("=" * 50)

        # Print test credentials
        print("\nTEST CREDENTIALS:")
        print("=" * 30)
        print("Management: lucas.robinson@epicevents.com / Password123!")
        print("Commercial: john.smith@epicevents.com / Password123!")
        print("Support: olivia.taylor@epicevents.com / Password123!")
        print("=" * 30)


if __name__ == "__main__":
    try:
        print("Starting event database seeding...")
        print("Cleaning existing data (preserving employees)...")
        clean_database()
        print("Creating sample data...")
        create_sample_data()
        print("Event database seeding complete!")
    except Exception as e:
        print(f"Error seeding event database: {str(e)}")
        import traceback

        traceback.print_exc()
        exit(1)
