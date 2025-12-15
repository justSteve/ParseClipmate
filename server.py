from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

DB_PATH = os.path.join(os.path.dirname(__file__), 'clipmate_from_xml.db')

class Clip(BaseModel):
    id: int
    guid: Optional[str]
    title: Optional[str]
    creator: Optional[str]
    url: Optional[str]
    content_text: Optional[str]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/clips")
def get_clips(search: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get collection names for display
    query = """
        SELECT
            c.id, c.guid, c.title, c.creator, c.created_at, c.modified_at,
            c.sourceurl, c.size, c.format_list, c.collid,
            col.title as collection_name
        FROM clips c
        LEFT JOIN collections col ON c.collid = col.guid
    """

    if search:
        query += " WHERE c.title LIKE ? OR c.content_text LIKE ? OR c.creator LIKE ?"
        query += " ORDER BY c.created_at DESC LIMIT 100"
        cursor.execute(query, (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        query += " ORDER BY c.created_at DESC LIMIT 100"
        cursor.execute(query)

    clips = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clips

@app.get("/api/clips/{clip_id}/content")
def get_clip_content(clip_id: int, content_type: str = "image"):
    """
    Serve clip content (images, HTML, etc.) from BLOB columns
    content_type: 'image' for content_image, 'html' for content_html
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if content_type == "image":
        cursor.execute("SELECT content_image, format_list FROM clips WHERE id = ?", (clip_id,))
    elif content_type == "html":
        cursor.execute("SELECT content_html, format_list FROM clips WHERE id = ?", (clip_id,))
    else:
        cursor.execute("SELECT content_image, format_list FROM clips WHERE id = ?", (clip_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Clip not found")

    content = row[0]
    format_list = row[1] or ""

    if not content:
        raise HTTPException(status_code=404, detail="No content available")

    # Determine MIME type from format_list
    media_type = "application/octet-stream"
    if "PNG" in format_list:
        media_type = "image/png"
    elif "JPG" in format_list or "JPEG" in format_list:
        media_type = "image/jpeg"
    elif "HTML" in format_list:
        media_type = "text/html"
    elif "RTF" in format_list:
        media_type = "application/rtf"

    return Response(content=content, media_type=media_type)

@app.get("/api/clips/{clip_id}")
def get_clip(clip_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            c.*,
            col.title as collection_name
        FROM clips c
        LEFT JOIN collections col ON c.collid = col.guid
        WHERE c.id = ?
    """, (clip_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    return dict(row)

@app.put("/api/clips/{clip_id}")
def update_clip(clip_id: int, clip: Clip):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clips SET title = ?, content_text = ? WHERE id = ?", (clip.title, clip.content_text, clip_id))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
