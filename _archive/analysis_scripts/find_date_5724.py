import struct
import os
import datetime
from clipmate_parser import ClipmateParser, clean_string

def find_date():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    parser = ClipmateParser(base_dir)
    
    with open(parser.clip_dat, 'rb') as f:
        header_offset = parser.find_header_offset(f)
        f.seek(header_offset)
        
        count = 0
        while True:
            data = f.read(568)
            if len(data) < 568: break
            
            # Check for Layout B ID 5724
            try:
                native_id = struct.unpack('<I', data[0:4])[0]
                print(f"ID: {native_id}")
                if native_id == 5724:
                    print("Found ID 5724")
                    print(f"Hex: {data.hex()}")
                    
                    # Targets
                    targets = {
                        "Unix": 1764624140,
                        "TDateTime": 45992.64,
                        "FileTime": 133775017400000000,
                        "DOS": 0x5B817ACA # or 7ACA5B81
                    }
                    
                    # Scan Int32
                    for i in range(len(data)-4):
                        val = struct.unpack('<I', data[i:i+4])[0]
                        if val == targets["Unix"]:
                            print(f"MATCH Unix at {i}")
                        if val == targets["DOS"] or val == 0x7ACA5B81:
                            print(f"MATCH DOS at {i}")
                            
                    # Scan Double
                    for i in range(len(data)-8):
                        val = struct.unpack('<d', data[i:i+8])[0]
                        if abs(val - targets["TDateTime"]) < 1.0:
                            print(f"MATCH TDateTime at {i}: {val}")
                            
                    # Scan Int64
                    for i in range(len(data)-8):
                        val = struct.unpack('<Q', data[i:i+8])[0]
                        if abs(val - targets["FileTime"]) < 1000000000:
                            print(f"MATCH FileTime at {i}: {val}")
                            
                    return
            except: pass
            
            count += 1
            if count > 2000: break

if __name__ == "__main__":
    find_date()
