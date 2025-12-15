#!/usr/bin/env python3
"""
Investigate the area around the December 2025 timestamp we found
"""
import struct
from datetime import datetime

def main():
    clipdata_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/ClipData.dat"

    with open(clipdata_path, 'rb') as f:
        data = f.read()

    # The Unix timestamp we found at offset 106944
    timestamp_offset = 106944

    print(f"Investigating timestamp at offset {timestamp_offset}")
    print(f"{'='*80}\n")

    # Read the timestamp
    ts_bytes = data[timestamp_offset:timestamp_offset+4]
    ts_value = struct.unpack('<I', ts_bytes)[0]
    ts_dt = datetime.fromtimestamp(ts_value)

    print(f"Timestamp value: {ts_value} (0x{ts_value:08x})")
    print(f"Timestamp datetime: {ts_dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
    print(f"Hex bytes: {ts_bytes.hex()}\n")

    # Dump 500 bytes before and after
    start = max(0, timestamp_offset - 500)
    end = min(len(data), timestamp_offset + 500)
    context = data[start:end]

    print(f"Context dump (offset {start} to {end}):\n")

    # Look for record IDs in this range
    target_ids = [5969, 5968, 5967, 5966, 5965, 5964, 5963, 5962, 5961, 5960, 5959]

    found_ids = []
    for record_id in target_ids:
        id_bytes = struct.pack('<I', record_id)
        pos = context.find(id_bytes)
        if pos != -1:
            actual_offset = start + pos
            distance = actual_offset - timestamp_offset
            found_ids.append((record_id, actual_offset, distance))

    if found_ids:
        print("Found record IDs in this area:")
        for rid, offset, distance in found_ids:
            print(f"  Record {rid} at offset {offset} ({distance:+d} from timestamp)")
        print()

    # Hex dump with annotations
    for i in range(0, len(context), 16):
        chunk = context[i:i+16]
        actual_offset = start + i
        hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])

        marker = ""
        if start + i <= timestamp_offset < start + i + 16:
            marker = "  <-- TIMESTAMP HERE"

        # Check if any record ID is in this line
        for rid, rid_offset, _ in found_ids:
            if start + i <= rid_offset < start + i + 16:
                marker = f"  <-- Record {rid}"

        print(f"  {actual_offset:6d}: {hex_str}{marker}")

    # Now check for patterns - are there more timestamps in this structure?
    print(f"\n{'='*80}")
    print("Searching for more timestamps in this region...")
    print(f"{'='*80}\n")

    # Scan every 4 bytes in the context for Unix timestamps
    timestamps_found = []
    for i in range(0, len(context) - 4, 4):
        chunk = context[i:i+4]
        try:
            ts = struct.unpack('<I', chunk)[0]
            if 1000000000 < ts < 2000000000:  # Valid Unix timestamp range
                dt = datetime.fromtimestamp(ts)
                # Only show December 2025
                if dt.year == 2025 and dt.month == 12:
                    actual_offset = start + i
                    timestamps_found.append((actual_offset, dt, ts))
        except:
            pass

    if timestamps_found:
        print(f"Found {len(timestamps_found)} timestamps in December 2025:\n")
        for offset, dt, ts in timestamps_found:
            print(f"  Offset {offset}: {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (0x{ts:08x})")

    # Check if there's a pattern (e.g., every N bytes)
    if len(timestamps_found) > 1:
        print("\nTimestamp spacing:")
        for i in range(1, len(timestamps_found)):
            spacing = timestamps_found[i][0] - timestamps_found[i-1][0]
            print(f"  {spacing} bytes between offset {timestamps_found[i-1][0]} and {timestamps_found[i][0]}")

if __name__ == '__main__':
    main()
