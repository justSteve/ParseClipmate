#!/usr/bin/env python3
"""
Comprehensive search for timestamps across ALL ClipMate files.
Tests the 4 most common timestamp formats against known records from mostrecent.jpg.
"""
import struct
import os
from datetime import datetime, timedelta
from pathlib import Path

# Known records from mostrecent.jpg (ID and timestamp)
KNOWN_RECORDS = [
    (6021, "12/14/2025 11:25:30 AM"),
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6016, "12/13/2025 4:06:46 PM"),
    (6015, "12/13/2025 3:59:46 PM"),
    (6014, "12/13/2025 3:55:50 PM"),
    (6013, "12/13/2025 1:06:44 PM"),
    (6012, "12/13/2025 12:55:28 PM"),
    (6011, "12/13/2025 12:20:52 PM"),
    (6010, "12/13/2025 11:38:42 AM"),
    (6009, "12/13/2025 11:16:08 AM"),
    (6008, "12/13/2025 10:41:24 AM"),
    (6007, "12/13/2025 10:36:26 AM"),
    (6006, "12/13/2025 10:28:06 AM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def parse_timestamp_formats(bytes_4, bytes_8):
    """Try parsing as the 4 most common timestamp formats"""
    results = []

    # Format 1: Unix timestamp (32-bit LE)
    try:
        ts = struct.unpack('<I', bytes_4)[0]
        if 1733000000 < ts < 1735000000:  # Dec 2025 range
            dt = datetime.fromtimestamp(ts)
            results.append(('Unix32', dt))
    except:
        pass

    # Format 2: Delphi TDateTime (64-bit double LE)
    try:
        delphi = struct.unpack('<d', bytes_8)[0]
        if 46000 < delphi < 46020:  # Dec 2025 range
            dt = datetime(1899, 12, 30) + timedelta(days=delphi)
            results.append(('Delphi', dt))
    except:
        pass

    # Format 3: Windows FILETIME (64-bit LE)
    try:
        filetime = struct.unpack('<Q', bytes_8)[0]
        if filetime > 0:
            # FILETIME is 100-nanosecond intervals since 1601-01-01
            dt = datetime(1601, 1, 1) + timedelta(microseconds=filetime / 10)
            if 2025 <= dt.year <= 2026:
                results.append(('FILETIME', dt))
    except:
        pass

    # Format 4: MS-DOS datetime (32-bit packed LE)
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
                results.append(('MS-DOS', dt))
    except:
        pass

    return results

def search_file_for_timestamps(file_path, known_records):
    """Search a single file for timestamps matching known records"""
    matches = []

    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        file_size = len(data)

        # For each known record
        for record_id, timestamp_str in known_records:
            expected_dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")

            # Scan entire file for timestamps matching this record (within 60 seconds)
            for offset in range(0, len(data) - 8):
                bytes_4 = data[offset:offset+4]
                bytes_8 = data[offset:offset+8]

                parsed = parse_timestamp_formats(bytes_4, bytes_8)

                for fmt, dt in parsed:
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 60:  # Match within 60 seconds
                        matches.append({
                            'file': os.path.basename(file_path),
                            'record_id': record_id,
                            'expected': timestamp_str,
                            'offset': offset,
                            'format': fmt,
                            'found': dt.strftime('%m/%d/%Y %I:%M:%S %p'),
                            'diff_seconds': diff,
                            'hex': bytes_8.hex() if fmt in ['Delphi', 'FILETIME'] else bytes_4.hex()
                        })

        return matches
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def main():
    clipmate_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"

    print("="*100)
    print("COMPREHENSIVE TIMESTAMP SEARCH")
    print("="*100)
    print(f"\nSearching directory: {clipmate_dir}")
    print(f"Testing {len(KNOWN_RECORDS)} known records from mostrecent.jpg")
    print(f"Timestamp formats: Unix32, Delphi TDateTime, Windows FILETIME, MS-DOS\n")

    # Get all files in directory
    all_files = []
    for root, dirs, files in os.walk(clipmate_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Skip very large files (>50MB) for performance
            try:
                if os.path.getsize(file_path) < 50 * 1024 * 1024:
                    all_files.append(file_path)
            except:
                pass

    print(f"Scanning {len(all_files)} files...\n")

    # Search each file
    all_matches = []
    files_with_matches = set()

    for i, file_path in enumerate(all_files):
        filename = os.path.basename(file_path)
        print(f"[{i+1}/{len(all_files)}] Searching {filename}...", end='\r')

        matches = search_file_for_timestamps(file_path, KNOWN_RECORDS)
        if matches:
            all_matches.extend(matches)
            files_with_matches.add(os.path.basename(file_path))

    print("\n" + "="*100)
    print(f"RESULTS: Found {len(all_matches)} timestamp match(es) across {len(files_with_matches)} file(s)")
    print("="*100 + "\n")

    if all_matches:
        # Group by file
        by_file = {}
        for match in all_matches:
            file = match['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(match)

        # Print results grouped by file
        for file in sorted(by_file.keys()):
            print(f"\n{'='*100}")
            print(f"FILE: {file} ({len(by_file[file])} matches)")
            print(f"{'='*100}\n")

            for match in sorted(by_file[file], key=lambda x: x['record_id']):
                print(f"Record {match['record_id']} - Expected: {match['expected']}")
                print(f"  Found at offset {match['offset']}: {match['format']} = {match['found']}")
                print(f"  Difference: {match['diff_seconds']:.1f} seconds")
                print(f"  Hex: {match['hex']}")
                print()
    else:
        print("NO TIMESTAMPS FOUND matching any of the known records.")
        print("\nThis confirms timestamps are NOT stored in any standard format in the database files.")
        print("\nNext steps:")
        print("  1. Check Windows Registry (HKEY_CURRENT_USER\\Software\\Thornsoft Development\\ClipMate)")
        print("  2. Use Process Monitor to trace ClipMate startup and UI refresh")
        print("  3. Check if timestamps are computed from file system metadata")
        print("  4. Examine ClipMate.elf log file in log/ directory")

if __name__ == '__main__':
    main()
