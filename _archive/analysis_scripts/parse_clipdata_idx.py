#!/usr/bin/env python3
"""
Parse ClipData.idx to find timestamps linked to record IDs
"""
import struct
from datetime import datetime

def find_timestamps_near_ids(data, record_ids):
    """Find timestamps near specific record IDs"""
    results = {}

    for record_id in record_ids:
        id_bytes = struct.pack('<I', record_id)

        # Find all occurrences
        offset = 0
        while True:
            pos = data.find(id_bytes, offset)
            if pos == -1:
                break

            # Check surrounding area for Unix timestamps
            search_start = max(0, pos - 100)
            search_end = min(len(data), pos + 100)

            timestamps_found = []
            for i in range(search_start, search_end - 4, 1):
                try:
                    ts = struct.unpack('<I', data[i:i+4])[0]
                    if 1000000000 < ts < 2000000000:
                        dt = datetime.fromtimestamp(ts)
                        if dt.year == 2025 and dt.month == 12:
                            offset_from_id = i - pos
                            timestamps_found.append((i, dt, ts, offset_from_id))
                except:
                    pass

            if timestamps_found:
                if record_id not in results:
                    results[record_id] = []
                results[record_id].append({
                    'id_offset': pos,
                    'timestamps': timestamps_found
                })

            offset = pos + 1

    return results

def scan_idx_structure(data):
    """Analyze the overall structure of the .idx file"""
    print(f"ClipData.idx file size: {len(data):,} bytes\n")

    # Look for common patterns
    print("="*80)
    print("Scanning for December 2025 timestamps...")
    print("="*80 + "\n")

    dec_timestamps = []
    for i in range(0, len(data) - 4, 4):
        try:
            ts = struct.unpack('<I', data[i:i+4])[0]
            if 1000000000 < ts < 2000000000:
                dt = datetime.fromtimestamp(ts)
                if dt.year == 2025 and (dt.month == 12 and dt.day == 11):
                    dec_timestamps.append((i, dt, ts))
        except:
            pass

    if dec_timestamps:
        print(f"Found {len(dec_timestamps)} timestamps on 12/11/2025:\n")

        # Group by time ranges
        for offset, dt, ts in sorted(dec_timestamps, key=lambda x: x[1]):
            print(f"  Offset {offset:6d}: {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (0x{ts:08x})")

            # Show nearby record IDs
            nearby_ids = []
            search_start = max(0, offset - 50)
            search_end = min(len(data), offset + 50)

            for target_id in range(5950, 5980):
                id_bytes = struct.pack('<I', target_id)
                if id_bytes in data[search_start:search_end]:
                    nearby_ids.append(target_id)

            if nearby_ids:
                print(f"    Nearby record IDs: {nearby_ids}")
            print()
    else:
        print("No December 11, 2025 timestamps found\n")

def main():
    idx_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/ClipData.idx"

    with open(idx_path, 'rb') as f:
        data = f.read()

    # Scan for timestamps
    scan_idx_structure(data)

    # Look specifically for our target records
    print("\n" + "="*80)
    print("Searching for specific record IDs with timestamps...")
    print("="*80 + "\n")

    target_records = {
        5969: "12/11/2025 11:14:28 AM",
        5968: "12/11/2025 9:41:47 AM",
        5967: "12/11/2025 9:40:33 AM",
        5966: "12/11/2025 9:40:20 AM",
        5965: "12/11/2025 9:39:46 AM",
    }

    results = find_timestamps_near_ids(data, list(target_records.keys()))

    for record_id, expected_dt_str in target_records.items():
        expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")

        print(f"Record {record_id}: Expected {expected_dt_str}")

        if record_id in results:
            for occurrence in results[record_id]:
                id_offset = occurrence['id_offset']
                timestamps = occurrence['timestamps']

                print(f"  Found at offset {id_offset}")
                for ts_offset, dt, ts, offset_from_id in timestamps:
                    diff = abs((dt - expected_dt).total_seconds())
                    match_str = " *** MATCH ***" if diff < 60 else ""
                    print(f"    Offset {ts_offset} ({offset_from_id:+d} from ID): {dt.strftime('%m/%d/%Y %I:%M:%S %p')}{match_str}")
                print()
        else:
            print(f"  Record ID not found in index\n")

if __name__ == '__main__':
    main()
