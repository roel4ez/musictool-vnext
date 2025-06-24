# ADR-001: Database Design for MusicTool

## Status
Accepted

## Context
We need to design a database schema to store music collection data from multiple sources:
- Digital tracks from Traktor NML files
- Physical releases from Discogs API/CSV
- Matching relationships between digital and physical formats
- Import history for incremental updates

## Decision
We will use SQLite with SQLAlchemy ORM for the following reasons:

### Database Choice: SQLite
- **Embedded**: No separate database server required
- **Zero configuration**: Works out of the box
- **Performance**: Sufficient for 3000+ tracks with proper indexing
- **Portability**: Single file database, easy to backup/restore

### ORM Choice: SQLAlchemy
- **Type safety**: Better integration with our pyright type checking
- **Migrations**: Built-in schema evolution support
- **Query builder**: Prevents SQL injection, improves maintainability
- **Relationships**: Clean handling of foreign keys and joins

### Schema Design Principles
1. **Normalized**: Separate concerns (tracks, formats, sources)
2. **Flexible**: Support for multiple digital/physical formats per track
3. **Auditable**: Track import history and changes
4. **Performant**: Appropriate indexes for common queries

## Schema Overview

```mermaid
erDiagram
    tracks ||--o{ digital_tracks : "has"
    tracks ||--o{ physical_tracks : "has"
    releases ||--o{ physical_tracks : "contains"
    import_batches ||--o{ tracks : "imported_in"
    
    tracks {
        int id PK
        string artist
        string title
        string album
        string label
        int year
        int duration_ms
        datetime created_at
        datetime updated_at
    }
    
    digital_tracks {
        int id PK
        int track_id FK
        string file_path
        string format
        int bitrate
        string source_file
        datetime created_at
    }
    
    physical_tracks {
        int id PK
        int track_id FK
        int release_id FK
        string position
        datetime created_at
    }
    
    releases {
        int id PK
        int discogs_id
        string title
        string artist
        string label
        int year
        string format_type
        datetime created_at
    }
    
    import_batches {
        int id PK
        string source_type
        string source_file
        int records_imported
        datetime created_at
        string status
    }
```

## Consequences

### Positive
- Clean separation of concerns
- Supports fuzzy matching between digital/physical
- Efficient queries with proper indexing
- Easy to extend for future features
- Type-safe with SQLAlchemy models

### Negative  
- Slightly more complex than a flat table structure
- Requires understanding of relational concepts
- Need to manage foreign key relationships

### Mitigation
- Use Repository pattern to hide complexity
- Provide clear documentation and examples
- Add database initialization helpers
