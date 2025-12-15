#!/usr/bin/env python3
"""
Comprehensive search across ALL database files for record IDs and timestamps
"""
import struct
from datetime import datetime, timedelta
import os

def search_all_files(base_dir, record_ids, expected_times):
    """Search all .dat and .idx files for records and timestamps"""

    files_to_search = [
        'CLIP.dat',
        'CLIP.idx',
        'ClipData.dat',
        'ClipData.idx',
        'BLOBTXT.dat',
        'BLOBTXT.idx',
    ]

    for filename in files_to_search:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, 'rb') as f:
            data = f.read()

        print(f"\n{'='*80}")
        print(f"Searching: {filename} ({len(data):,} bytes)")
        print(f"{'='*80}\n")

        found_any = False

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
                found_any = True
                expected_dt_str = expected_times.get(record_id, "Unknown")

                if expected_dt_str != "Unknown":
                    expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")
                else:
                    expected_dt = None

                print(f"Record {record_id}: Expected {expected_dt_str}")
                print(f"  Found at {len(positions)} position(s): {positions[:5]}")  # Show first 5

                # For each position, search for timestamps
                for pos in positions[:3]:  # Check first 3 occurrences
                    print(f"\n  Occurrence at offset {pos}:")

                    # Search within 500 bytes
                    search_start = max(0, pos - 500)
                    search_end = min(len(data), pos + 500)

                    timestamps_found = []

                    # Try Unix 32-bit timestamps
                    for i in range(search_start, search_end - 4, 1):
                        try:
                            ts = struct.unpack('<I', data[i:i+4])[0]
                            if 1765400000 < ts < 1765500000:  # Dec 11, 2025 range
                                dt = datetime.fromtimestamp(ts)
                                offset_from_id = i - pos

                                if expected_dt:
                                    diff = abs((dt - expected_dt).total_seconds())
                                    if diff < 7200:  # Within 2 hours
                                        timestamps_found.append(('Unix32', i, dt, offset_from_id, diff))
                        except:
                            pass

                    # Try Delphi TDateTime (8-byte double)
                    for i in range(search_start, search_end - 8, 1):
                        try:
                            delphi_val = struct.unpack('<d', data[i:i+8])[0]
                            if 46002.0 < delphi_val < 46003.0:  # Dec 11, 2025 range
                                dt = datetime(1899, 12, 30) + timedelta(days=delphi_val)
                                offset_from_id = i - pos

                                if expected_dt:
                                    diff = abs((dt - expected_dt).total_seconds())
                                    if diff < 7200:
                                        timestamps_found.append(('Delphi', i, dt, offset_from_id, diff))
                        except:
                            pass

                    if timestamps_found:
                        print(f"    *** FOUND {len(timestamps_found)} MATCHING TIMESTAMP(S) ***")

                        # Sort by closest match
                        timestamps_found.sort(key=lambda x: x[4])

                        for fmt, ts_offset, dt, offset_from_id, diff in timestamps_found[:5]:
                            match_marker = ""
                            if diff < 5:
                                match_marker = " *** EXACT MATCH ***"
                            elif diff < 60:
                                match_marker = " *** VERY CLOSE ***"

                            print(f"      {fmt} at offset {ts_offset} ({offset_from_id:+5d} from ID)")
                            print(f"        DateTime: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
                            print(f"        Difference: {diff:.1f} seconds{match_marker}")

                        # Show hex dump around the best match
                        if timestamps_found:
                            best = timestamps_found[0]
                            best_offset = best[1]

                            print(f"\n      Hex dump around best match (offset {best_offset}):")
                            dump_start = max(0, best_offset - 40)
                            dump_end = min(len(data), best_offset + 40)
                            chunk = data[dump_start:dump_end]

                            for i in range(0, len(chunk), 16):
                                line = chunk[i:i+16]
                                actual_offset = dump_start + i
                                hex_str = ' '.join([line[j:j+2].hex() for j in range(0, len(line), 2)])

                                marker = ""
                                if dump_start + i <= best_offset < dump_start + i + 16:
                                    marker = "  <-- TIMESTAMP"
                                elif dump_start + i <= pos < dump_start + i + 16:
                                    marker = "  <-- ID"

                                print(f"        {actual_offset:6d}: {hex_str}{marker}")
                    else:
                        print(f"    No matching timestamps found nearby")

                print()

        if not found_any:
            print(f"  None of the target records found in this file\n")

def main():
    base_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"

    target_records = {
        5969: "12/11/2025 11:14:28 AM",
        5968: "12/11/2025 9:41:47 AM",
        5967: "12/11/2025 9:40:33 AM",
        5966: "12/11/2025 9:40:20 AM",
        5965: "12/11/2025 9:39:46 AM",
    }

    search_all_files(base_dir, list(target_records.keys()), target_records)

if __name__ == '__main__':
    main()
