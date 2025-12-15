import os
import zipfile
import glob
from clipmate_parser import ClipmateParser
from database import ClipmateDB

def process_archives():
    base_dir = r'c:/myStuff/ParseClipmate'
    archives_dir = os.path.join(base_dir, 'archives')
    sample_data_dir = os.path.join(base_dir, 'sample Clipmate data')
    db_path = os.path.join(base_dir, 'clipmate.db')
    
    # Ensure DB is fresh for this run (optional, but good for testing)
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("Initializing database...")
    db = ClipmateDB(db_path)
    db.connect()
    
    # 1. Process Live Data first
    live_data_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    print(f"Processing Live Data from {live_data_dir}...")
    parser = ClipmateParser(live_data_dir)
    clips = parser.parse_clips()
    print(f"  Found {len(clips)} clips.")
    for clip in clips:
        try:
            db.insert_clip(clip, source_archive="LIVE_DATA")
        except Exception as e:
            print(f"  Error inserting clip {clip.get('id')}: {e}")
            
    # 2. Find and Process Archives -- uncomment only after verifying Live Data works
#    zip_files = glob.glob(os.path.join(sample_data_dir, '*.ZIP'))
    # print(f"Found {len(zip_files)} archives.")
    
    # for zip_file in zip_files:
    #     archive_name = os.path.splitext(os.path.basename(zip_file))[0]
    #     extract_path = os.path.join(archives_dir, archive_name)
        
    #     print(f"Processing archive: {archive_name}")
        
    #     if not os.path.exists(extract_path):
    #         print(f"  Extracting to {extract_path}...")
    #         with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    #             zip_ref.extractall(extract_path)
    #     else:
    #         print(f"  Already extracted at {extract_path}")
            
    #     # Parse
    #     parser = ClipmateParser(extract_path)
    #     clips = parser.parse_clips()
    #     print(f"  Found {len(clips)} clips.")
        
    #     count = 0
    #     for clip in clips:
    #         try:
    #             db.insert_clip(clip, source_archive=archive_name)
    #             count += 1
    #         except Exception as e:
    #             pass
    #     print(f"  Imported {count} clips from {archive_name}")

    # db.close()
    # print("Done processing all archives.")

if __name__ == "__main__":
    process_archives()
