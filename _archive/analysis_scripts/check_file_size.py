#!/usr/bin/env python3
"""
Check CLIP.dat file size and record count to understand why we're missing records
"""
import os
import struct

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    file_size = os.path.getsize(clip_path)
    print(f"CLIP.dat file size: {file_size:,} bytes")

    record_size = 568
    max_possible_records = file_size // record_size
    print(f"Record size: {record_size} bytes")
    print(f"Maximum possible records: {max_possible_records:,}")

    # Read the file and scan for all IDs
    print("\nScanning file for all record IDs...")
    with open(clip_path, 'rb') as f:
        data = f.read()

    print(f"Read {len(data):,} bytes")

    # Scan every 568-byte chunk and try to read ID from offset 0 (Layout B)
    all_ids = []
    for i in range(0, len(data) - record_size, record_size):
        chunk = data[i:i+record_size]
        record_id = struct.unpack('<I', chunk[0:4])[0]
        if record_id > 0 and record_id < 100000:  # Reasonable range
            all_ids.append((i // record_size, record_id))

    print(f"\nFound {len(all_ids)} potential records")
    print(f"First 10 IDs: {[rid for _, rid in all_ids[:10]]}")
    print(f"Last 10 IDs: {[rid for _, rid in all_ids[-10:]]}")

    # Find records 5959-5969
    target_ids = range(5959, 5970)
    found_targets = [(idx, rid) for idx, rid in all_ids if rid in target_ids]

    if found_targets:
        print(f"\n=== FOUND target records from screenshot ===")
        for record_idx, record_id in found_targets:
            byte_offset = record_idx * record_size
            print(f"Record ID {record_id} at record index {record_idx} (byte offset {byte_offset})")

            # Dump the record
            chunk = data[byte_offset:byte_offset+record_size]

            # Try to parse GUID at offset 454
            guid_bytes = chunk[454:492]
            if b'{' in guid_bytes:
                guid_str = guid_bytes.decode('ascii', errors='ignore').split('\x00')[0]
                print(f"  GUID: {guid_str}")

            # Try to parse title
            title_bytes = chunk[10:422]
            title = title_bytes.decode('mbcs', errors='ignore').split('\x00')[0].strip()
            print(f"  Title: {title[:60]}")

            # Check size field
            size = struct.unpack('<I', chunk[422:426])[0]
            print(f"  Size: {size}")

            print(f"\n  Hex dump at various offsets:")
            for offset in [0, 203, 426, 430, 432, 454, 500, 520, 540, 560]:
                if offset + 8 <= len(chunk):
                    hex_chunk = chunk[offset:offset+8]
                    print(f"    Offset {offset:3d}: {hex_chunk.hex()}")
    else:
        print(f"\nTarget records 5959-5969 NOT FOUND in file")

if __name__ == '__main__':
    main()
