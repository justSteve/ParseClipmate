#!/usr/bin/env python3
"""
Analyze blob index files (*.dat) to find foreign key relationships.
These files map record IDs to blob positions in .blb files.
"""
import struct
from datetime import datetime, timedelta
import os

# Known test records
TEST_RECORDS = [
    (6021, "12/14/2025 11:25:30 AM"),
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def parse_timestamp(bytes_4, bytes_8):
    """Try parsing timestamps in multiple formats"""
    results = []

    # Unix 32-bit
    try:
        ts = struct.unpack('<I', bytes_4)[0]
        if 1733000000 < ts < 1735000000:
            results.append(('Unix32', datetime.fromtimestamp(ts), bytes_4.hex()))
    except:
        pass

    # Delphi TDateTime
    try:
        delphi = struct.unpack('<d', bytes_8)[0]
        if 46000 < delphi < 46020:
            dt = datetime(1899, 12, 30) + timedelta(days=delphi)
            results.append(('Delphi', dt, bytes_8.hex()))
    except:
        pass

    # MS-DOS datetime
    try:
        dos = struct.unpack('<I', bytes_4)[0]
        time_part = dos & 0xFFFF
        date_part = (dos >> 16) & 0xFFFF

        if date_part > 0:
            second = (time_part & 0x1F) * 2
            minute = (time_part >> 5) & 0x3F
            hour = (time_part >> 11) & 0x1F
            day = date_part & 0x1F
            month = (date_part >> 5) & 0x0F
            year = ((date_part >> 9) & 0x7F) + 1980

            if 2025 <= year <= 2026 and 1 <= month <= 12 and 1 <= day <= 31:
                dt = datetime(year, month, day, hour, minute, second)
                results.append(('MS-DOS', dt, bytes_4.hex()))
    except:
        pass

    return results

def analyze_blob_index(file_path, test_records):
    """Analyze a blob .dat index file"""
    filename = os.path.basename(file_path)

    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return

    print(f"\n{'='*100}")
    print(f"FILE: {filename} ({len(data):,} bytes)")
    print(f"{'='*100}\n")

    # First, find record IDs
    record_positions = {}
    for record_id, _ in test_records:
        id_bytes = struct.pack('<I', record_id)
        offset = 0
        positions = []
        while True:
            pos = data.find(id_bytes, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1
        if positions:
            record_positions[record_id] = positions

    if not record_positions:
        print(f"No test record IDs found in {filename}")
        return

    print(f"Found {len(record_positions)} test record(s) in index file:\n")

    # For each record ID, analyze the surrounding structure
    for record_id, positions in sorted(record_positions.items()):
        expected_dt = datetime.strptime(dict(test_records)[record_id], "%m/%d/%Y %I:%M:%S %p")

        print(f"Record {record_id} ({dict(test_records)[record_id]}):")
        print(f"  Found at {len(positions)} position(s): {positions}\n")

        for pos in positions:
            # Determine likely record size by looking for next record ID
            record_start = max(0, pos - 100)  # Assume record starts within 100 bytes before ID
            record_end = min(len(data), pos + 200)  # Assume record ends within 200 bytes after ID

            # Extract the record area
            record_data = data[record_start:record_end]

            # Look for timestamps in this record
            print(f"  Position {pos}:")
            print(f"  Hex dump (offset {record_start} to {record_end}):")

            # Hex dump
            for i in range(0, len(record_data), 16):
                chunk = record_data[i:i+16]
                hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
                text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
                abs_offset = record_start + i
                marker = "  <-- ID" if record_start + i <= pos < record_start + i + 16 else ""
                print(f"    {abs_offset:6d}: {hex_str:<48} | {text}{marker}")

            # Search for timestamps
            print(f"\n  Searching for timestamps in this record:")
            found_any = False

            for i in range(0, len(record_data) - 8):
                bytes_4 = record_data[i:i+4]
                bytes_8 = record_data[i:i+8]
                parsed = parse_timestamp(bytes_4, bytes_8)

                for fmt, dt, hex_val in parsed:
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 3600:  # Within 1 hour
                        offset_in_record = i
                        offset_from_id = (record_start + i) - pos
                        marker = " *** MATCH ***" if diff < 60 else ""
                        print(f"    +{offset_in_record:3d} ({offset_from_id:+4d} from ID): {fmt:<10} {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.0f}s){marker}")
                        print(f"        Hex: {hex_val}")
                        found_any = True

            if not found_any:
                print(f"    No matching timestamps found in this record")

            print()

def main():
    base_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"

    # Blob index files to analyze
    blob_indices = [
        "blobpng.dat",
        "BLOBJPG.dat",
        "BLOBBLOB.dat",
        "BLOBTXT.dat",
    ]

    print("="*100)
    print("ANALYZING BLOB INDEX FILES FOR TIMESTAMPS")
    print("="*100)
    print(f"\nThese .dat files map record IDs to blob positions in .blb files")
    print(f"Looking for timestamps stored as metadata in index records\n")

    for filename in blob_indices:
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            analyze_blob_index(file_path, TEST_RECORDS)

if __name__ == '__main__':
    main()
