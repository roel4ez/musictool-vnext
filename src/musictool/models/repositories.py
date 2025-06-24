"""Repository pattern implementation for data access."""

from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session

from .database import DigitalTrack, ImportBatch, PhysicalTrack, Release, Track


class BaseRepository(ABC):
    """Base repository with common CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def get_model_class(self):
        """Return the SQLAlchemy model class."""
        raise NotImplementedError

    def get_by_id(self, id: int):
        """Get a record by ID."""
        return self.session.query(self.get_model_class()).filter_by(id=id).first()

    def get_all(self, limit: Optional[int] = None, offset: int = 0):
        """Get all records with optional pagination."""
        query = self.session.query(self.get_model_class()).offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    def create(self, **kwargs):
        """Create a new record."""
        obj = self.get_model_class()(**kwargs)
        self.session.add(obj)
        self.session.flush()  # Get the ID without committing
        return obj

    def update(self, id: int, **kwargs):
        """Update a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.session.flush()
        return obj

    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def count(self) -> int:
        """Count total records."""
        return self.session.query(self.get_model_class()).count()


class TrackRepository(BaseRepository):
    """Repository for Track entities."""

    def get_model_class(self):
        return Track

    def find_by_artist_and_title(self, artist: str, title: str) -> Optional[Track]:
        """Find track by artist and title (exact match)."""
        return self.session.query(Track).filter_by(artist=artist, title=title).first()

    def search_by_artist(self, artist: str, limit: Optional[int] = None) -> list[Track]:
        """Search tracks by artist (case-insensitive partial match)."""
        query = self.session.query(Track).filter(Track.artist.ilike(f"%{artist}%"))
        if limit:
            query = query.limit(limit)
        return query.all()

    def search_by_title(self, title: str, limit: Optional[int] = None) -> list[Track]:
        """Search tracks by title (case-insensitive partial match)."""
        query = self.session.query(Track).filter(Track.title.ilike(f"%{title}%"))
        if limit:
            query = query.limit(limit)
        return query.all()

    def search_by_album(self, album: str, limit: Optional[int] = None) -> list[Track]:
        """Search tracks by album (case-insensitive partial match)."""
        query = self.session.query(Track).filter(Track.album.ilike(f"%{album}%"))
        if limit:
            query = query.limit(limit)
        return query.all()

    def find_by_year(self, year: int) -> list[Track]:
        """Find tracks by release year."""
        return self.session.query(Track).filter_by(year=year).all()

    def get_with_digital_formats(self, limit: Optional[int] = None) -> list[Track]:
        """Get tracks that have digital formats."""
        query = self.session.query(Track).join(DigitalTrack)
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_with_physical_formats(self, limit: Optional[int] = None) -> list[Track]:
        """Get tracks that have physical formats."""
        query = self.session.query(Track).join(PhysicalTrack)
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_orphaned_tracks(self, limit: Optional[int] = None) -> list[Track]:
        """Get tracks that have no digital or physical formats."""
        query = (
            self.session.query(Track)
            .outerjoin(DigitalTrack)
            .outerjoin(PhysicalTrack)
            .filter(DigitalTrack.id.is_(None))
            .filter(PhysicalTrack.id.is_(None))
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def search_tracks(
        self,
        artist: Optional[str] = None,
        title: Optional[str] = None,
        album: Optional[str] = None,
        year: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[Track]:
        """Advanced search across multiple fields."""
        query = self.session.query(Track)

        if artist:
            query = query.filter(Track.artist.ilike(f"%{artist}%"))
        if title:
            query = query.filter(Track.title.ilike(f"%{title}%"))
        if album:
            query = query.filter(Track.album.ilike(f"%{album}%"))
        if year:
            query = query.filter_by(year=year)

        if limit:
            query = query.limit(limit)

        return query.all()


class DigitalTrackRepository(BaseRepository):
    """Repository for DigitalTrack entities."""

    def get_model_class(self):
        return DigitalTrack

    def find_by_file_path(self, file_path: str) -> Optional[DigitalTrack]:
        """Find digital track by file path."""
        return self.session.query(DigitalTrack).filter_by(file_path=file_path).first()

    def find_by_track_id(self, track_id: int) -> list[DigitalTrack]:
        """Find all digital formats for a track."""
        return self.session.query(DigitalTrack).filter_by(track_id=track_id).all()

    def find_by_format(self, format: str) -> list[DigitalTrack]:
        """Find digital tracks by format (mp3, flac, etc.)."""
        return self.session.query(DigitalTrack).filter_by(format=format).all()

    def find_by_source_file(self, source_file: str) -> list[DigitalTrack]:
        """Find digital tracks by source file (NML file)."""
        return self.session.query(DigitalTrack).filter_by(source_file=source_file).all()


class PhysicalTrackRepository(BaseRepository):
    """Repository for PhysicalTrack entities."""

    def get_model_class(self):
        return PhysicalTrack

    def find_by_track_id(self, track_id: int) -> list[PhysicalTrack]:
        """Find all physical formats for a track."""
        return self.session.query(PhysicalTrack).filter_by(track_id=track_id).all()

    def find_by_release_id(self, release_id: int) -> list[PhysicalTrack]:
        """Find all tracks on a release."""
        return (
            self.session.query(PhysicalTrack)
            .filter_by(release_id=release_id)
            .order_by(PhysicalTrack.position)
            .all()
        )


class ReleaseRepository(BaseRepository):
    """Repository for Release entities."""

    def get_model_class(self):
        return Release

    def find_by_discogs_id(self, discogs_id: int) -> Optional[Release]:
        """Find release by Discogs ID."""
        return self.session.query(Release).filter_by(discogs_id=discogs_id).first()

    def search_by_title(self, title: str, limit: Optional[int] = None) -> list[Release]:
        """Search releases by title."""
        query = self.session.query(Release).filter(Release.title.ilike(f"%{title}%"))
        if limit:
            query = query.limit(limit)
        return query.all()

    def search_by_artist(
        self, artist: str, limit: Optional[int] = None
    ) -> list[Release]:
        """Search releases by artist."""
        query = self.session.query(Release).filter(Release.artist.ilike(f"%{artist}%"))
        if limit:
            query = query.limit(limit)
        return query.all()

    def find_by_format(self, format_type: str) -> list[Release]:
        """Find releases by format type."""
        return self.session.query(Release).filter_by(format_type=format_type).all()

    def find_by_year(self, year: int) -> list[Release]:
        """Find releases by year."""
        return self.session.query(Release).filter_by(year=year).all()


class ImportBatchRepository(BaseRepository):
    """Repository for ImportBatch entities."""

    def get_model_class(self):
        return ImportBatch

    def find_by_source_type(self, source_type: str) -> list[ImportBatch]:
        """Find import batches by source type."""
        return (
            self.session.query(ImportBatch)
            .filter_by(source_type=source_type)
            .order_by(ImportBatch.created_at.desc())
            .all()
        )

    def find_by_status(self, status: str) -> list[ImportBatch]:
        """Find import batches by status."""
        return (
            self.session.query(ImportBatch)
            .filter_by(status=status)
            .order_by(ImportBatch.created_at.desc())
            .all()
        )

    def get_latest_successful_import(self, source_type: str) -> Optional[ImportBatch]:
        """Get the latest successful import for a source type."""
        return (
            self.session.query(ImportBatch)
            .filter_by(source_type=source_type, status="success")
            .order_by(ImportBatch.created_at.desc())
            .first()
        )


class RepositoryManager:
    """Manages all repositories for a database session."""

    def __init__(self, session: Session):
        self.session = session
        self.tracks = TrackRepository(session)
        self.digital_tracks = DigitalTrackRepository(session)
        self.physical_tracks = PhysicalTrackRepository(session)
        self.releases = ReleaseRepository(session)
        self.import_batches = ImportBatchRepository(session)

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()

    def flush(self):
        """Flush the session (execute pending operations without committing)."""
        self.session.flush()
