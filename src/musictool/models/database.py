"""Database models for MusicTool."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Track(Base):
    """Core track entity representing a unique musical work."""

    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    artist = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    album = Column(String(255), nullable=True)
    label = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)  # Duration in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    digital_tracks = relationship(
        "DigitalTrack", back_populates="track", cascade="all, delete-orphan"
    )
    physical_tracks = relationship(
        "PhysicalTrack", back_populates="track", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Track(id={self.id}, artist='{self.artist}', title='{self.title}')>"

    @property
    def has_digital_format(self) -> bool:
        """Check if track has any digital formats."""
        return len(self.digital_tracks) > 0

    @property
    def has_physical_format(self) -> bool:
        """Check if track has any physical formats."""
        return len(self.physical_tracks) > 0


class DigitalTrack(Base):
    """Digital format instance of a track (e.g., from Traktor NML)."""

    __tablename__ = "digital_tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    file_path = Column(String(512), nullable=False)
    format = Column(String(10), nullable=False)  # mp3, flac, wav, etc.
    bitrate = Column(Integer, nullable=True)  # kbps
    source_file = Column(String(512), nullable=False)  # Original NML file path
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track", back_populates="digital_tracks")

    def __repr__(self) -> str:
        return (
            f"<DigitalTrack(id={self.id}, format='{self.format}', "
            f"file_path='{self.file_path}')>"
        )


class Release(Base):
    """Physical release information (album, EP, single, etc.)."""

    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discogs_id = Column(Integer, nullable=True, unique=True)  # Discogs release ID
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    label = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    format_type = Column(String(50), nullable=False)  # vinyl, cd, cassette, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    physical_tracks = relationship(
        "PhysicalTrack", back_populates="release", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Release(id={self.id}, title='{self.title}', "
            f"format='{self.format_type}')>"
        )


class PhysicalTrack(Base):
    """Physical format instance of a track on a specific release."""

    __tablename__ = "physical_tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)
    position = Column(String(10), nullable=True)  # A1, B2, 1, 2, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track", back_populates="physical_tracks")
    release = relationship("Release", back_populates="physical_tracks")

    def __repr__(self) -> str:
        return f"<PhysicalTrack(id={self.id}, position='{self.position}')>"


class ImportBatch(Base):
    """Track import batches for auditing and incremental updates."""

    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # traktor_nml, discogs_api, discogs_csv
    source_type = Column(String(50), nullable=False)
    source_file = Column(String(512), nullable=True)  # File path if applicable
    records_imported = Column(Integer, nullable=False, default=0)
    # pending, success, error
    status = Column(String(20), nullable=False, default="pending")
    error_message = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ImportBatch(id={self.id}, source='{self.source_type}', "
            f"status='{self.status}')>"
        )


# Create indexes for performance
Index("idx_tracks_artist_title", Track.artist, Track.title)
Index("idx_tracks_artist", Track.artist)
Index("idx_tracks_title", Track.title)
Index("idx_tracks_album", Track.album)
Index("idx_digital_tracks_track_id", DigitalTrack.track_id)
Index("idx_digital_tracks_file_path", DigitalTrack.file_path)
Index("idx_physical_tracks_track_id", PhysicalTrack.track_id)
Index("idx_physical_tracks_release_id", PhysicalTrack.release_id)
Index("idx_releases_discogs_id", Release.discogs_id)
Index("idx_import_batches_source_type", ImportBatch.source_type)
Index("idx_import_batches_created_at", ImportBatch.created_at)


# Database engine and session configuration
def create_database_engine(database_url: str):
    """Create and configure the database engine."""
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    )
    return engine


def create_database_session(engine):
    """Create a database session factory."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


def init_database(database_url: str):
    """Initialize the database with all tables."""
    engine = create_database_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine
