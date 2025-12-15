#!/usr/bin/env python3
"""
Find the timestamp pattern by examining multiple records
Record 6018 is at offset 128,168
"""
import struct
from datetime import datetime, timedelta

def examine_record(data, file_offset, expected_id, expected_dt_str):
    """Examine a single 568-byte record"""
    record = data[file_offset:file_offset + 568]

    print(f"\n{'='*100}")
    print(f"Record at offset {file_offset}")
    print(f"Expected ID: {expected_id}, Expected DateTime: {expected_dt_str}")
    print(f"{'='*100}")

    # Parse ID at offset +4
    actual_id = struct.unpack('<I', record[4:8])[0]
    print(f"Actual ID at offset +4: {actual_id}")

    if actual_id != expected_id:
        print(f"  WARNING: ID mismatch! Expected {expected_id}, got {actual_id}")
        return

    expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")

    # Look for timestamps at key offsets
    candidate_offsets = [160, 164, 448, 452, 528, 532, 560]

    print(f"\nChecking candidate timestamp locations:")

    for offset in candidate_offsets:
        if offset + 8 > len(record):
            continue

        bytes_8 = record[offset:offset+8]
        bytes_4 = record[offset:offset+4]

        # Try Unix timestamp
        try:
            ts = struct.unpack('<I', bytes_4)[0]
            if 1733000000 < ts < 1735000000:  # Dec 2025 range
                dt = datetime.fromtimestamp(ts)
                diff = abs((dt - expected_dt).total_seconds())
                marker = " *** MATCH ***" if diff < 60 else ""
                print(f"  Offset +{offset}: Unix32 = {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s){marker}")
        except:
            pass

        # Try Delphi TDateTime
        try:
            delphi = struct.unpack('<d', bytes_8)[0]
            if 46000 < delphi < 46020:  # Dec 2025 range
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                diff = abs((dt - expected_dt).total_seconds())
                marker = " *** MATCH ***" if diff < 60 else ""
                print(f"  Offset +{offset}: Delphi = {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s){marker}")
        except:
            pass

    # Show hex at key offsets
    print(f"\nHex dump at key offsets:")
    for offset in candidate_offsets:
        if offset + 8 <= len(record):
            hex_val = record[offset:offset+8].hex()
            print(f"  Offset +{offset:3d}: {hex_val}")

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        data = f.read()

    print(f"CLIP.dat size: {len(data):,} bytes")

    # Test records from mostrecent.jpg
    # We know record 6018 is at offset 128,168
    # Records are 568 bytes, so we can calculate offsets for adjacent records

    test_records = [
        (128168, 6018, "12/14/2025 9:35:03 AM"),
        (128168 + 568, 6019, "12/14/2025 10:38:01 AM"),  # Next record
        (128168 - 568, 6017, "12/14/2025 8:58:00 AM"),  # Previous record
        (128168 + 568*2, 6020, "12/14/2025 10:38:25 AM"),  # Two ahead
    ]

    for file_offset, expected_id, expected_dt_str in test_records:
        if 0 <= file_offset < len(data):
            examine_record(data, file_offset, expected_id, expected_dt_str)
        else:
            print(f"\nOffset {file_offset} is out of bounds")

if __name__ == '__main__':
    main()
