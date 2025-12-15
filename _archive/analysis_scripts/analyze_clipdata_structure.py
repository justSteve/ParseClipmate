#!/usr/bin/env python3
"""
Analyze ClipData.dat record structure to find timestamps.
We know record IDs exist in this file, so let's determine the record layout.
"""
import struct
from datetime import datetime, timedelta

# Known test records
TEST_RECORDS = [
    (6021, "12/14/2025 11:25:30 AM"),
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def find_record_size(data, record_positions):
    """Determine record size by looking at spacing between record IDs"""
    if len(record_positions) < 2:
        return None

    gaps = []
    for i in range(len(record_positions) - 1):
        gap = record_positions[i+1] - record_positions[i]
        if 50 < gap < 500:  # Reasonable record size
            gaps.append(gap)

    if gaps:
        # Most common gap is likely the record size
        from collections import Counter
        counts = Counter(gaps)
        most_common_gap = counts.most_common(1)[0][0]
        return most_common_gap

    return None

def parse_timestamps(bytes_4, bytes_8):
    """Try all timestamp formats"""
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

def main():
    clipdata_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/ClipData.dat"

    with open(clipdata_path, 'rb') as f:
        data = f.read()

    print("="*100)
    print("ANALYZING CLIPDATA.DAT STRUCTURE")
    print("="*100)
    print(f"\nFile size: {len(data):,} bytes\n")

    # Find all test record IDs and their positions
    all_positions = []
    for record_id, _ in TEST_RECORDS:
        id_bytes = struct.pack('<I', record_id)
        offset = 0
        while True:
            pos = data.find(id_bytes, offset)
            if pos == -1:
                break
            all_positions.append((record_id, pos))
            offset = pos + 1

    # Sort by position
    all_positions.sort(key=lambda x: x[1])

    print("Record ID positions in ClipData.dat:")
    for record_id, pos in all_positions:
        print(f"  Record {record_id} at offset {pos}")

    # Determine record size
    positions_only = [pos for _, pos in all_positions if _ == 6017 or _ == 6018 or _ == 6019]
    if len(positions_only) >= 2:
        record_size = find_record_size(data, sorted(positions_only))
        print(f"\nEstimated record size: {record_size} bytes")
    else:
        record_size = None
        print(f"\nCannot determine record size (not enough sequential records)")

    # Analyze each record in detail
    for record_id, timestamp_str in TEST_RECORDS:
        expected_dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")
        id_bytes = struct.pack('<I', record_id)

        pos = data.find(id_bytes)
        if pos == -1:
            continue

        print(f"\n{'='*100}")
        print(f"Record {record_id} - Expected: {timestamp_str}")
        print(f"Position: {pos}")
        print(f"{'='*100}\n")

        # Determine record boundaries
        if record_size:
            # Find start of record (ID might not be at the beginning)
            record_start = (pos // record_size) * record_size
            record_end = record_start + record_size
        else:
            record_start = max(0, pos - 100)
            record_end = min(len(data), pos + 200)

        record_data = data[record_start:record_end]

        # Hex dump
        print("Hex dump:")
        for i in range(0, len(record_data), 16):
            chunk = record_data[i:i+16]
            hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
            text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
            abs_offset = record_start + i
            marker = "  <-- ID" if record_start + i <= pos < record_start + i + 16 else ""
            print(f"  {abs_offset:6d}: {hex_str:<48} | {text}{marker}")

        # Search entire record for timestamps
        print(f"\nSearching for timestamps in this record:")
        found_any = False

        for i in range(0, len(record_data) - 8):
            bytes_4 = record_data[i:i+4]
            bytes_8 = record_data[i:i+8]
            parsed = parse_timestamps(bytes_4, bytes_8)

            for fmt, dt, hex_val in parsed:
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 7200:  # Within 2 hours
                    offset_in_record = i
                    offset_from_id = (record_start + i) - pos
                    marker = " *** MATCH ***" if diff < 60 else " (possible match)"
                    print(f"  +{offset_in_record:3d} ({offset_from_id:+4d} from ID): {fmt:<10} {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.0f}s){marker}")
                    found_any = True

        if not found_any:
            print("  No timestamps found in this record")

if __name__ == '__main__':
    main()
