import struct
import os
import datetime
from clipmate_parser import ClipmateParser, clean_string

def debug_dates():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    parser = ClipmateParser(base_dir)
    
    print(f"Scanning CLIP.dat in {base_dir}...")
    
    with open(parser.clip_dat, 'rb') as f:
        # Find header
        header_offset = parser.find_header_offset(f)
        print(f"Header Offset: {header_offset}")
        
        f.seek(header_offset)
        
        count = 0
        while True:
            data = f.read(568)
            if len(data) < 568: break
            
            # Check for valid record
            # if data[0] != 100: # 'd'
            #    continue
                
            count += 1
            if count > 200: break # Check first 200 records
            
            # Try to detect layout
            guid_a = clean_string(data[46:84])
            guid_b = clean_string(data[454:492])
            
            layout = 'Unknown'
            if guid_a.startswith('{') and guid_a.endswith('}'):
                layout = 'A'
            elif guid_b.startswith('{') and guid_b.endswith('}'):
                layout = 'B'
                
            print(f"\nRecord {count}: Layout {layout}")
            
            if layout == 'A':
                # Check Offset 151
                ts = struct.unpack('<I', data[151:155])[0]
                print(f"  Offset 151 (Int32): {ts}")
                if ts > 0:
                    try:
                        dt = datetime.datetime.fromtimestamp(ts)
                        print(f"  Parsed Date: {dt}")
                    except:
                        print("  Invalid Timestamp")
                        
            if layout == 'B':
                # Parse ID
                native_id = struct.unpack('<I', data[0:4])[0]
                print(f"  ID: {native_id}")
                
                # Check Title parsing
                title = clean_string(data[10:100])
                print(f"  Title: {title}")
                
                if title.startswith("Graphic:"):
                    try:
                        date_str = title.split('Graphic:')[1].strip()
                        print(f"  Date String: '{date_str}'")
                        dt = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
                        print(f"  Parsed Date: {dt}")
                    except Exception as e:
                        print(f"  Date Parse Error: {e}")
                
                # Search for ID 5724
                if native_id == 5724:
                    print(f"  Hex Dump of 5724:")
                    print(data.hex())
                    
                    # Check offset 151
                    ts = struct.unpack('<I', data[151:155])[0]
                    print(f"  Offset 151 (Int32): {ts}")
                    try:
                        dt = datetime.datetime.fromtimestamp(ts)
                        print(f"  Parsed Date at 151: {dt}")
                    except:
                        print("  Invalid Timestamp at 151")
                    break
                    print(f"  Hex Dump of 5724:")
                    print(data.hex())
                    break

if __name__ == "__main__":
    debug_dates()
