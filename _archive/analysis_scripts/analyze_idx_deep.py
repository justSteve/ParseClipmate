import struct
import os
import datetime

def analyze_idx_deep():
    path = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.idx'
    print(f"Scanning {path}...")
    
    with open(path, 'rb') as f:
        data = f.read()
        
    # Search for ID 5724 (0x165C)
    # Hex: 5C 16 00 00
    target_id = b'\x5C\x16\x00\x00'
    
    # Search for Date (Unix: 1764624140 -> 0C 07 2E 69)
    target_date = b'\x0C\x07\x2E\x69'
    
    # Search for FileTime (134090761400000000 -> 00 56 1F 66 42 DB 01 00 approx)
    # 01 DB 42 ...
    target_ft_prefix = b'\x01\xDB\x42'
    
    print(f"Searching for ID 5724 ({target_id.hex()})...")
    count_id = data.count(target_id)
    print(f"Found {count_id} occurrences of ID 5724")
    
    start = 0
    for _ in range(count_id):
        idx = data.find(target_id, start)
        if idx == -1: break
        print(f"  At offset {idx}")
        # Print surrounding bytes
        start_ctx = max(0, idx - 40)
        end_ctx = min(len(data), idx + 100)
        print(f"    Context: {data[start_ctx:end_ctx].hex()}")
        start = idx + 1
        
    print(f"\nSearching for Unix Date ({target_date.hex()})...")
    if target_date in data:
        print(f"FOUND Unix Date at {data.index(target_date)}")
    else:
        print("Unix Date NOT FOUND")
        
    print(f"\nSearching for FileTime Prefix ({target_ft_prefix.hex()})...")
    if target_ft_prefix in data:
        print(f"FOUND FileTime Prefix at {data.index(target_ft_prefix)}")
    else:
        print("FileTime Prefix NOT FOUND")

if __name__ == "__main__":
    analyze_idx_deep()
