from database.connection import DatabaseConnection
from models.models import Base
from sqlalchemy import text
import time


def wait_for_db(engine, max_retries=5, delay=2):
    """Wait for database to be ready."""
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            if i == max_retries - 1:
                raise Exception(
                    f"Could not connect to database after {max_retries} attempts: {str(e)}"
                )
            print(f"Database not ready, retrying in {delay} seconds...")
            time.sleep(delay)
    return False


def init_db():
    """Initialize the database by creating all tables."""
    print("Initializing database connection...")
    db = DatabaseConnection()
    engine = db.get_engine()

    print("Waiting for database to be ready...")
    wait_for_db(engine)

    print("Creating tables...")
    Base.metadata.create_all(engine)

    # Verify tables were created (SQLite compatible)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print("\nCreated tables:")
        for table in sorted(tables):
            print(f"- {table}")


if __name__ == "__main__":
    try:
        print("Starting database initialization...")
        init_db()
        print("\nDatabase initialization complete!")
    except Exception as e:
        print(f"\nError initializing database: {str(e)}")
        exit(1)
