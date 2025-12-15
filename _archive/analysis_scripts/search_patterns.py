import os

def search_patterns():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    files = ['CLIP.dat', 'CLIP.idx']
    
    # Time: 15:22:20 -> 0F 16 14
    pat_time = b'\x0F\x16\x14'
    pat_time_rev = b'\x14\x16\x0F'
    
    # Date: 2025-12-01 -> 07 E9 0C 01 (Year Month Day)
    pat_date_1 = b'\x07\xE9\x0C\x01'
    pat_date_2 = b'\x01\x0C\xE9\x07' # Day Month Year
    pat_date_3 = b'\xE9\x07\x0C\x01' # Year Month Day (LE year)
    pat_date_4 = b'\x01\x0C\x07\xE9' # Day Month Year (LE year)
    
    # Short Year: 25 -> 19
    pat_date_short = b'\x19\x0C\x01'
    
    patterns = {
        "Time (0F 16 14)": pat_time,
        "Time Rev (14 16 0F)": pat_time_rev,
        "Date 1 (07 E9 0C 01)": pat_date_1,
        "Date 2 (01 0C E9 07)": pat_date_2,
        "Date 3 (E9 07 0C 01)": pat_date_3,
        "Date 4 (01 0C 07 E9)": pat_date_4,
        "Date Short (19 0C 01)": pat_date_short
    }
    
    for fname in files:
        path = os.path.join(base_dir, fname)
        print(f"Scanning {path}...")
        with open(path, 'rb') as f:
            data = f.read()
            
            for name, pat in patterns.items():
                if pat in data:
                    print(f"FOUND {name} in {fname} at {data.index(pat)}")
                    # Print context
                    idx = data.index(pat)
                    print(f"  Context: {data[max(0, idx-10):min(len(data), idx+10)].hex()}")

if __name__ == "__main__":
    search_patterns()
