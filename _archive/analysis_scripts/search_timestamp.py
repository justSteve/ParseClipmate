import struct
import os

def search_ts():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    # List all files
    files = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))]
    
    # Target: 1764624140 (0x692E070C)
    target_le = b'\x0C\x07\x2E\x69'
    target_be = b'\x69\x2E\x07\x0C'
    
    for fname in files:
        path = os.path.join(base_dir, fname)
        print(f"Scanning {path}...")
        with open(path, 'rb') as f:
            data = f.read()
            
            if target_le in data:
                print(f"FOUND LE in {fname} at {data.index(target_le)}")
            if target_be in data:
                print(f"FOUND BE in {fname} at {data.index(target_be)}")
                
            # Search for FileTime: 134090761400000000
            # Hex: 01 DB 42 66 1F 56 00 00 (approx)
            # Let's search for just the top bytes: 01 DB 42
            if b'\x01\xDB\x42' in data:
                 print(f"FOUND FileTime prefix in {fname} at {data.index(b'\x01\xDB\x42')}")

if __name__ == "__main__":
    search_ts()
