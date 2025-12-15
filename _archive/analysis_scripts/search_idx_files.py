#!/usr/bin/env python3
"""
Search for timestamp bytes in .idx files
"""
import struct
from datetime import datetime
import os

def datetime_to_delphi(dt_str):
    """Convert datetime string to Delphi TDateTime (days since 1899-12-30)"""
    dt = datetime.strptime(dt_str, "%m/%d/%Y %I:%M:%S %p")
    epoch = datetime(1899, 12, 30)
    delta = dt - epoch
    return delta.total_seconds() / 86400.0

def main():
    base_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"

    idx_files = ['CLIP.idx', 'ClipData.idx', 'BLOBTXT.idx']

    # Test record
    record_id = 5969
    dt_str = "12/11/2025 11:14:28 AM"

    print(f"Searching for Record {record_id}: {dt_str}\n")

    delphi_dt = datetime_to_delphi(dt_str)
    delphi_bytes = struct.pack('<d', delphi_dt)

    print(f"Delphi TDateTime: {delphi_dt:.10f}")
    print(f"Hex bytes: {delphi_bytes.hex()}\n")

    for idx_file in idx_files:
        idx_path = os.path.join(base_dir, idx_file)
        if not os.path.exists(idx_path):
            continue

        file_size = os.path.getsize(idx_path)
        print(f"=== Searching {idx_file} ({file_size:,} bytes) ===")

        with open(idx_path, 'rb') as f:
            data = f.read()

        # Search for timestamp bytes
        pos = data.find(delphi_bytes)
        if pos != -1:
            print(f"*** TIMESTAMP FOUND AT OFFSET {pos} ***")

            # Show context
            start = max(0, pos - 40)
            end = min(len(data), pos + 40)
            context = data[start:end]
            print(f"Context: {context.hex()}")

            # Search for record ID nearby
            id_bytes = struct.pack('<I', record_id)
            for search_range in [50, 100, 200, 500]:
                search_start = max(0, pos - search_range)
                search_end = min(len(data), pos + search_range)
                search_area = data[search_start:search_end]

                id_pos = search_area.find(id_bytes)
                if id_pos != -1:
                    actual_id_offset = search_start + id_pos
                    offset_from_timestamp = actual_id_offset - pos
                    print(f"\n  Record ID found {abs(offset_from_timestamp)} bytes {'before' if offset_from_timestamp < 0 else 'after'} timestamp")
                    print(f"  ID at offset: {actual_id_offset}")
                    print(f"  Timestamp at offset: {pos}")
                    print(f"  Field offset in record structure: {offset_from_timestamp}")

                    # If we found it, dump the structure around it
                    if abs(offset_from_timestamp) < 200:
                        record_start = min(actual_id_offset, pos) - 20
                        record_end = max(actual_id_offset, pos) + 40
                        if record_start >= 0 and record_end <= len(data):
                            record_bytes = data[record_start:record_end]
                            print(f"\n  Record structure dump (offset {record_start}):")
                            for i in range(0, len(record_bytes), 16):
                                chunk = record_bytes[i:i+16]
                                offset_label = record_start + i
                                hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
                                print(f"    {offset_label:5d}: {hex_str}")
                    break
        else:
            print("Timestamp NOT FOUND")

        # Also search for record ID
        id_bytes = struct.pack('<I', record_id)
        id_pos = data.find(id_bytes)
        if id_pos != -1:
            print(f"\n  Record ID {record_id} found at offset {id_pos}")
            # Dump surrounding area
            start = max(0, id_pos - 20)
            end = min(len(data), id_pos + 60)
            chunk = data[start:end]

            print(f"  Context:")
            for i in range(0, len(chunk), 16):
                line = chunk[i:i+16]
                offset_label = start + i
                hex_str = ' '.join([line[j:j+2].hex() for j in range(0, len(line), 2)])
                print(f"    {offset_label:5d}: {hex_str}")

                # Try to parse as double at various offsets
                for double_offset in range(0, min(16, len(line) - 7)):
                    if i + double_offset + 8 <= len(chunk):
                        double_bytes = chunk[i + double_offset:i + double_offset + 8]
                        try:
                            as_double = struct.unpack('<d', double_bytes)[0]
                            if 46000 < as_double < 46010:  # Date range around 12/11/2025
                                from datetime import timedelta
                                base = datetime(1899, 12, 30)
                                date = base + timedelta(days=as_double)
                                print(f"      -> Offset {start + i + double_offset}: {as_double:.10f} = {date.strftime('%m/%d/%Y %I:%M:%S %p')}")
                        except:
                            pass

        print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    main()
