# Clipmate Parser Project Files

This document describes the key files and components of the Clipmate Parser application.

## Core Application Files

### `clipmate_parser.py`
**Purpose**: The core parsing logic for Clipmate data files (`CLIP.dat`, `BLOB*.dat`, `BLOB*.blb`).
**Key Classes**:
- `ClipmateParser`: Main class for parsing `CLIP.dat`. Handles record iteration, layout detection (Layout A vs. Layout B), and field extraction (ID, Title, Date, Size, etc.).
- `BlobManager`: Manages the index of blob data (images, rich text) stored in `.dat` and `.blb` files. Provides methods to retrieve blob content by Clip ID.
**Key Functions**:
- `clean_string`: Utility to decode and clean text strings from binary data.
- `find_header_offset`: Heuristic to detect the start of records in `CLIP.dat`.

### `server.py`
**Purpose**: A FastAPI web server that exposes the parsed data via a REST API.
**Endpoints**:
- `GET /api/clips`: Search and retrieve a list of clips. Supports searching by Title, Content, or ID.
- `GET /api/clips/{clip_id}`: Retrieve details for a specific clip.
- `GET /api/clips/{clip_id}/content`: Retrieve binary content (e.g., images) for a clip.
- `/`: Serves the `index.html` frontend.

### `database.py`
**Purpose**: Handles SQLite database interactions.
**Key Functions**:
- `init_db`: Creates the `clips` table if it doesn't exist.
- `insert_clip`: Inserts or updates a clip record in the database.
- `get_db_connection`: Returns a connection to `clipmate.db`.

### `index.html`
**Purpose**: The frontend user interface for browsing and searching clips.
**Features**:
- React-based single-page application (served statically).
- Search bar for filtering clips by text or ID.
- Split-view layout: List of clips on the left, details/content on the right.
- Displays images for "Graphic" clips using the `/content` API.

### `process_archives.py`
**Purpose**: A utility script to batch process multiple Clipmate archives.
**Functionality**:
- Scans a directory for `.zip` archives containing Clipmate data.
- Extracts each archive to a temporary location.
- Runs the parser on the extracted data.
- Populates the database with data from all archives, tagging them with the source archive name.

### `main.py`
**Purpose**: The entry point for parsing the "Live" Clipmate data (from the user's AppData directory).
**Functionality**:
- Connects to the live data directory.
- Parses `CLIP.dat`.
- Updates the database.

### `requirements.txt`
**Purpose**: Lists Python dependencies required to run the application.
**Content**: `fastapi`, `uvicorn`, `pydantic`.

## Data Files

- `clipmate.db`: The SQLite database where parsed clip metadata is stored.
- `CLIP.dat`: The main Clipmate data file containing clip metadata (ID, Title, etc.).
- `BLOB*.dat` / `BLOB*.blb`: Files storing binary data (images, large text) referenced by clips.

## Usage

1.  **Start the Server**:
    ```bash
    python server.py
    ```
    The UI will be available at `http://localhost:8000/`.

2.  **Reprocess All Data**:
    ```bash
    python process_archives.py
    ```
    This will clear the database and re-import data from both the live directory and any archives in the `archives/` folder.
