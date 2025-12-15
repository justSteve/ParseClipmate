import struct
import os

def analyze_idx_offsets():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    clip_dat = os.path.join(base_dir, 'CLIP.dat')
    clip_idx = os.path.join(base_dir, 'CLIP.idx')
    
    # 1. Calculate exact offset of ID 5724 in CLIP.dat
    print(f"Analyzing {clip_dat} to find offset of ID 5724...")
    offset_5724 = -1
    with open(clip_dat, 'rb') as f:
        # Simple heuristic to find the header/start
        data = f.read(20000)
        # Look for the first "Layout B" GUID or just scan for ID 5724
        # ID 5724 hex: 5C 16 00 00
        # But we need to be careful about alignment.
        # Let's just scan the whole file for the ID 5724 signature at 568-byte intervals?
        # No, let's just find the byte offset of the ID.
        f.seek(0)
        full_data = f.read()
        target_id = b'\x5C\x16\x00\x00'
        
        count = full_data.count(target_id)
        print(f"Found {count} occurrences of ID 5724 in CLIP.dat")
        
        start = 0
        for _ in range(count):
            idx = full_data.find(target_id, start)
            print(f"  ID 5724 found at offset {idx}")
            offset_5724 = idx
            start = idx + 1
            
            # Check if this looks like a record start
            # Layout B has GUID at offset 454?
            # Or maybe the ID is at offset 0?
            # In parser we assume ID is at offset 0.
            
    if offset_5724 != -1:
        print(f"\nSearching for offset {offset_5724} (0x{offset_5724:08X}) in CLIP.idx...")
        val_bytes = struct.pack('<I', offset_5724)
        print(f"Target bytes: {val_bytes.hex()}")
        
        with open(clip_idx, 'rb') as f:
            idx_data = f.read()
            if val_bytes in idx_data:
                print(f"FOUND Offset {offset_5724} in CLIP.idx at {idx_data.index(val_bytes)}")
                # Print context
                loc = idx_data.index(val_bytes)
                print(f"  Context: {idx_data[max(0, loc-20):min(len(idx_data), loc+20)].hex()}")
            else:
                print("Offset NOT FOUND in CLIP.idx")

if __name__ == "__main__":
    analyze_idx_offsets()
