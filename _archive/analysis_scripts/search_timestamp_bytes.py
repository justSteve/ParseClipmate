#!/usr/bin/env python3
"""
Search for the exact Delphi TDateTime bytes for the screenshot records
"""
import struct
from datetime import datetime

def datetime_to_delphi(dt_str):
    """Convert datetime string to Delphi TDateTime (days since 1899-12-30)"""
    dt = datetime.strptime(dt_str, "%m/%d/%Y %I:%M:%S %p")
    epoch = datetime(1899, 12, 30)
    delta = dt - epoch
    return delta.total_seconds() / 86400.0

def main():
    clipdata_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/ClipData.dat"

    with open(clipdata_path, 'rb') as f:
        data = f.read()

    print(f"ClipData.dat file size: {len(data):,} bytes\n")

    # Records from screenshot with timestamps
    records = {
        5969: "12/11/2025 11:14:28 AM",
        5968: "12/11/2025 9:41:47 AM",
        5967: "12/11/2025 9:40:33 AM",
        5966: "12/11/2025 9:40:20 AM",
        5965: "12/11/2025 9:39:46 AM",
    }

    for record_id, dt_str in records.items():
        print(f"=== Record {record_id}: {dt_str} ===")

        delphi_dt = datetime_to_delphi(dt_str)
        delphi_bytes = struct.pack('<d', delphi_dt)

        print(f"Delphi TDateTime: {delphi_dt:.10f}")
        print(f"Hex bytes: {delphi_bytes.hex()}")

        # Search for these bytes
        pos = data.find(delphi_bytes)
        if pos != -1:
            print(f"\n*** FOUND AT OFFSET {pos} ***")

            # Show context
            start = max(0, pos - 40)
            end = min(len(data), pos + 40)
            context = data[start:end]
            print(f"Context: {context.hex()}")

            # Find the record ID nearby
            id_bytes = struct.pack('<I', record_id)
            for search_range in [100, 200, 500, 1000]:
                search_start = max(0, pos - search_range)
                search_end = min(len(data), pos + search_range)
                search_area = data[search_start:search_end]

                id_pos = search_area.find(id_bytes)
                if id_pos != -1:
                    actual_id_offset = search_start + id_pos
                    offset_from_timestamp = actual_id_offset - pos
                    print(f"\nRecord ID {record_id} found {abs(offset_from_timestamp)} bytes {'before' if offset_from_timestamp < 0 else 'after'} timestamp")
                    print(f"  ID at offset: {actual_id_offset}")
                    print(f"  Timestamp at offset: {pos}")
                    print(f"  Offset difference: {offset_from_timestamp}")
                    break
        else:
            print("NOT FOUND")

        print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
