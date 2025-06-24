"""Database models and data access layer for MusicTool."""

from .config import (
    DatabaseConfig,
    db_session_scope,
    get_database_config,
    get_db_session,
    initialize_database,
)
from .database import (
    Base,
    DigitalTrack,
    ImportBatch,
    PhysicalTrack,
    Release,
    Track,
)
from .repositories import (
    DigitalTrackRepository,
    ImportBatchRepository,
    PhysicalTrackRepository,
    ReleaseRepository,
    RepositoryManager,
    TrackRepository,
)

__all__ = [
    # Database models
    "Base",
    "Track",
    "DigitalTrack",
    "PhysicalTrack",
    "Release",
    "ImportBatch",
    # Configuration
    "DatabaseConfig",
    "initialize_database",
    "get_database_config",
    "get_db_session",
    "db_session_scope",
    # Repositories
    "TrackRepository",
    "DigitalTrackRepository",
    "PhysicalTrackRepository",
    "ReleaseRepository",
    "ImportBatchRepository",
    "RepositoryManager",
]
