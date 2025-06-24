# Step 2: Database Schema and Models

## Objective
Design and implement the local SQLite database schema to store tracks, formats, and metadata.

## Tasks
- [ ] Design database schema for tracks table
- [ ] Design schema for formats/sources tracking
- [ ] Create SQLAlchemy models or direct SQL schema
- [ ] Implement database initialization and migration logic
- [ ] Create data access layer (DAO/Repository pattern)
- [ ] Add database connection management
- [ ] Create basic CRUD operations for tracks

## Database Tables
- **tracks**: id, artist, title, label, album, year, duration
- **digital_formats**: track_id, file_path, format, bitrate, source_file
- **physical_formats**: track_id, discogs_release_id, format_type (vinyl/cd/etc)
- **import_history**: timestamp, source_type, file_path, records_imported

## Acceptance Criteria
- [ ] Database schema is properly normalized
- [ ] All tables have appropriate indexes
- [ ] Data access layer provides clean interface
- [ ] Database can be initialized from scratch
- [ ] Basic queries execute in <100ms for 3000+ records
