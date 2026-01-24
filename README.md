# ParseClipmate

A tool for migrating data from ClipMate (discontinued clipboard manager) to SQLite, with a web-based viewer.

## QuickStart

```bash
# 1. Start the server
./start.sh

# 2. Open browser
# http://localhost:8000
```

**Prerequisites:**
- Python 3.8+
- ClipMate XML export file (or existing `clipmate_from_xml.db`)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ParseClipmate                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │  ClipMate    │    │  XML Parser      │    │  SQLite          │   │
│  │  XML Export  │───▶│  clipmate_xml_   │───▶│  Database        │   │
│  │  (.xml)      │    │  parser.py       │    │  (.db)           │   │
│  └──────────────┘    └──────────────────┘    └────────┬─────────┘   │
│                                                        │             │
│                                                        ▼             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     FastAPI Server                            │   │
│  │                     server.py:8000                            │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  GET  /api/clips          - List clips (searchable)          │   │
│  │  GET  /api/clips/{id}     - Get clip details                 │   │
│  │  GET  /api/clips/{id}/content - Get image/HTML content       │   │
│  │  PUT  /api/clips/{id}     - Update clip (requires API key)   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    React Web UI                               │   │
│  │                    index.html                                 │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  • Sortable clip table with search                           │   │
│  │  • Content preview (text, HTML, images)                      │   │
│  │  • Collection filtering                                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| **XML Parsing** | Parse ClipMate's XML export format (1,125+ clips) |
| **Multiple Formats** | TEXT, PNG, HTML, RTF, PICTURE, HDROP, FileName |
| **Web Viewer** | React-based UI with search and content preview |
| **REST API** | FastAPI endpoints for programmatic access |
| **Image Support** | View embedded screenshots and images |
| **HTML Preview** | Sandboxed iframe preview of HTML clips |
| **Search** | Full-text search across titles, content, creators |
| **Collections** | Organize clips by ClipMate collection |

## Configuration

Environment variables for customization:

| Variable | Default | Description |
|----------|---------|-------------|
| `CLIPMATE_API_KEY` | *(none)* | Enable API key authentication for write operations |
| `CLIPMATE_HOST` | `127.0.0.1` | Server bind address (use `0.0.0.0` for network access) |
| `CLIPMATE_PORT` | `8000` | Server port |

**Security Notes:**
- Server binds to localhost only by default (not exposed to network)
- Set `CLIPMATE_API_KEY` in production to protect write operations
- HTML content is displayed in sandboxed iframes to prevent XSS

### Example with Authentication

```bash
export CLIPMATE_API_KEY="your-secret-key"
./start.sh

# API calls require X-Api-Key header for PUT operations
curl -X PUT http://localhost:8000/api/clips/1 \
  -H "X-Api-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

## Data Import

### From ClipMate XML Export (Recommended)

1. In ClipMate: **File → Export → XML** (select "Everything")
2. Edit `process_xml_export.py` to set correct paths
3. Run:
   ```bash
   python process_xml_export.py
   ```
4. Creates `clipmate_from_xml.db` with full clip history

### Database Schema

**clips table:**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| guid | TEXT | Unique ClipMate identifier |
| collid | TEXT | Collection GUID |
| title | TEXT | Clip title |
| creator | TEXT | Source application |
| created_at | TEXT | Creation timestamp |
| modified_at | TEXT | Last modified timestamp |
| sourceurl | TEXT | Source URL (for web clips) |
| content_text | TEXT | Plain text content |
| content_html | BLOB | HTML content |
| content_image | BLOB | Image data (PNG/JPEG) |
| size | INTEGER | Content size in bytes |
| format_list | TEXT | Available formats |

**collections table:**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| guid | TEXT | Unique identifier |
| title | TEXT | Collection name |
| parent | TEXT | Parent collection GUID |

## API Reference

### List Clips
```http
GET /api/clips?search={query}
```
Returns up to 100 clips, sorted by creation date (newest first).

**Response:**
```json
[
  {
    "id": 1,
    "guid": "abc-123",
    "title": "My Clip",
    "creator": "notepad.exe",
    "created_at": "2024-01-15T10:30:00",
    "format_list": "TEXT, HTML",
    "collection_name": "InBox"
  }
]
```

### Get Clip Details
```http
GET /api/clips/{id}
```
Returns full clip metadata (excludes binary content).

### Get Clip Content
```http
GET /api/clips/{id}/content?content_type={type}
```
- `content_type=image` - Returns image data (PNG/JPEG)
- `content_type=html` - Returns HTML content

### Update Clip
```http
PUT /api/clips/{id}
```
Requires `X-Api-Key` header if `CLIPMATE_API_KEY` is set.

## Project Structure

```
parseClipmate/
├── server.py              # FastAPI server
├── index.html             # React web UI
├── start.sh               # Startup script
├── process_xml_export.py  # XML to SQLite processor
├── clipmate_xml_parser.py # XML parsing library
├── clipmate_parser.py     # Binary parser (legacy)
├── database.py            # Database utilities
├── requirements.txt       # Python dependencies
├── clipmate_from_xml.db   # SQLite database (generated)
└── _archive/              # Legacy analysis scripts
```

## Development

### Running Locally

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python server.py
```

### Requirements

- fastapi
- uvicorn
- pydantic
- python-multipart

## Known Issues

See `.beads/issues.jsonl` for tracked issues:

| Priority | Issue |
|----------|-------|
| P3 | Hardcoded Windows paths in some scripts |
| P3 | Bare except clauses hide errors |
| P3 | database.py lacks error handling |
| P4 | Debug print statements should use logging |
| P4 | index.html uses development CDN builds |

## Parsing Approaches

### XML Parsing (Recommended)
- **Coverage:** 1,125 clips from 3 collections (19 years)
- **Accuracy:** 100% timestamp accuracy
- **Formats:** TEXT, PNG, HTML, RTF, PICTURE, HDROP, FileName
- **Complexity:** Simple, maintainable

### Binary Parsing (Legacy)
- **Coverage:** 258 clips from InBox only
- **Accuracy:** Partial timestamps (graphics only)
- **Formats:** TEXT, PNG (partial)
- **Complexity:** Requires DBISAM reverse engineering

See [XML_VS_BINARY_COMPARISON.md](XML_VS_BINARY_COMPARISON.md) for detailed comparison.

## Screenshot

![ClipMate Viewer](image.png)
