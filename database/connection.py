import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.exc import OperationalError
import time


class DatabaseConnection:
    _instance = None
    _engine = None
    _Session = None

    @classmethod
    def _initialize(cls):
        if cls._Session is None:  # Only initialize if not already done
            DATABASE_URL = os.getenv(
                "DATABASE_URL",
                "sqlite:///epicevents.db",
            )
            # Add connection pool and timeout settings for SQLite
            cls._engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,  # Recycle connections after 1 hour
                connect_args={
                    "timeout": 30,  # Connection timeout in seconds for SQLite
                },
            )
            cls._Session = sessionmaker(bind=cls._engine)

    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        if cls._Session is None:
            cls._initialize()
        session = cls._Session()
        try:
            yield session
        finally:
            session.close()

    @classmethod
    def get_engine(cls):
        """Get the database engine, initializing it if necessary."""
        if cls._engine is None:
            cls._initialize()
        return cls._engine
