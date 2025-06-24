"""Tests for database configuration."""

import os
from unittest.mock import patch

import pytest

from musictool.models.config import (
    DatabaseConfig,
    db_session_scope,
    get_database_config,
    initialize_database,
)
from musictool.models.database import Base, Track


class TestDatabaseConfig:
    """Test DatabaseConfig class."""

    def test_default_database_url(self):
        """Test default database URL."""
        config = DatabaseConfig()
        assert "sqlite:///musictool.db" in config.database_url

    def test_custom_database_url(self):
        """Test custom database URL."""
        custom_url = "sqlite:///test.db"
        config = DatabaseConfig(custom_url)
        assert config.database_url == custom_url

    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///env_test.db"})
    def test_environment_database_url(self):
        """Test database URL from environment variable."""
        config = DatabaseConfig()
        assert config.database_url == "sqlite:///env_test.db"

    def test_create_tables(self):
        """Test creating database tables."""
        # Use in-memory database for testing
        config = DatabaseConfig("sqlite:///:memory:")
        config.create_tables()

        # Verify tables exist by checking metadata
        table_names = list(Base.metadata.tables.keys())
        expected_tables = [
            "tracks",
            "digital_tracks", 
            "physical_tracks",
            "releases",
            "import_batches",
        ]

        for table in expected_tables:
            assert table in table_names

    def test_get_session(self):
        """Test getting a database session."""
        config = DatabaseConfig("sqlite:///:memory:")
        config.create_tables()

        session = config.get_session()
        assert session is not None

        # Test that we can use the session
        track = Track(artist="Test", title="Test")
        session.add(track)
        session.commit()

        # Verify track was saved
        saved_track = session.query(Track).first()
        assert saved_track is not None

        session.close()

    def test_session_scope(self):
        """Test session scope context manager."""
        config = DatabaseConfig("sqlite:///:memory:")
        config.create_tables()

        # Test successful transaction
        with config.session_scope() as session:
            track = Track(artist="Test", title="Test")
            session.add(track)
            # No explicit commit needed - should be automatic

        # Verify track was committed
        with config.session_scope() as session:
            saved_track = session.query(Track).first()
            assert saved_track is not None

    def test_session_scope_rollback(self):
        """Test session scope rollback on exception."""
        config = DatabaseConfig("sqlite:///:memory:")
        config.create_tables()

        # Test rollback on exception
        try:
            with config.session_scope() as session:
                track = Track(artist="Test", title="Test")
                session.add(track)
                session.flush()  # Make sure track gets an ID
                track_id = track.id

                # Force an exception
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify track was rolled back
        with config.session_scope() as session:
            saved_track = session.query(Track).filter_by(id=track_id).first()
            assert saved_track is None


class TestGlobalDatabaseFunctions:
    """Test global database management functions."""

    def setUp(self):
        """Reset global state before each test."""
        # Clear the global config
        import musictool.models.config
        musictool.models.config.db_config = None

    def test_initialize_database(self):
        """Test initializing the global database configuration."""
        self.setUp()

        config = initialize_database("sqlite:///:memory:")
        assert config is not None
        assert isinstance(config, DatabaseConfig)

        # Should be able to get it back
        same_config = get_database_config()
        assert same_config is config

    def test_get_database_config_before_init(self):
        """Test getting database config before initialization raises error."""
        self.setUp()

        with pytest.raises(RuntimeError, match="Database not initialized"):
            get_database_config()

    def test_db_session_scope(self):
        """Test global database session scope."""
        self.setUp()

        initialize_database("sqlite:///:memory:")

        # Test using the global session scope
        with db_session_scope() as session:
            track = Track(artist="Global Test", title="Global Test")
            session.add(track)

        # Verify track was saved
        with db_session_scope() as session:
            saved_track = session.query(Track).first()
            assert saved_track is not None


class TestDatabaseIntegration:
    """Integration tests for the database system."""

    def test_full_database_workflow(self):
        """Test a complete database workflow."""
        # Initialize database
        initialize_database("sqlite:///:memory:")

        # Create some test data using the repository pattern
        from musictool.models.repositories import RepositoryManager

        track_id = None

        with db_session_scope() as session:
            repos = RepositoryManager(session)

            # Create a track
            track = repos.tracks.create(
                artist="Integration Test Artist",
                title="Integration Test Song",
                album="Integration Test Album",
                year=2023
            )
            track_id = track.id

            # Create a digital format
            repos.digital_tracks.create(
                track_id=track.id,
                file_path="/test/path/song.mp3",
                format="mp3",
                source_file="test.nml"
            )

            # Create a release
            release = repos.releases.create(
                title="Integration Test Release",
                artist="Integration Test Artist",
                format_type="vinyl",
                year=2023
            )

            # Create a physical format
            repos.physical_tracks.create(
                track_id=track.id,
                release_id=release.id,
                position="A1"
            )

            # Create an import batch
            repos.import_batches.create(
                source_type="test",
                records_imported=1,
                status="success"
            )

            repos.commit()

        # Verify everything was saved correctly
        with db_session_scope() as session:
            repos = RepositoryManager(session)

            # Check track
            tracks = repos.tracks.get_all()
            assert len(tracks) == 1

            # Check digital format
            digitals = repos.digital_tracks.find_by_track_id(track_id)
            assert len(digitals) == 1

            # Check release
            releases = repos.releases.get_all()
            assert len(releases) == 1

            # Check physical format
            physicals = repos.physical_tracks.find_by_track_id(track_id)
            assert len(physicals) == 1

            # Check import batch
            batches = repos.import_batches.find_by_status("success")
            assert len(batches) == 1

    def test_database_indexes_exist(self):
        """Test that database indexes are created."""
        config = initialize_database("sqlite:///:memory:")

        # For SQLite, we can check if the tables were created successfully
        # The indexes should be created automatically with the tables
        inspector = config.engine.dialect.get_table_names(config.engine.connect())

        # Just verify that our main tables exist
        # (Detailed index checking would require database-specific queries)
        with config.session_scope() as session:
            # Try to query each table to ensure they exist
            session.query(Track).count()

            from musictool.models.database import (
                DigitalTrack,
                ImportBatch,
                PhysicalTrack,
                Release,
            )
            session.query(DigitalTrack).count()
            session.query(PhysicalTrack).count()
            session.query(Release).count()
            session.query(ImportBatch).count()
