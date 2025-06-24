"""Tests for repository classes."""

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
from musictool.models.repositories import (
    DigitalTrackRepository,
    ImportBatchRepository,
    PhysicalTrackRepository,
    ReleaseRepository,
    RepositoryManager,
    TrackRepository,
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
def sample_tracks(session):
    """Create sample tracks for testing."""
    tracks = [
        Track(artist="Artist A", title="Song 1", album="Album A", year=2020),
        Track(artist="Artist B", title="Song 2", album="Album B", year=2021),
        Track(artist="Artist A", title="Song 3", album="Album A", year=2020),
        Track(artist="Artist C", title="Song 4", year=2022),  # No album
    ]
    session.add_all(tracks)
    session.commit()
    return tracks


@pytest.fixture
def sample_releases(session):
    """Create sample releases for testing."""
    releases = [
        Release(title="Release A", artist="Artist A", format_type="vinyl", year=2020),
        Release(title="Release B", artist="Artist B", format_type="cd", year=2021),
        Release(title="Release C", artist="Artist A", format_type="vinyl", year=2022),
    ]
    session.add_all(releases)
    session.commit()
    return releases


class TestTrackRepository:
    """Test TrackRepository methods."""

    def test_get_model_class(self, session):
        """Test get_model_class returns Track."""
        repo = TrackRepository(session)
        assert repo.get_model_class() == Track

    def test_create_track(self, session):
        """Test creating a track."""
        repo = TrackRepository(session)
        track = repo.create(artist="Test Artist", title="Test Song", year=2023)

        assert track.id is not None
        assert track.artist == "Test Artist"
        assert track.title == "Test Song"
        assert track.year == 2023

    def test_get_by_id(self, session, sample_tracks):
        """Test getting track by ID."""
        repo = TrackRepository(session)
        track = repo.get_by_id(sample_tracks[0].id)

        assert track is not None
        assert track.artist == "Artist A"
        assert track.title == "Song 1"

    def test_get_all(self, session, sample_tracks):
        """Test getting all tracks."""
        repo = TrackRepository(session)
        tracks = repo.get_all()

        assert len(tracks) == 4

        # Test with limit
        limited_tracks = repo.get_all(limit=2)
        assert len(limited_tracks) == 2

    def test_find_by_artist_and_title(self, session, sample_tracks):
        """Test finding track by artist and title."""
        repo = TrackRepository(session)
        track = repo.find_by_artist_and_title("Artist A", "Song 1")

        assert track is not None
        assert track.artist == "Artist A"
        assert track.title == "Song 1"

        # Test non-existent track
        no_track = repo.find_by_artist_and_title("Non-existent", "Not Found")
        assert no_track is None

    def test_search_by_artist(self, session, sample_tracks):
        """Test searching tracks by artist."""
        repo = TrackRepository(session)

        # Search for "Artist A"
        tracks = repo.search_by_artist("Artist A")
        assert len(tracks) == 2

        # Partial search
        tracks = repo.search_by_artist("Artist")
        assert len(tracks) == 4  # All tracks have "Artist" in the name

        # With limit
        tracks = repo.search_by_artist("Artist", limit=2)
        assert len(tracks) == 2

    def test_search_by_title(self, session, sample_tracks):
        """Test searching tracks by title."""
        repo = TrackRepository(session)

        # Search for specific title
        tracks = repo.search_by_title("Song 1")
        assert len(tracks) == 1
        assert tracks[0].title == "Song 1"

        # Partial search
        tracks = repo.search_by_title("Song")
        assert len(tracks) == 4

    def test_search_by_album(self, session, sample_tracks):
        """Test searching tracks by album."""
        repo = TrackRepository(session)

        # Search for specific album
        tracks = repo.search_by_album("Album A")
        assert len(tracks) == 2

        # Partial search
        tracks = repo.search_by_album("Album")
        assert len(tracks) == 3  # One track has no album

    def test_find_by_year(self, session, sample_tracks):
        """Test finding tracks by year."""
        repo = TrackRepository(session)

        tracks_2020 = repo.find_by_year(2020)
        assert len(tracks_2020) == 2

        tracks_2021 = repo.find_by_year(2021)
        assert len(tracks_2021) == 1

    def test_search_tracks_advanced(self, session, sample_tracks):
        """Test advanced search across multiple fields."""
        repo = TrackRepository(session)

        # Search by artist and year
        tracks = repo.search_tracks(artist="Artist A", year=2020)
        assert len(tracks) == 2

        # Search by multiple criteria
        tracks = repo.search_tracks(artist="Artist A", album="Album A", year=2020)
        assert len(tracks) == 2

        # Search with no matches
        tracks = repo.search_tracks(artist="Non-existent")
        assert len(tracks) == 0

    def test_get_with_digital_formats(self, session, sample_tracks):
        """Test getting tracks with digital formats."""
        repo = TrackRepository(session)

        # Add a digital track
        digital = DigitalTrack(
            track_id=sample_tracks[0].id,
            file_path="/path/to/file.mp3",
            format="mp3",
            source_file="test.nml"
        )
        session.add(digital)
        session.commit()

        tracks = repo.get_with_digital_formats()
        assert len(tracks) == 1
        assert tracks[0].id == sample_tracks[0].id

    def test_get_with_physical_formats(self, session, sample_tracks, sample_releases):
        """Test getting tracks with physical formats."""
        repo = TrackRepository(session)

        # Add a physical track
        physical = PhysicalTrack(
            track_id=sample_tracks[0].id,
            release_id=sample_releases[0].id,
            position="A1"
        )
        session.add(physical)
        session.commit()

        tracks = repo.get_with_physical_formats()
        assert len(tracks) == 1
        assert tracks[0].id == sample_tracks[0].id

    def test_get_orphaned_tracks(self, session, sample_tracks, sample_releases):
        """Test getting orphaned tracks (no digital or physical formats)."""
        repo = TrackRepository(session)

        # Initially all tracks are orphaned
        orphaned = repo.get_orphaned_tracks()
        assert len(orphaned) == 4

        # Add a digital track to one
        digital = DigitalTrack(
            track_id=sample_tracks[0].id,
            file_path="/path/to/file.mp3",
            format="mp3",
            source_file="test.nml"
        )
        session.add(digital)
        session.commit()

        orphaned = repo.get_orphaned_tracks()
        assert len(orphaned) == 3  # One less orphaned

    def test_update(self, session, sample_tracks):
        """Test updating a track."""
        repo = TrackRepository(session)
        track_id = sample_tracks[0].id

        updated_track = repo.update(track_id, year=2025, album="Updated Album")
        assert updated_track.year == 2025
        assert updated_track.album == "Updated Album"

        # Verify in database
        session.commit()
        fetched_track = repo.get_by_id(track_id)
        assert fetched_track.year == 2025
        assert fetched_track.album == "Updated Album"

    def test_delete(self, session, sample_tracks):
        """Test deleting a track."""
        repo = TrackRepository(session)
        track_id = sample_tracks[0].id

        result = repo.delete(track_id)
        assert result is True

        # Verify deleted
        session.commit()
        deleted_track = repo.get_by_id(track_id)
        assert deleted_track is None

    def test_count(self, session, sample_tracks):
        """Test counting tracks."""
        repo = TrackRepository(session)
        count = repo.count()
        assert count == 4


class TestDigitalTrackRepository:
    """Test DigitalTrackRepository methods."""

    def test_get_model_class(self, session):
        """Test get_model_class returns DigitalTrack."""
        repo = DigitalTrackRepository(session)
        assert repo.get_model_class() == DigitalTrack

    def test_find_by_file_path(self, session, sample_tracks):
        """Test finding digital track by file path."""
        repo = DigitalTrackRepository(session)

        # Create digital track
        digital = DigitalTrack(
            track_id=sample_tracks[0].id,
            file_path="/unique/path/file.flac",
            format="flac",
            source_file="test.nml"
        )
        session.add(digital)
        session.commit()

        found = repo.find_by_file_path("/unique/path/file.flac")
        assert found is not None
        assert found.format == "flac"

        not_found = repo.find_by_file_path("/non/existent/path")
        assert not_found is None

    def test_find_by_track_id(self, session, sample_tracks):
        """Test finding digital tracks by track ID."""
        repo = DigitalTrackRepository(session)

        # Create multiple digital tracks for same track
        digitals = [
            DigitalTrack(
                track_id=sample_tracks[0].id,
                file_path="/path/file.mp3",
                format="mp3",
                source_file="test.nml"
            ),
            DigitalTrack(
                track_id=sample_tracks[0].id,
                file_path="/path/file.flac",
                format="flac",
                source_file="test.nml"
            ),
        ]
        session.add_all(digitals)
        session.commit()

        found = repo.find_by_track_id(sample_tracks[0].id)
        assert len(found) == 2

    def test_find_by_format(self, session, sample_tracks):
        """Test finding digital tracks by format."""
        repo = DigitalTrackRepository(session)

        # Create tracks with different formats
        digitals = [
            DigitalTrack(
                track_id=sample_tracks[0].id,
                file_path="/path/file1.mp3",
                format="mp3",
                source_file="test.nml"
            ),
            DigitalTrack(
                track_id=sample_tracks[1].id,
                file_path="/path/file2.mp3",
                format="mp3",
                source_file="test.nml"
            ),
            DigitalTrack(
                track_id=sample_tracks[2].id,
                file_path="/path/file3.flac",
                format="flac",
                source_file="test.nml"
            ),
        ]
        session.add_all(digitals)
        session.commit()

        mp3_tracks = repo.find_by_format("mp3")
        assert len(mp3_tracks) == 2

        flac_tracks = repo.find_by_format("flac")
        assert len(flac_tracks) == 1

    def test_find_by_source_file(self, session, sample_tracks):
        """Test finding digital tracks by source file."""
        repo = DigitalTrackRepository(session)

        # Create tracks from different sources
        digitals = [
            DigitalTrack(
                track_id=sample_tracks[0].id,
                file_path="/path/file1.mp3",
                format="mp3",
                source_file="source1.nml"
            ),
            DigitalTrack(
                track_id=sample_tracks[1].id,
                file_path="/path/file2.mp3",
                format="mp3",
                source_file="source1.nml"
            ),
            DigitalTrack(
                track_id=sample_tracks[2].id,
                file_path="/path/file3.mp3",
                format="mp3",
                source_file="source2.nml"
            ),
        ]
        session.add_all(digitals)
        session.commit()

        source1_tracks = repo.find_by_source_file("source1.nml")
        assert len(source1_tracks) == 2

        source2_tracks = repo.find_by_source_file("source2.nml")
        assert len(source2_tracks) == 1


class TestReleaseRepository:
    """Test ReleaseRepository methods."""

    def test_get_model_class(self, session):
        """Test get_model_class returns Release."""
        repo = ReleaseRepository(session)
        assert repo.get_model_class() == Release

    def test_find_by_discogs_id(self, session, sample_releases):
        """Test finding release by Discogs ID."""
        repo = ReleaseRepository(session)

        # Update one release with Discogs ID
        sample_releases[0].discogs_id = 12345
        session.commit()

        found = repo.find_by_discogs_id(12345)
        assert found is not None
        assert found.title == "Release A"

        not_found = repo.find_by_discogs_id(99999)
        assert not_found is None

    def test_search_by_title(self, session, sample_releases):
        """Test searching releases by title."""
        repo = ReleaseRepository(session)

        # Search for specific title
        releases = repo.search_by_title("Release A")
        assert len(releases) == 1
        assert releases[0].title == "Release A"

        # Partial search
        releases = repo.search_by_title("Release")
        assert len(releases) == 3

    def test_search_by_artist(self, session, sample_releases):
        """Test searching releases by artist."""
        repo = ReleaseRepository(session)

        # Search for Artist A (should have 2 releases)
        releases = repo.search_by_artist("Artist A")
        assert len(releases) == 2

        # Search for Artist B
        releases = repo.search_by_artist("Artist B")
        assert len(releases) == 1

    def test_find_by_format(self, session, sample_releases):
        """Test finding releases by format."""
        repo = ReleaseRepository(session)

        vinyl_releases = repo.find_by_format("vinyl")
        assert len(vinyl_releases) == 2

        cd_releases = repo.find_by_format("cd")
        assert len(cd_releases) == 1

    def test_find_by_year(self, session, sample_releases):
        """Test finding releases by year."""
        repo = ReleaseRepository(session)

        releases_2020 = repo.find_by_year(2020)
        assert len(releases_2020) == 1

        releases_2021 = repo.find_by_year(2021)
        assert len(releases_2021) == 1


class TestImportBatchRepository:
    """Test ImportBatchRepository methods."""

    def test_get_model_class(self, session):
        """Test get_model_class returns ImportBatch."""
        repo = ImportBatchRepository(session)
        assert repo.get_model_class() == ImportBatch

    def test_find_by_source_type(self, session):
        """Test finding import batches by source type."""
        repo = ImportBatchRepository(session)

        # Create batches with different source types
        batches = [
            ImportBatch(source_type="traktor_nml", status="success"),
            ImportBatch(source_type="traktor_nml", status="error"),
            ImportBatch(source_type="discogs_api", status="success"),
        ]
        session.add_all(batches)
        session.commit()

        traktor_batches = repo.find_by_source_type("traktor_nml")
        assert len(traktor_batches) == 2

        discogs_batches = repo.find_by_source_type("discogs_api")
        assert len(discogs_batches) == 1

    def test_find_by_status(self, session):
        """Test finding import batches by status."""
        repo = ImportBatchRepository(session)

        # Create batches with different statuses
        batches = [
            ImportBatch(source_type="traktor_nml", status="success"),
            ImportBatch(source_type="discogs_api", status="success"),
            ImportBatch(source_type="discogs_csv", status="error"),
            ImportBatch(source_type="traktor_nml", status="pending"),
        ]
        session.add_all(batches)
        session.commit()

        success_batches = repo.find_by_status("success")
        assert len(success_batches) == 2

        error_batches = repo.find_by_status("error")
        assert len(error_batches) == 1

        pending_batches = repo.find_by_status("pending")
        assert len(pending_batches) == 1

    def test_get_latest_successful_import(self, session):
        """Test getting latest successful import."""
        repo = ImportBatchRepository(session)

        # Create batches at different times
        batches = [
            ImportBatch(source_type="traktor_nml", status="success", records_imported=100),
            ImportBatch(source_type="traktor_nml", status="error"),
            ImportBatch(source_type="traktor_nml", status="success", records_imported=150),
        ]
        session.add_all(batches)
        session.commit()

        latest = repo.get_latest_successful_import("traktor_nml")
        assert latest is not None
        assert latest.status == "success"
        assert latest.records_imported == 150  # Should be the latest one

        # Test for non-existent source type
        no_latest = repo.get_latest_successful_import("non_existent")
        assert no_latest is None


class TestRepositoryManager:
    """Test RepositoryManager."""

    def test_repository_manager_initialization(self, session):
        """Test that repository manager initializes all repositories."""
        manager = RepositoryManager(session)

        assert isinstance(manager.tracks, TrackRepository)
        assert isinstance(manager.digital_tracks, DigitalTrackRepository)
        assert isinstance(manager.physical_tracks, PhysicalTrackRepository)
        assert isinstance(manager.releases, ReleaseRepository)
        assert isinstance(manager.import_batches, ImportBatchRepository)

        # All should use the same session
        assert manager.tracks.session is session
        assert manager.digital_tracks.session is session

    def test_repository_manager_transaction_methods(self, session, sample_tracks):
        """Test commit, rollback, and flush methods."""
        manager = RepositoryManager(session)

        # Create a track
        track = manager.tracks.create(artist="Test", title="Test")
        assert track.id is not None

        # Test flush
        manager.flush()
        assert track.id is not None

        # Test rollback
        manager.rollback()

        # Test commit
        track2 = manager.tracks.create(artist="Test2", title="Test2")
        manager.commit()

        # Verify track2 persists
        found = manager.tracks.get_by_id(track2.id)
        assert found is not None
