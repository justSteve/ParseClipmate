#!/usr/bin/env python3
"""
Comprehensive timestamp search across all ClipMate database files
Tests top 4 date formats at all offsets near record IDs
"""
import struct
from datetime import datetime, timedelta
import os
import glob

def parse_timestamp_formats(bytes_4, bytes_8):
    """Try parsing as the 4 most common timestamp formats"""
    results = []

    # Format 1: Unix timestamp (32-bit, seconds since 1970-01-01)
    try:
        ts = struct.unpack('<I', bytes_4)[0]
        if 1000000000 < ts < 2000000000:  # ~2001-2033
            dt = datetime.fromtimestamp(ts)
            if 2020 < dt.year < 2030:
                results.append(('Unix32', dt))
    except:
        pass

    # Format 2: Delphi TDateTime (64-bit double, days since 1899-12-30)
    try:
        delphi = struct.unpack('<d', bytes_8)[0]
        if 40000 < delphi < 50000:  # ~2009-2036
            dt = datetime(1899, 12, 30) + timedelta(days=delphi)
            if 2020 < dt.year < 2030:
                results.append(('Delphi', dt))
    except:
        pass

    # Format 3: Windows FILETIME (64-bit, 100-nanosecond intervals since 1601-01-01)
    try:
        ft = struct.unpack('<Q', bytes_8)[0]
        if 100000000000000000 < ft < 200000000000000000:
            dt = datetime(1601, 1, 1) + timedelta(microseconds=ft / 10)
            if 2020 < dt.year < 2030:
                results.append(('FILETIME', dt))
    except:
        pass

    # Format 4: MS-DOS datetime (32-bit packed format)
    try:
        dos_val = struct.unpack('<I', bytes_4)[0]
        dos_time = dos_val & 0xFFFF
        dos_date = (dos_val >> 16) & 0xFFFF

        if dos_date > 0:
            year = 1980 + ((dos_date >> 9) & 0x7F)
            month = (dos_date >> 5) & 0x0F
            day = dos_date & 0x1F
            hour = (dos_time >> 11) & 0x1F
            minute = (dos_time >> 5) & 0x3F
            second = (dos_time & 0x1F) * 2

            if 2020 < year < 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                dt = datetime(year, month, day, hour, minute, second)
                results.append(('DOS', dt))
    except:
        pass

    return results

def search_file_for_timestamp(filepath, record_id, expected_dt):
    """Search a single file for a record ID and nearby timestamps"""
    with open(filepath, 'rb') as f:
        data = f.read()

    id_bytes = struct.pack('<I', record_id)

    # Find all occurrences of the record ID
    positions = []
    offset = 0
    while True:
        pos = data.find(id_bytes, offset)
        if pos == -1:
            break
        positions.append(pos)
        offset = pos + 1

    if not positions:
        return []

    matches = []

    # For each occurrence, search nearby for timestamps
    for id_pos in positions:
        # Search 200 bytes before and after the ID
        search_start = max(0, id_pos - 200)
        search_end = min(len(data), id_pos + 200)

        # Try every offset
        for i in range(search_start, search_end - 8):
            bytes_4 = data[i:i+4]
            bytes_8 = data[i:i+8]

            # Skip all zeros
            if bytes_8 == b'\x00' * 8:
                continue

            timestamp_results = parse_timestamp_formats(bytes_4, bytes_8)

            for fmt, dt in timestamp_results:
                # Check if it matches expected time (within 1 hour)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 3600:
                    offset_from_id = i - id_pos
                    matches.append({
                        'file': os.path.basename(filepath),
                        'id_offset': id_pos,
                        'ts_offset': i,
                        'offset_from_id': offset_from_id,
                        'format': fmt,
                        'datetime': dt,
                        'diff_seconds': diff,
                        'hex': bytes_8.hex() if fmt in ['Delphi', 'FILETIME'] else bytes_4.hex()
                    })

    return matches

def main():
    base_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"

    # Test records from mostrecent.jpg
    test_records = [
        (6021, "12/14/2025 10:47:10 AM"),
        (6020, "12/14/2025 10:38:25 AM"),
        (6019, "12/14/2025 10:38:01 AM"),
        (6018, "12/14/2025 9:35:03 AM"),
        (6017, "12/14/2025 8:58:00 AM"),
        (6016, "12/14/2025 4:13:32 AM"),
        (6015, "12/14/2025 4:05:19 AM"),
        (6014, "12/14/2025 4:04:02 AM"),
        (6013, "12/13/2025 5:45:49 PM"),
        (6012, "12/13/2025 6:19:52 PM"),
    ]

    # Files to search
    file_patterns = ['*.dat', '*.idx']

    print("=" * 100)
    print("COMPREHENSIVE TIMESTAMP SEARCH")
    print("=" * 100)
    print(f"\nSearching directory: {base_dir}")
    print(f"Testing {len(test_records)} records with known timestamps")
    print(f"Formats: Unix32, Delphi TDateTime, Windows FILETIME, MS-DOS datetime\n")

    all_matches = []

    # Get all database files
    all_files = []
    for pattern in file_patterns:
        all_files.extend(glob.glob(os.path.join(base_dir, pattern)))

    print(f"Found {len(all_files)} database files to search\n")

    # Search each record in each file
    for record_id, dt_str in test_records:
        expected_dt = datetime.strptime(dt_str, "%m/%d/%Y %I:%M:%S %p")

        print(f"\n{'='*100}")
        print(f"Record {record_id}: {dt_str}")
        print(f"{'='*100}")

        record_matches = []

        for filepath in all_files:
            matches = search_file_for_timestamp(filepath, record_id, expected_dt)
            record_matches.extend(matches)
            all_matches.extend(matches)

        if record_matches:
            # Group by file and offset
            by_file = {}
            for match in record_matches:
                key = (match['file'], match['offset_from_id'])
                if key not in by_file:
                    by_file[key] = []
                by_file[key].append(match)

            print(f"\nFound {len(record_matches)} match(es) across {len(by_file)} location(s):")

            for (filename, offset_from_id), matches in sorted(by_file.items(), key=lambda x: min(m['diff_seconds'] for m in x[1])):
                # Show best match for this location
                best = min(matches, key=lambda x: x['diff_seconds'])

                marker = ""
                if best['diff_seconds'] < 1:
                    marker = " *** PERFECT MATCH ***"
                elif best['diff_seconds'] < 60:
                    marker = " *** EXCELLENT ***"

                print(f"\n  {filename} at offset {best['offset_from_id']:+5d} from ID:")
                print(f"    Format: {best['format']}")
                print(f"    DateTime: {best['datetime'].strftime('%m/%d/%Y %I:%M:%S %p')}")
                print(f"    Difference: {best['diff_seconds']:.1f} seconds{marker}")
                print(f"    Hex: {best['hex']}")
                print(f"    Absolute offset: {best['ts_offset']}")

                # Show if multiple formats match at same location
                if len(matches) > 1:
                    print(f"    Note: {len(matches)} formats match at this offset")
        else:
            print(f"\n  No matches found")

    # Summary
    print(f"\n\n{'='*100}")
    print("SUMMARY")
    print(f"{'='*100}\n")

    if all_matches:
        # Group by file
        by_file = {}
        for match in all_matches:
            if match['file'] not in by_file:
                by_file[match['file']] = []
            by_file[match['file']].append(match)

        print(f"Total matches found: {len(all_matches)}")
        print(f"Files with matches: {len(by_file)}\n")

        for filename in sorted(by_file.keys()):
            matches = by_file[filename]
            print(f"\n{filename}: {len(matches)} match(es)")

            # Show most common offset
            offsets = {}
            for m in matches:
                offset = m['offset_from_id']
                if offset not in offsets:
                    offsets[offset] = 0
                offsets[offset] += 1

            if offsets:
                most_common_offset = max(offsets.items(), key=lambda x: x[1])
                print(f"  Most common offset: {most_common_offset[0]:+5d} from ID ({most_common_offset[1]} occurrences)")

            # Show format distribution
            formats = {}
            for m in matches:
                fmt = m['format']
                if fmt not in formats:
                    formats[fmt] = 0
                formats[fmt] += 1

            print(f"  Formats: {', '.join([f'{fmt}={count}' for fmt, count in sorted(formats.items())])}")
    else:
        print("No timestamp matches found in any file.")

if __name__ == '__main__':
    main()
