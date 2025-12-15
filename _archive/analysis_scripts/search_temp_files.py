#!/usr/bin/env python3
"""
Search temp .cm_dat files for record IDs and timestamps
"""
import struct
from datetime import datetime
import os

def search_file_for_timestamps(filepath, record_ids, expected_times):
    """Search a file for record IDs and nearby timestamps"""
    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"\n{'='*80}")
    print(f"Searching: {os.path.basename(filepath)} ({len(data):,} bytes)")
    print(f"{'='*80}\n")

    for record_id in record_ids:
        id_bytes = struct.pack('<I', record_id)

        # Find all occurrences
        positions = []
        offset = 0
        while True:
            pos = data.find(id_bytes, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1

        if positions:
            expected_dt_str = expected_times.get(record_id, "Unknown")
            if expected_dt_str != "Unknown":
                expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")
            else:
                expected_dt = None

            print(f"Record {record_id}: Expected {expected_dt_str}")
            print(f"  Found at {len(positions)} position(s): {positions}")

            for pos in positions:
                # Search for timestamps within 200 bytes
                search_start = max(0, pos - 200)
                search_end = min(len(data), pos + 200)

                timestamps_found = []

                # Try Unix timestamps (4-byte)
                for i in range(search_start, search_end - 4, 1):
                    try:
                        ts = struct.unpack('<I', data[i:i+4])[0]
                        if 1000000000 < ts < 2000000000:
                            dt = datetime.fromtimestamp(ts)
                            if dt.year == 2025 and dt.month == 12:
                                offset_from_id = i - pos
                                if expected_dt:
                                    diff = abs((dt - expected_dt).total_seconds())
                                    if diff < 7200:  # Within 2 hours
                                        timestamps_found.append((i, dt, ts, offset_from_id, diff))
                                else:
                                    timestamps_found.append((i, dt, ts, offset_from_id, 0))
                    except:
                        pass

                # Try Delphi TDateTime (8-byte double)
                for i in range(search_start, search_end - 8, 1):
                    try:
                        delphi_val = struct.unpack('<d', data[i:i+8])[0]
                        if 46000 < delphi_val < 46010:  # Around Dec 2025
                            dt = datetime(1899, 12, 30) + timedelta(days=delphi_val)
                            offset_from_id = i - pos
                            if expected_dt:
                                diff = abs((dt - expected_dt).total_seconds())
                                if diff < 7200:
                                    timestamps_found.append((i, dt, struct.pack('<d', delphi_val).hex(), offset_from_id, diff))
                            else:
                                timestamps_found.append((i, dt, struct.pack('<d', delphi_val).hex(), offset_from_id, 0))
                    except:
                        pass

                if timestamps_found:
                    print(f"\n  At position {pos}:")
                    # Sort by difference from expected
                    for ts_offset, dt, ts_hex, offset_from_id, diff in sorted(timestamps_found, key=lambda x: x[4]):
                        match_marker = " *** EXACT MATCH ***" if diff < 5 else (" *** CLOSE MATCH ***" if diff < 60 else "")
                        print(f"    Offset {ts_offset} ({offset_from_id:+4d} from ID): {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.0f}s){match_marker}")

                    # Dump hex around the ID
                    print(f"\n    Hex dump around offset {pos}:")
                    dump_start = max(0, pos - 40)
                    dump_end = min(len(data), pos + 80)
                    chunk = data[dump_start:dump_end]

                    for i in range(0, len(chunk), 16):
                        line = chunk[i:i+16]
                        actual_offset = dump_start + i
                        hex_str = ' '.join([line[j:j+2].hex() for j in range(0, len(line), 2)])

                        marker = ""
                        if dump_start + i <= pos < dump_start + i + 16:
                            marker = "  <-- ID"

                        # Check if timestamp is in this line
                        for ts_offset, _, _, _, _ in timestamps_found:
                            if dump_start + i <= ts_offset < dump_start + i + 16:
                                marker = f"  <-- TIMESTAMP at +{ts_offset - pos}"

                        print(f"      {actual_offset:5d}: {hex_str}{marker}")

                else:
                    print(f"\n  At position {pos}: No matching timestamps found")

            print()

def main():
    from datetime import timedelta  # Import here for Delphi datetime calc

    temp_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/temp"

    target_records = {
        5969: "12/11/2025 11:14:28 AM",
        5968: "12/11/2025 9:41:47 AM",
        5967: "12/11/2025 9:40:33 AM",
        5966: "12/11/2025 9:40:20 AM",
        5965: "12/11/2025 9:39:46 AM",
    }

    # Search the most recent temp files
    temp_files = [
        "153480.cm_dat",
        "153480.cm_idx",
        "217520.cm_dat",
    ]

    for filename in temp_files:
        filepath = os.path.join(temp_dir, filename)
        if os.path.exists(filepath):
            search_file_for_timestamps(filepath, list(target_records.keys()), target_records)

if __name__ == '__main__':
    from datetime import timedelta
    main()
