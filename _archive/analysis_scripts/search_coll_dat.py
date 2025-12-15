#!/usr/bin/env python3
"""
Search COLL.dat for record IDs and timestamps
"""
import struct
from datetime import datetime, timedelta
import os

def main():
    coll_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/COLL.dat"

    with open(coll_path, 'rb') as f:
        data = f.read()

    print(f"COLL.dat size: {len(data):,} bytes\n")

    # Search for our target record IDs
    target_records = {
        5969: "12/11/2025 11:14:28 AM",
        5968: "12/11/2025 9:41:47 AM",
        5967: "12/11/2025 9:40:33 AM",
    }

    print("Searching for record IDs in COLL.dat:\n")

    for record_id, expected_dt_str in target_records.items():
        id_bytes = struct.pack('<I', record_id)
        expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")

        # Search for ID
        positions = []
        offset = 0
        while True:
            pos = data.find(id_bytes, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1

        if positions:
            print(f"Record {record_id}: Found at {len(positions)} position(s)")

            for pos in positions[:3]:
                # Search for timestamps nearby
                search_start = max(0, pos - 200)
                search_end = min(len(data), pos + 200)

                # Try Unix timestamps
                timestamps_found = []
                for i in range(search_start, search_end - 4, 1):
                    try:
                        ts = struct.unpack('<I', data[i:i+4])[0]
                        if 1765400000 < ts < 1765500000:  # Dec 11, 2025 range
                            dt = datetime.fromtimestamp(ts)
                            diff = abs((dt - expected_dt).total_seconds())
                            if diff < 7200:
                                timestamps_found.append((i, dt, diff))
                    except:
                        pass

                if timestamps_found:
                    print(f"  At offset {pos}:")
                    for ts_offset, dt, diff in timestamps_found:
                        match_str = " *** MATCH ***" if diff < 60 else ""
                        print(f"    Timestamp at {ts_offset} ({ts_offset - pos:+d} from ID): {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s){match_str}")
        else:
            print(f"Record {record_id}: NOT FOUND")

        print()

    # Also scan entire file for December 2025 timestamps
    print("\n" + "="*80)
    print("Scanning entire COLL.dat for December 2025 timestamps:")
    print("="*80 + "\n")

    dec_timestamps = []
    for i in range(0, len(data) - 4, 4):
        try:
            ts = struct.unpack('<I', data[i:i+4])[0]
            if 1765400000 < ts < 1765500000:  # Dec 11, 2025 range
                dt = datetime.fromtimestamp(ts)
                dec_timestamps.append((i, dt))
        except:
            pass

    if dec_timestamps:
        print(f"Found {len(dec_timestamps)} timestamps on Dec 11, 2025:\n")
        for offset, dt in dec_timestamps[:20]:
            print(f"  Offset {offset:6d}: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
    else:
        print("No December 11, 2025 timestamps found")

if __name__ == '__main__':
    main()
