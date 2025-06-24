# MusicTool MVP Project Plan

*Date: June 23, 2025*

## Vision

A simple application that shows your music collection in one table, displaying which formats you own and providing direct links to Discogs for viewing or purchasing missing tracks.

## Key Decisions

### Supported source data

- **Digital Collection**: Traktor NML files (nice-to-have: auto-detected)
- **Physical Collection**: Discogs API integration, or from Exported CSV file
  - Discogs exposes releases, these will need to be expanded into individual songs
- **Gap Analysis**: Fuzzy matching between digital and physical

Data constraints: 
- the NML file must be backed up before every change.
- it must be possible to provide a new version of the source data files, and the
  tool should import only new songs or releases.

### Architecture: Standalone Desktop App

- **Technology**: Streamlit with local database

### User Interface: Minimalist Single-Table View

- **Core View**: One table showing all tracks with essential information
- **Columns**: Artist | Track | Label | Digital Format | Physical Format |
  Discogs Links
- **Format Indicators**: Filetype, 💿 Vinyl, ❌ Missing
- **Actions**: [View] Discogs release

## MVP Scope

### Must Have
1. Parse Traktor NML file
2. Sync with Discogs collection via API
3. Single table view with format indicators
4. Direct Discogs links for viewing
5. Basic collection statistics

### Won't Have (v1)
- Multiple views/dashboards
- Complex metadata editing
- Advanced analytics
- Mobile support
- Cloud sync

## Success Criteria

- ✅ Display 3,000+ tracks in responsive table
- ✅ Clear visual indication of owned formats
- ✅ Sub-second performance for typical operations

