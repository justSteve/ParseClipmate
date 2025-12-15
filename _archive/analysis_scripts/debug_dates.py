import struct
import os
import datetime
import sys

# Add parent dir to path to import clipmate_parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clipmate_parser import ClipmateParser, clean_string

def debug_dates():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    parser = ClipmateParser(base_dir)
    
    print(f"Scanning CLIP.dat in {base_dir}...")
    
    with open(parser.clip_dat, 'rb') as f:
        header_offset = parser.find_header_offset(f)
        f.seek(header_offset)
        
        count = 0
        while True:
            data = f.read(568)
            if len(data) < 568: break
            
            # Parse ID
            try:
                native_id = struct.unpack('<I', data[0:4])[0]
            except: native_id = 0
            
            # Detect Layout
            layout = 'Unknown'
            guid_a = clean_string(data[46:84])
            guid_b = clean_string(data[454:492])
            
            if guid_a.startswith('{') and guid_a.endswith('}'):
                layout = 'A'
            elif guid_b.startswith('{') and guid_b.endswith('}'):
                layout = 'B'
                
            # Check for ID 5724 (Layout B sample)
            if native_id == 5724:
                print(f"\n--- Record {native_id} (Layout {layout}) ---")
                print(f"Title: {clean_string(data[10:100])}")
                print(f"Hex: {data.hex()}")
                # Look for date patterns
                # Expected: 12/1/2025 3:22:20 PM
                # 2025-12-01 15:22:20
                
            # Check for Graphic Clip (Layout B)
            title = clean_string(data[10:100])
            if title.startswith("Graphic:"):
                print(f"\n--- Graphic Clip (ID {native_id}) ---")
                print(f"Title: {title}")
                try:
                    date_str = title.split('Graphic:')[1].strip()
                    dt = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
                    print(f"Parsed Date from Title: {dt}")
                except Exception as e:
                    print(f"Failed to parse date from title: {e}")

            if count < 20:
                print(f"\nRecord {count}: Layout {layout}, ID {native_id}")
                if layout == 'A':
                    ts = struct.unpack('<I', data[151:155])[0]
                    print(f"  Offset 151: {ts}")
                elif layout == 'B':
                    print(f"  Title: {title}")

            count += 1
            if count > 3000: break

if __name__ == "__main__":
    debug_dates()
