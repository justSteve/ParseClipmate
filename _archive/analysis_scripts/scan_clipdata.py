#!/usr/bin/env python3
"""
Scan ClipData.dat for the records from the screenshot
"""
import struct

def main():
    clipdata_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/ClipData.dat"

    with open(clipdata_path, 'rb') as f:
        data = f.read()

    print(f"ClipData.dat file size: {len(data):,} bytes")

    # Target record IDs from screenshot
    target_ids = [5969, 5968, 5967, 5966, 5965, 5964, 5963, 5962, 5961, 5960, 5959]

    # Search for these IDs as 4-byte integers (little-endian)
    print("\nSearching for target record IDs...")
    for record_id in target_ids:
        id_bytes = struct.pack('<I', record_id)
        positions = []

        # Find all occurrences
        offset = 0
        while True:
            pos = data.find(id_bytes, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1

        if positions:
            print(f"\nRecord ID {record_id} found at {len(positions)} position(s): {positions}")

            # Dump data around each occurrence
            for pos in positions[:3]:  # First 3 occurrences
                start = max(0, pos - 20)
                end = min(len(data), pos + 100)
                chunk = data[start:end]

                print(f"  Context at offset {pos}:")
                print(f"    Hex: {chunk.hex()}")

                # Try to interpret as 568-byte record starting at various alignments
                for align_offset in [-20, -10, 0]:
                    record_start = pos + align_offset
                    if record_start >= 0 and record_start + 568 <= len(data):
                        record = data[record_start:record_start+568]

                        # Check if this looks like a valid record
                        potential_id = struct.unpack('<I', record[0:4])[0]
                        if potential_id == record_id:
                            print(f"\n  *** Possible record alignment at offset {record_start} ***")

                            # Parse GUID at offset 454
                            guid_bytes = record[454:492]
                            if b'{' in guid_bytes:
                                guid_str = guid_bytes.decode('ascii', errors='ignore').split('\x00')[0]
                                print(f"    GUID: {guid_str}")

                            # Parse title at offset 10
                            title_bytes = record[10:422]
                            title = title_bytes.decode('mbcs', errors='ignore').split('\x00')[0].strip()
                            print(f"    Title: {repr(title[:80])}")

                            # Parse size at offset 422
                            size = struct.unpack('<I', record[422:426])[0]
                            print(f"    Size: {size}")

                            # Dump potential date field locations
                            print(f"\n    Potential date fields:")
                            for offset in [203, 426, 430, 432, 454, 492, 500, 520]:
                                if offset + 8 <= len(record):
                                    hex_chunk = record[offset:offset+8]
                                    print(f"      Offset {offset:3d}: {hex_chunk.hex()}", end='')

                                    # Try to interpret as double (Delphi TDateTime)
                                    try:
                                        as_double = struct.unpack('<d', hex_chunk)[0]
                                        if 40000 < as_double < 50000:  # Reasonable date range (2009-2036)
                                            from datetime import datetime, timedelta
                                            base = datetime(1899, 12, 30)
                                            date = base + timedelta(days=as_double)
                                            print(f"  -> Delphi date: {date.strftime('%m/%d/%Y %I:%M:%S %p')}")
                                        else:
                                            print()
                                    except:
                                        print()
        else:
            print(f"Record ID {record_id} NOT FOUND")

if __name__ == '__main__':
    main()
