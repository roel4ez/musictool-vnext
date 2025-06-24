"""Database configuration and connection management."""

import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .database import Base

# Default database configuration
DEFAULT_DATABASE_URL = "sqlite:///musictool.db"


class DatabaseConfig:
    """Database configuration settings."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", DEFAULT_DATABASE_URL
        )
        self.engine = create_engine(
            self.database_url,
            echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
            connect_args=(
                {"check_same_thread": False}
                if "sqlite" in self.database_url
                else {}
            ),
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database configuration instance
db_config: Optional[DatabaseConfig] = None


def initialize_database(database_url: Optional[str] = None) -> DatabaseConfig:
    """Initialize the global database configuration."""
    global db_config
    db_config = DatabaseConfig(database_url)
    db_config.create_tables()
    return db_config


def get_database_config() -> DatabaseConfig:
    """Get the global database configuration."""
    if db_config is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database() first."
        )
    return db_config


def get_db_session() -> Session:
    """Get a new database session."""
    return get_database_config().get_session()


@contextmanager
def db_session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    with get_database_config().session_scope() as session:
        yield session
