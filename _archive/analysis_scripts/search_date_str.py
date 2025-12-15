import os

def search_str():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    # List all files
    files = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))]
    
    # Target: 2025-12-01
    patterns = {
        b'12012025', b'01122025', b'20251201',
        b'12-01-2025', b'01-12-2025', b'2025-12-01',
        b'12.01.2025', b'01.12.2025', b'2025.12.01',
        b'12/01/2025', b'01/12/2025', b'2025/12/01',
        b'12 01 2025', b'01 12 2025', b'2025 12 01'
    }
    
    for fname in files:
        path = os.path.join(base_dir, fname)
        # Skip large blobs to save time, focus on metadata files
        if 'BLOB' in fname and 'idx' not in fname: continue
        
        print(f"Scanning {path}...")
        with open(path, 'rb') as f:
            data = f.read()
            
            for pat in patterns:
                count = data.count(pat)
                if count > 0:
                    print(f"Found {count} occurrences of '{pat.decode()}' in {fname}")
                    # Print context of first few
                    start = 0
                    for _ in range(min(5, count)):
                        idx = data.find(pat, start)
                        if idx == -1: break
                        print(f"  At {idx}: {data[max(0, idx-20):min(len(data), idx+30)]}")
                        start = idx + 1

if __name__ == "__main__":
    search_str()
