from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
from pydantic import BaseModel
from typing import Optional
from clipmate_parser import BlobManager

app = FastAPI()

# Initialize BlobManager
BASE_DIR = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
blob_manager = BlobManager(BASE_DIR)

DB_PATH = os.path.join(os.path.dirname(__file__), 'clipmate.db')

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
    if search:
        # Check if search is numeric for ID search
        if search.isdigit():
            cursor.execute("SELECT id, title, creator, url, source_archive, created_at, size, native_id FROM clips WHERE native_id = ? OR title LIKE ? OR content_text LIKE ? LIMIT 100", (int(search), f'%{search}%', f'%{search}%'))
        else:
            cursor.execute("SELECT id, title, creator, url, source_archive, created_at, size, native_id FROM clips WHERE title LIKE ? OR content_text LIKE ? LIMIT 100", (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("SELECT id, title, creator, url, source_archive, created_at, size, native_id FROM clips LIMIT 100")
    clips = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clips

@app.get("/api/clips/{clip_id}/content")
def get_clip_content(clip_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT native_id, size FROM clips WHERE id = ?", (clip_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Clip not found")
        
    native_id = row['native_id']
    size = row['size']
    
    if not native_id or not size:
        raise HTTPException(status_code=404, detail="No content available")
        
    result = blob_manager.get_blob(native_id, size)
    if not result:
        raise HTTPException(status_code=404, detail="Blob not found")
        
    data, filename = result
    
    # Determine MIME type
    media_type = "application/octet-stream"
    if "png" in filename:
        media_type = "image/png"
    elif "JPG" in filename:
        media_type = "image/jpeg"
        
    return Response(content=data, media_type=media_type)

@app.get("/api/clips/{clip_id}")
def get_clip(clip_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips WHERE id = ?", (clip_id,))
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
