"""Tests for database models."""


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from musictool.models.database import (
    Base,
    DigitalTrack,
    ImportBatch,
    PhysicalTrack,
    Release,
    Track,
)


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_track(session):
    """Create a sample track for testing."""
    track = Track(
        artist="Test Artist",
        title="Test Song",
        album="Test Album",
        label="Test Label",
        year=2023,
        duration_ms=240000,  # 4 minutes
    )
    session.add(track)
    session.commit()
    return track


@pytest.fixture
def sample_release(session):
    """Create a sample release for testing."""
    release = Release(
        title="Test Release",
        artist="Test Artist",
        label="Test Label",
        year=2023,
        format_type="vinyl",
        discogs_id=12345,
    )
    session.add(release)
    session.commit()
    return release


class TestTrack:
    """Test Track model."""

    def test_track_creation(self, session):
        """Test creating a track."""
        track = Track(
            artist="Artist Name",
            title="Song Title",
            album="Album Name",
            year=2023,
        )
        session.add(track)
        session.commit()

        assert track.id is not None
        assert track.artist == "Artist Name"
        assert track.title == "Song Title"
        assert track.album == "Album Name"
        assert track.year == 2023
        assert track.created_at is not None
        assert track.updated_at is not None

    def test_track_minimal_required_fields(self, session):
        """Test creating a track with only required fields."""
        track = Track(artist="Artist", title="Title")
        session.add(track)
        session.commit()

        assert track.id is not None
        assert track.artist == "Artist"
        assert track.title == "Title"
        assert track.album is None
        assert track.year is None

    def test_track_repr(self, sample_track):
        """Test track string representation."""
        repr_str = repr(sample_track)
        assert "Test Artist" in repr_str
        assert "Test Song" in repr_str
        assert str(sample_track.id) in repr_str

    def test_track_format_properties_empty(self, sample_track):
        """Test format properties when no formats exist."""
        assert not sample_track.has_digital_format
        assert not sample_track.has_physical_format

    def test_track_format_properties_with_digital(self, session, sample_track):
        """Test format properties with digital format."""
        digital = DigitalTrack(
            track_id=sample_track.id,
            file_path="/path/to/file.mp3",
            format="mp3",
            source_file="test.nml",
        )
        session.add(digital)
        session.commit()
        session.refresh(sample_track)

        assert sample_track.has_digital_format
        assert not sample_track.has_physical_format

    def test_track_format_properties_with_physical(self, session, sample_track, sample_release):
        """Test format properties with physical format."""
        physical = PhysicalTrack(
            track_id=sample_track.id,
            release_id=sample_release.id,
            position="A1",
        )
        session.add(physical)
        session.commit()
        session.refresh(sample_track)

        assert not sample_track.has_digital_format
        assert sample_track.has_physical_format


class TestDigitalTrack:
    """Test DigitalTrack model."""

    def test_digital_track_creation(self, session, sample_track):
        """Test creating a digital track."""
        digital = DigitalTrack(
            track_id=sample_track.id,
            file_path="/path/to/music.flac",
            format="flac",
            bitrate=1411,
            source_file="/path/to/traktor.nml",
        )
        session.add(digital)
        session.commit()

        assert digital.id is not None
        assert digital.track_id == sample_track.id
        assert digital.file_path == "/path/to/music.flac"
        assert digital.format == "flac"
        assert digital.bitrate == 1411
        assert digital.source_file == "/path/to/traktor.nml"
        assert digital.created_at is not None

    def test_digital_track_relationship(self, session, sample_track):
        """Test relationship with track."""
        digital = DigitalTrack(
            track_id=sample_track.id,
            file_path="/path/to/file.mp3",
            format="mp3",
            source_file="test.nml",
        )
        session.add(digital)
        session.commit()

        # Test the relationship
        assert digital.track == sample_track
        assert digital in sample_track.digital_tracks

    def test_digital_track_repr(self, session, sample_track):
        """Test digital track string representation."""
        digital = DigitalTrack(
            track_id=sample_track.id,
            file_path="/path/to/file.mp3",
            format="mp3",
            source_file="test.nml",
        )
        session.add(digital)
        session.commit()

        repr_str = repr(digital)
        assert "mp3" in repr_str
        assert "/path/to/file.mp3" in repr_str
        assert str(digital.id) in repr_str


class TestRelease:
    """Test Release model."""

    def test_release_creation(self, session):
        """Test creating a release."""
        release = Release(
            title="Test Album",
            artist="Test Artist",
            label="Test Label",
            year=2023,
            format_type="cd",
            discogs_id=54321,
        )
        session.add(release)
        session.commit()

        assert release.id is not None
        assert release.title == "Test Album"
        assert release.artist == "Test Artist"
        assert release.label == "Test Label"
        assert release.year == 2023
        assert release.format_type == "cd"
        assert release.discogs_id == 54321
        assert release.created_at is not None

    def test_release_minimal_fields(self, session):
        """Test creating a release with minimal fields."""
        release = Release(
            title="Minimal Release",
            artist="Minimal Artist",
            format_type="vinyl",
        )
        session.add(release)
        session.commit()

        assert release.id is not None
        assert release.title == "Minimal Release"
        assert release.artist == "Minimal Artist"
        assert release.format_type == "vinyl"
        assert release.label is None
        assert release.year is None
        assert release.discogs_id is None

    def test_release_repr(self, sample_release):
        """Test release string representation."""
        repr_str = repr(sample_release)
        assert "Test Release" in repr_str
        assert "vinyl" in repr_str
        assert str(sample_release.id) in repr_str


class TestPhysicalTrack:
    """Test PhysicalTrack model."""

    def test_physical_track_creation(self, session, sample_track, sample_release):
        """Test creating a physical track."""
        physical = PhysicalTrack(
            track_id=sample_track.id,
            release_id=sample_release.id,
            position="B2",
        )
        session.add(physical)
        session.commit()

        assert physical.id is not None
        assert physical.track_id == sample_track.id
        assert physical.release_id == sample_release.id
        assert physical.position == "B2"
        assert physical.created_at is not None

    def test_physical_track_relationships(self, session, sample_track, sample_release):
        """Test relationships with track and release."""
        physical = PhysicalTrack(
            track_id=sample_track.id,
            release_id=sample_release.id,
            position="A1",
        )
        session.add(physical)
        session.commit()

        # Test relationships
        assert physical.track == sample_track
        assert physical.release == sample_release
        assert physical in sample_track.physical_tracks
        assert physical in sample_release.physical_tracks

    def test_physical_track_repr(self, session, sample_track, sample_release):
        """Test physical track string representation."""
        physical = PhysicalTrack(
            track_id=sample_track.id,
            release_id=sample_release.id,
            position="A1",
        )
        session.add(physical)
        session.commit()

        repr_str = repr(physical)
        assert "A1" in repr_str
        assert str(physical.id) in repr_str


class TestImportBatch:
    """Test ImportBatch model."""

    def test_import_batch_creation(self, session):
        """Test creating an import batch."""
        batch = ImportBatch(
            source_type="traktor_nml",
            source_file="/path/to/collection.nml",
            records_imported=150,
            status="success",
        )
        session.add(batch)
        session.commit()

        assert batch.id is not None
        assert batch.source_type == "traktor_nml"
        assert batch.source_file == "/path/to/collection.nml"
        assert batch.records_imported == 150
        assert batch.status == "success"
        assert batch.error_message is None
        assert batch.created_at is not None

    def test_import_batch_defaults(self, session):
        """Test import batch with default values."""
        batch = ImportBatch(source_type="discogs_api")
        session.add(batch)
        session.commit()

        assert batch.records_imported == 0
        assert batch.status == "pending"
        assert batch.source_file is None
        assert batch.error_message is None

    def test_import_batch_with_error(self, session):
        """Test import batch with error."""
        batch = ImportBatch(
            source_type="discogs_csv",
            source_file="/path/to/export.csv",
            status="error",
            error_message="File not found",
        )
        session.add(batch)
        session.commit()

        assert batch.status == "error"
        assert batch.error_message == "File not found"

    def test_import_batch_repr(self, session):
        """Test import batch string representation."""
        batch = ImportBatch(
            source_type="traktor_nml",
            status="success",
        )
        session.add(batch)
        session.commit()

        repr_str = repr(batch)
        assert "traktor_nml" in repr_str
        assert "success" in repr_str
        assert str(batch.id) in repr_str


class TestModelRelationships:
    """Test relationships between models."""

    def test_cascade_delete_digital_tracks(self, session, sample_track):
        """Test that deleting a track cascades to digital tracks."""
        digital = DigitalTrack(
            track_id=sample_track.id,
            file_path="/path/to/file.mp3",
            format="mp3",
            source_file="test.nml",
        )
        session.add(digital)
        session.commit()

        digital_id = digital.id
        track_id = sample_track.id

        # Delete the track
        session.delete(sample_track)
        session.commit()

        # Check that digital track was also deleted
        deleted_digital = session.query(DigitalTrack).filter_by(id=digital_id).first()
        assert deleted_digital is None

        deleted_track = session.query(Track).filter_by(id=track_id).first()
        assert deleted_track is None

    def test_cascade_delete_physical_tracks(self, session, sample_track, sample_release):
        """Test that deleting a track cascades to physical tracks."""
        physical = PhysicalTrack(
            track_id=sample_track.id,
            release_id=sample_release.id,
            position="A1",
        )
        session.add(physical)
        session.commit()

        physical_id = physical.id
        track_id = sample_track.id

        # Delete the track
        session.delete(sample_track)
        session.commit()

        # Check that physical track was also deleted
        deleted_physical = session.query(PhysicalTrack).filter_by(id=physical_id).first()
        assert deleted_physical is None

    def test_cascade_delete_release_physical_tracks(self, session, sample_track, sample_release):
        """Test that deleting a release cascades to its physical tracks."""
        physical = PhysicalTrack(
            track_id=sample_track.id,
            release_id=sample_release.id,
            position="A1",
        )
        session.add(physical)
        session.commit()

        physical_id = physical.id
        release_id = sample_release.id

        # Delete the release
        session.delete(sample_release)
        session.commit()

        # Check that physical track was also deleted
        deleted_physical = session.query(PhysicalTrack).filter_by(id=physical_id).first()
        assert deleted_physical is None

        # But track should still exist
        assert session.query(Track).filter_by(id=sample_track.id).first() is not None
