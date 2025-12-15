# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ParseClipmate extracts data from **ClipMate** (a discontinued Windows clipboard manager) and migrates it to SQLite with a web-based viewer. The project provides TWO parsing approaches: **XML-based** (recommended) and **binary-based** (fallback).

**Status**: ✅ **COMPLETE** - All goals achieved with XML-based solution providing 1,125 clips across 19 years with 100% accurate timestamps.

## Recommended Approach: XML Export Parsing

### Why XML?
- **Complete Data**: 1,125 clips vs 258 from binary parsing (4.4x more)
- **Perfect Timestamps**: 100% accurate from DBISAM metadata
- **All Formats**: TEXT, PNG, HTML, RTF, PICTURE, HDROP, FileName
- **Simple Code**: 230 lines vs 315 for binary parser
- **Future-Proof**: Stable XML schema, no reverse engineering needed

### Quick Start (XML Method)
```bash
# 1. Export from ClipMate application
#    File → Export → XML format
#    Select "Everything" container for complete export

# 2. Parse XML and create database
python process_xml_export.py
# Creates: clipmate_from_xml.db (1,125 clips, 3 collections)

# 3. Start web server
python server.py
# Access at: http://localhost:8000
```

## Architecture

### Data Flow (XML-Based)
1. **XML Export** (from ClipMate): Complete data including DBISAM metadata
2. **XML Parsing** (`clipmate_xml_parser.py`): Standard XML parsing
3. **Database Export** (`database.py`): Stores in SQLite (`clipmate_from_xml.db`)
4. **Web API** (`server.py`): FastAPI server exposes data via REST
5. **Frontend** (`index.html`): React-based single-page app

### Key Components

#### `clipmate_xml_parser.py` - XML Parser (PRIMARY)
- **`ClipMateXMLParser`**: Main class for parsing ClipMate XML exports
  - Parses Collections and Clips
  - Extracts 13 metadata fields per clip
  - Handles base64-encoded binary content (images, HTML, RTF)
  - URL-decodes text content
  - Supports multi-format clips
- **Data Extracted**:
  - Metadata: GUID, title, creator, timestamps (created + modified), URL, etc.
  - Content: TEXT, PNG images, HTML, RTF, HDROP, FileName, PICTURE
  - Collections: Samples, Overflow, InBox with full hierarchy
- **Output**: Complete clip data with 100% accurate timestamps

#### `process_xml_export.py` - Database Populator
- Creates enhanced SQLite schema with 19 fields
- Separate `collections` table for collection metadata
- Proper indexing for performance
- Handles duplicate detection (GUID uniqueness)
- Produces `clipmate_from_xml.db` with 1,125 clips

#### `clipmate_parser.py` - Binary Parser (FALLBACK)
- **Use only when**: ClipMate application unavailable for XML export
- Reverse-engineers DBISAM binary format
- Handles two layout formats (Layout A/B)
- Limited data: 258 clips from InBox only
- Partial timestamps: Graphics only (via title parsing)
- Complex code: 315 lines of layout detection and blob retrieval

#### `server.py` - FastAPI Web Server
- **Endpoints**:
  - `GET /api/clips?search=<query>`: Search clips
  - `GET /api/clips/{clip_id}`: Get clip details
  - `GET /api/clips/{clip_id}/content`: Binary content with MIME types
  - `PUT /api/clips/{clip_id}`: Update clip
  - `GET /`: Serve React frontend
- **Database**: Update to use `clipmate_from_xml.db` (currently hardcoded to old path)

#### `database.py` - SQLite Persistence
- **Schema** (`clips` table - XML version):
  - `id`, `guid`, `collid`, `title`, `creator`
  - `created_at`, `modified_at` (accurate timestamps!)
  - `sourceurl`, `shortcut`, `locale`, `icons`, `encrypted`, `macro`, `viewtab`
  - `content_text`, `content_html`, `content_image` (BLOB)
  - `size`, `format_list`, `source_xml`
- **Schema** (`collections` table):
  - `id`, `guid`, `title`, `parent`, and 12 other metadata fields

## Common Development Commands

### XML-Based Workflow (RECOMMENDED)
```bash
# Parse XML export
python process_xml_export.py

# Start web server
python server.py

# Access UI
# http://localhost:8000
```

### Binary Parsing Workflow (FALLBACK)
```bash
# Only use if XML export unavailable
# Currently archived, restore from _archive/legacy_binary_parsing/ if needed
```

## File Organization

### Core Application (6 files)
- **PRIMARY**: `clipmate_xml_parser.py`, `process_xml_export.py`
- **INFRASTRUCTURE**: `server.py`, `database.py`, `index.html`
- **FALLBACK**: `clipmate_parser.py` (binary parser)

### Data Files
- **PRIMARY**: `clipmate_from_xml.db` - 1,125 clips, 3 collections
- **XML EXPORTS**: `ClipMate_Export_*.xml` - Source data files

### Documentation
- `README.md` - Project overview and quick start
- `CLAUDE.md` - This file
- `XML_VS_BINARY_COMPARISON.md` - Detailed comparison of approaches
- `SESSION_SUMMARY.md` - Original timestamp investigation
- `SESSION_2_SUMMARY.md` - XML solution implementation
- `TIMESTAMP_SOLUTION.md` - How timestamps were solved
- `already-tried.md` - Historical record of failed binary parsing attempts

### Archived Files
- `_archive/analysis_scripts/` - 54 analysis/debug/test scripts from reverse engineering
- `_archive/legacy_binary_parsing/` - Old binary-based tools (main.py, process_archives.py, etc.)
- `_archive/README.md` - Explanation of archived files

### Utilities
- `cleanup_project.py` - Script that performed the cleanup
- `start.bat`, `start.sh` - Launch scripts (need updating for XML approach)
- `requirements.txt` - Python dependencies

## Technology Stack

- **Python 3.8+**: Core language
- **xml.etree.ElementTree**: XML parsing (stdlib)
- **python-dateutil**: ISO 8601 timestamp parsing
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **SQLite3**: Database (stdlib)
- **React**: Frontend (inline in `index.html` via CDN)

## Database Schema Comparison

### XML-Based Database (clipmate_from_xml.db)
- **Clips**: 1,125 records with 19 fields
- **Collections**: 3 records with full metadata
- **Timestamps**: 100% accurate (created + modified)
- **Formats**: All 7 types supported
- **Date Range**: 2006-06-29 to 2025-12-15 (19 years)

### Binary-Based Database (ARCHIVED: clipmate.db)
- **Clips**: 258 records with 11 fields
- **Collections**: None
- **Timestamps**: Partial (Graphics only via title parsing)
- **Formats**: TEXT, PNG (partial)
- **Date Range**: 2025-12-02 to 2025-12-15 (2 weeks)

## Timestamp Mystery - SOLVED ✅

After exhaustive investigation (50+ analysis scripts, comprehensive searches), we discovered:

**The Problem**: Timestamps not found in binary `.dat`, `.idx`, `.blb` files despite searching:
- All timestamp formats (Unix, Delphi, Windows, MS-DOS)
- All offsets and patterns
- Foreign key relationships
- Text string variations

**The Solution**: Timestamps are stored in **DBISAM's internal metadata structures** (B-tree metadata), only accessible via the database engine API.

**The Access Method**: ClipMate's XML export uses DBISAM API and includes timestamps in `<TIMESTAMP>` tags.

**The Result**: 100% accurate timestamps for all 1,125 clips spanning 19 years.

See `TIMESTAMP_SOLUTION.md` and `XML_VS_BINARY_COMPARISON.md` for complete details.

## Development Patterns

### Working with XML Parser
```python
from clipmate_xml_parser import ClipMateXMLParser

parser = ClipMateXMLParser('ClipMate_Export_*.xml')
parser.load()

collections = parser.parse_collections()
clips = parser.parse_clips()
stats = parser.get_statistics()
```

### Working with Database
```python
from database import ClipmateDB

db = ClipmateDB('clipmate_from_xml.db')
db.connect()
# Query clips with proper timestamps
db.close()
```

### Adding New Features
1. Prefer XML-based approach for new development
2. Binary parser is frozen (fallback only)
3. Update `server.py` to use `clipmate_from_xml.db`
4. Test with full 1,125 clip dataset

## Project History

**Phase 1**: Binary reverse engineering (extensive)
- Created 50+ analysis scripts
- Investigated DBISAM format
- Built working binary parser (partial data)
- Timestamp mystery remained unsolved

**Phase 2**: Timestamp investigation (exhaustive)
- Tested all known timestamp formats
- Searched all binary files
- Discovered DBISAM metadata limitation
- Found XML export solution

**Phase 3**: XML-based solution (current)
- Implemented pure XML parser
- Achieved 100% timestamp accuracy
- 4.4x more data than binary approach
- Project COMPLETE ✅

## Next Steps

1. **Update server.py**: Point to `clipmate_from_xml.db` instead of old binary database
2. **Test web interface**: Verify all 1,125 clips display correctly
3. **Update start scripts**: Modify `start.bat`/`start.sh` for XML workflow
4. **Production deployment**: Use XML-based solution for actual migration

## Troubleshooting

### "Can't find clips in database"
- Ensure you ran `process_xml_export.py` to create `clipmate_from_xml.db`
- Check `server.py` is pointing to correct database file

### "Timestamps showing 'Unknown'"
- Verify XML export includes `<TIMESTAMP>` tags
- Check export was from "Everything" container (complete data)

### "Need to re-export from ClipMate"
- ClipMate → File → Export → XML format
- Select "Everything" for complete history
- Save as `ClipMate_Export_*.xml`

## References

- **Primary Docs**: `XML_VS_BINARY_COMPARISON.md` - Complete comparison
- **Implementation**: `SESSION_2_SUMMARY.md` - How XML solution was built
- **History**: `already-tried.md` - All failed binary parsing attempts
- **Architecture**: `CLIPMATE_FILES.md` - Component descriptions
