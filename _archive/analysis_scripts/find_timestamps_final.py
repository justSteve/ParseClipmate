#!/usr/bin/env python3
"""
FINAL attempt: Search all files for timestamps using all available keys.
Use proper parsing to extract GUIDs, then search everywhere.
"""
import struct
from datetime import datetime, timedelta
import sys
import io

# Test records from mostrecent.jpg
TEST_RECORDS = [
    (6021, "12/14/2025 10:47:10 AM"),
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def extract_record_at_offset(file_path, offset, size=568):
    """Extract a record at a specific offset"""
    with open(file_path, 'rb') as f:
        f.seek(offset)
        return f.read(size)

def parse_guid_from_record(record_data):
    """Parse GUID from record at offset +454"""
    if len(record_data) < 492:  # 454 + 38
        return None

    guid_bytes = record_data[454:492]
    try:
        guid_str = guid_bytes.decode('ascii', errors='ignore').strip('\x00')
        if guid_str.startswith('{') and '}' in guid_str:
            return guid_str[:38]  # Standard GUID length with braces
    except:
        pass

    return None

def search_timestamps_in_data(data, expected_dt, search_range):
    """Search for timestamps in data within a range"""
    results = []

    for offset in range(search_range[0], min(search_range[1], len(data) - 8)):
        bytes_4 = data[offset:offset+4]
        bytes_8 = data[offset:offset+8]

        # Unix 32-bit
        try:
            ts = struct.unpack('<I', bytes_4)[0]
            if 1733000000 < ts < 1735000000:
                dt = datetime.fromtimestamp(ts)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 3600:
                    results.append(('Unix32', offset, dt, diff, bytes_4.hex()))
        except:
            pass

        # Delphi TDateTime
        try:
            delphi = struct.unpack('<d', bytes_8)[0]
            if 46000 < delphi < 46020:
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 3600:
                    results.append(('Delphi', offset, dt, diff, bytes_8.hex()))
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

                if 2025 <= year <= 2026 and 1 <= month <= 12 and 1 <= day <= 31 and hour < 24:
                    dt = datetime(year, month, day, hour, minute, second)
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 3600:
                        results.append(('MS-DOS', offset, dt, diff, bytes_4.hex()))
        except:
            pass

    return results

def main():
    base_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"
    clip_dat_path = f"{base_dir}/CLIP.dat"
    clip_idx_path = f"{base_dir}/CLIP.idx"

    with open(clip_dat_path, 'rb') as f:
        clip_dat = f.read()

    with open(clip_idx_path, 'rb') as f:
        clip_idx = f.read()

    print("="*100)
    print("FINAL COMPREHENSIVE TIMESTAMP SEARCH")
    print("="*100)
    print("\nSearching entire CLIP.idx for ANY timestamps matching our test records")
    print("(ignoring GUID/ID linkage, just looking for timestamps)\n")

    all_matches = []

    for record_id, timestamp_str in TEST_RECORDS:
        expected_dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")

        print(f"Record {record_id} - Expected: {timestamp_str}")

        # Search entire CLIP.idx for matching timestamps
        results = search_timestamps_in_data(clip_idx, expected_dt, (0, len(clip_idx)))

        if results:
            print(f"  *** FOUND {len(results)} timestamp match(es) in CLIP.idx! ***")

            for fmt, offset, dt, diff, hex_val in results:
                marker = " *** EXACT MATCH ***" if diff < 5 else ""
                print(f"    Offset {offset}: {fmt} = {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.0f}s){marker}")
                all_matches.append((record_id, fmt, offset, dt, diff))
        else:
            print(f"  No matching timestamps found in CLIP.idx")

        print()

    print(f"{'='*100}")
    print(f"TOTAL MATCHES: {len(all_matches)}")
    print(f"{'='*100}\n")

    if all_matches:
        print("SUCCESS! Found timestamps in CLIP.idx!\n")

        # Analyze pattern
        offsets = [m[2] for m in all_matches]
        formats = set(m[1] for m in all_matches)

        print(f"Timestamp format(s): {', '.join(formats)}")
        print(f"Offsets: {offsets}")

        # Check if offsets follow a pattern
        if len(offsets) > 1:
            gaps = [offsets[i+1] - offsets[i] for i in range(len(offsets) - 1)]
            print(f"Gaps between offsets: {gaps}")

            if len(set(gaps)) == 1:
                print(f"\n*** CONSISTENT PATTERN: Records are spaced {gaps[0]} bytes apart! ***")
    else:
        print("NO MATCHES FOUND.")
        print("\nConclusion: Timestamps are NOT stored in CLIP.idx in standard binary formats.")
        print("\nNext steps:")
        print("  1. Timestamps might only exist for graphic clips (embedded in title)")
        print("  2. Timestamps might be computed dynamically from another source")
        print("  3. Timestamps might be in an undocumented proprietary format")

if __name__ == '__main__':
    main()
