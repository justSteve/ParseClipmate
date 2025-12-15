#!/usr/bin/env python3
"""
Search for foreign key relationships between record IDs and timestamps.
Focus on .idx files and ClipData.dat which likely contain linking tables.
"""
import struct
from datetime import datetime, timedelta
import os

# Known test records from mostrecent.jpg
TEST_RECORDS = [
    (6021, "12/14/2025 11:25:30 AM"),
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def find_record_id_with_timestamp(data, record_id, expected_dt):
    """Find record ID and check for timestamps within nearby bytes"""
    id_bytes = struct.pack('<I', record_id)
    positions = []
    offset = 0

    while True:
        pos = data.find(id_bytes, offset)
        if pos == -1:
            break
        positions.append(pos)
        offset = pos + 1

    results = []
    for pos in positions:
        # Check within ±100 bytes for timestamps
        search_start = max(0, pos - 100)
        search_end = min(len(data), pos + 100)

        # Try Unix timestamp (4 bytes)
        for i in range(search_start, search_end - 4):
            try:
                ts = struct.unpack('<I', data[i:i+4])[0]
                if 1733000000 < ts < 1735000000:  # Dec 2025 range
                    dt = datetime.fromtimestamp(ts)
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 60:  # Match within 60 seconds
                        offset_from_id = i - pos
                        results.append({
                            'format': 'Unix32',
                            'id_offset': pos,
                            'ts_offset': i,
                            'offset_from_id': offset_from_id,
                            'found_dt': dt,
                            'diff_seconds': diff,
                            'hex': data[i:i+4].hex()
                        })
            except:
                pass

        # Try Delphi TDateTime (8 bytes)
        for i in range(search_start, search_end - 8):
            try:
                delphi = struct.unpack('<d', data[i:i+8])[0]
                if 46000 < delphi < 46020:  # Dec 2025 range
                    dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 60:
                        offset_from_id = i - pos
                        results.append({
                            'format': 'Delphi',
                            'id_offset': pos,
                            'ts_offset': i,
                            'offset_from_id': offset_from_id,
                            'found_dt': dt,
                            'diff_seconds': diff,
                            'hex': data[i:i+8].hex()
                        })
            except:
                pass

    return results

def analyze_file(file_path, test_records):
    """Analyze a file for record ID + timestamp patterns"""
    filename = os.path.basename(file_path)

    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

    print(f"\n{'='*100}")
    print(f"FILE: {filename} ({len(data):,} bytes)")
    print(f"{'='*100}")

    all_results = []

    for record_id, timestamp_str in test_records:
        expected_dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")
        results = find_record_id_with_timestamp(data, record_id, expected_dt)

        if results:
            print(f"\n[+] Record {record_id} - Expected: {timestamp_str}")
            for r in results:
                print(f"  Found at offset {r['id_offset']:6d}")
                print(f"  Timestamp at offset {r['ts_offset']:6d} ({r['offset_from_id']:+4d} from ID)")
                print(f"  Format: {r['format']} = {r['found_dt'].strftime('%m/%d/%Y %I:%M:%S %p')}")
                print(f"  Difference: {r['diff_seconds']:.1f} seconds")
                print(f"  Hex: {r['hex']}")
                print()
            all_results.extend(results)
        else:
            # Check if record ID exists at all
            id_bytes = struct.pack('<I', record_id)
            if id_bytes in data:
                pos = data.find(id_bytes)
                print(f"\n[-] Record {record_id} found at offset {pos:6d}, but NO matching timestamp nearby")
            else:
                print(f"\n[-] Record {record_id} NOT FOUND in this file")

    if all_results:
        # Analyze pattern
        print(f"\n{'='*100}")
        print(f"PATTERN ANALYSIS for {filename}")
        print(f"{'='*100}\n")

        offsets_from_id = [r['offset_from_id'] for r in all_results]
        formats = set(r['format'] for r in all_results)

        print(f"Total matches: {len(all_results)}")
        print(f"Timestamp format(s): {', '.join(formats)}")
        print(f"Offset from record ID:")
        for offset in set(offsets_from_id):
            count = offsets_from_id.count(offset)
            print(f"  {offset:+4d} bytes: {count} occurrence(s)")

        if len(set(offsets_from_id)) == 1:
            print(f"\n*** CONSISTENT PATTERN: Timestamp is always at {offsets_from_id[0]:+d} bytes from record ID ***")

    return all_results

def main():
    base_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"

    # Files to analyze (most likely to contain foreign key mappings)
    target_files = [
        "CLIP.idx",
        "ClipData.dat",
        "ClipData.idx",
        "CLIP.dat",  # Re-check with wider search range
    ]

    print("="*100)
    print("SEARCHING FOR FOREIGN KEY TIMESTAMP RELATIONSHIPS")
    print("="*100)
    print(f"\nTesting {len(TEST_RECORDS)} known records")
    print(f"Looking for record IDs paired with timestamps within ±100 bytes\n")

    all_file_results = {}

    for filename in target_files:
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            results = analyze_file(file_path, TEST_RECORDS)
            if results:
                all_file_results[filename] = results
        else:
            print(f"\nFile not found: {filename}")

    print(f"\n\n{'='*100}")
    print("SUMMARY")
    print(f"{'='*100}\n")

    if all_file_results:
        print(f"TIMESTAMPS FOUND in {len(all_file_results)} file(s):\n")
        for filename, results in all_file_results.items():
            print(f"  {filename}: {len(results)} match(es)")
        print("\n*** THIS IS THE FOREIGN KEY RELATIONSHIP! ***")
    else:
        print("NO timestamp/record ID pairings found.")
        print("\nNext steps:")
        print("  1. Examine record structure in .idx files more carefully")
        print("  2. Check if .idx files use block/page-based indexing")
        print("  3. Analyze ClipData.dat structure (we found IDs there before)")

if __name__ == '__main__':
    main()
