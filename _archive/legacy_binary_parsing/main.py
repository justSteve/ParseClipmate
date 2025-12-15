from clipmate_parser import ClipmateParser
from database import ClipmateDB
import os

def main():
    # base_dir = os.path.join(os.path.dirname(__file__), 'exploration')
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    db_path = os.path.join(os.path.dirname(__file__), 'clipmate.db')
    
    # Initialize DB
    print("Initializing database...")
    db = ClipmateDB(db_path)
    db.connect()
    
    # Parse Clips
    print("Parsing clips...")
    parser = ClipmateParser(base_dir)
    clips = parser.parse_clips()
    
    # Parse BLOBs
    print("Parsing text blobs...")
    blobs = parser.parse_blobtxt()
    
    # Map blobs to clips
    print("Mapping blobs to clips...")
    blob_map = {b['clip_id']: b['content'] for b in blobs}
    
    # Export
    print(f"Exporting {len(clips)} records to database...")
    count = 0
    for clip in clips:
        # Link content
        # Note: clip['id'] is just the index, we might need to match the actual ID from the file if 'id' in blob is different.
        # But for now let's assume the 'id' in blob corresponds to the record index or an ID field we parsed.
        # Wait, in parse_clips we didn't parse an explicit ID field, we just used index.
        # The blob has 'clip_id'. We need to find where 'clip_id' is in CLIP.dat.
        # In the hexdump, 'CLIP_ID' was a field.
        # Let's assume the first 4 bytes of CLIP.dat record might be the ID?
        # Or we just try to match by index if ID is sequential.
        
        # Let's try to find the ID in the raw data of the clip if possible, 
        # but for now, let's just try to match by index if the IDs look like 1, 2, 3...
        # If blob IDs are large (like 1024), maybe they are offsets?
        
        # Let's just store the blob map for now and try to link later or just store what we have.
        # Actually, let's try to match:
        # If we found a 'clip_id' in the blob, we should try to use it.
        
        # For this version, let's just insert the clip metadata.
        # If we have a match in blob_map, add it.
        # We need to know the ID of the clip.
        # Let's assume the first 4 bytes of the clip record is the ID.
        try:
            clip_id = struct.unpack('<I', clip['raw_data'][:4])[0]
            if clip_id in blob_map:
                clip['content_text'] = blob_map[clip_id]
        except:
            pass

        try:
            if count < 5:
                with open('debug_log.txt', 'a') as log:
                    log.write(f"Inserting clip {clip.get('id')}: URL='{clip.get('url')}' Title='{clip.get('title')}'\n")
            db.insert_clip(clip)
            count += 1
        except Exception as e:
            print(f"Failed to insert clip {clip.get('id')}: {e}")
            
    db.close()
    print(f"Done. Successfully exported {count} records to {db_path}")

if __name__ == "__main__":
    main()
