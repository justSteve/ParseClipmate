#!/usr/bin/env python3
"""
Find record 6001 with timestamp 12/13/2025 6:04:04 AM
"""
import struct
from datetime import datetime, timedelta

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        data = f.read()

    print(f"CLIP.dat size: {len(data):,} bytes\n")

    # Expected timestamp
    expected_dt = datetime(2025, 12, 13, 6, 4, 4)
    print(f"Looking for record 6001 with timestamp: {expected_dt.strftime('%m/%d/%Y %I:%M:%S %p')}\n")

    # Convert to various formats
    unix_ts = int(expected_dt.timestamp())
    delphi_ts = (expected_dt - datetime(1899, 12, 30)).total_seconds() / 86400.0

    print(f"Unix timestamp: {unix_ts} (0x{unix_ts:08x})")
    print(f"Delphi TDateTime: {delphi_ts:.10f}")
    print(f"Unix bytes (LE): {struct.pack('<I', unix_ts).hex()}")
    print(f"Delphi bytes: {struct.pack('<d', delphi_ts).hex()}\n")

    # Search for record ID 6001
    id_bytes = struct.pack('<I', 6001)
    print(f"Searching for record ID 6001 (bytes: {id_bytes.hex()})...")

    positions = []
    offset = 0
    while True:
        pos = data.find(id_bytes, offset)
        if pos == -1:
            break
        positions.append(pos)
        offset = pos + 1

    if positions:
        print(f"Found record ID 6001 at {len(positions)} position(s): {positions}\n")

        for pos in positions:
            print(f"\n{'='*100}")
            print(f"Record ID 6001 at offset {pos}")
            print(f"{'='*100}")

            # Check for timestamps within 200 bytes
            search_start = max(0, pos - 200)
            search_end = min(len(data), pos + 200)

            # Try Unix timestamp
            unix_found = False
            for i in range(search_start, search_end - 4):
                try:
                    ts = struct.unpack('<I', data[i:i+4])[0]
                    if abs(ts - unix_ts) < 3600:  # Within 1 hour
                        dt = datetime.fromtimestamp(ts)
                        diff = abs((dt - expected_dt).total_seconds())
                        offset_from_id = i - pos
                        print(f"\nUnix timestamp at offset {i} ({offset_from_id:+d} from ID):")
                        print(f"  DateTime: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
                        print(f"  Hex: {data[i:i+4].hex()}")
                        print(f"  Difference: {diff:.1f} seconds")
                        if diff < 60:
                            print(f"  *** EXCELLENT MATCH ***")
                        unix_found = True
                except:
                    pass

            # Try Delphi TDateTime
            delphi_found = False
            for i in range(search_start, search_end - 8):
                try:
                    delphi = struct.unpack('<d', data[i:i+8])[0]
                    if abs(delphi - delphi_ts) < 0.05:  # Within ~1 hour
                        dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                        diff = abs((dt - expected_dt).total_seconds())
                        offset_from_id = i - pos
                        print(f"\nDelphi TDateTime at offset {i} ({offset_from_id:+d} from ID):")
                        print(f"  DateTime: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
                        print(f"  Hex: {data[i:i+8].hex()}")
                        print(f"  Difference: {diff:.1f} seconds")
                        if diff < 60:
                            print(f"  *** EXCELLENT MATCH ***")
                        delphi_found = True
                except:
                    pass

            if not unix_found and not delphi_found:
                print(f"\nNo matching timestamps found within 200 bytes of record ID")

                # Dump the record area
                print(f"\nHex dump around record ID:")
                dump_start = max(0, pos - 40)
                dump_end = min(len(data), pos + 200)
                chunk = data[dump_start:dump_end]

                for i in range(0, len(chunk), 16):
                    line = chunk[i:i+16]
                    offset_label = dump_start + i
                    hex_str = ' '.join([line[j:j+2].hex() for j in range(0, len(line), 2)])
                    text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in line])

                    marker = ""
                    if dump_start + i <= pos < dump_start + i + 16:
                        marker = "  <-- ID HERE"

                    print(f"  {offset_label:6d}: {hex_str:<48} | {text}{marker}")
    else:
        print(f"Record ID 6001 NOT FOUND in CLIP.dat")

    # Also check offset 0 (the 512 bytes Process Monitor showed)
    print(f"\n\n{'='*100}")
    print(f"Examining offset 0 (first 512 bytes - what Process Monitor read):")
    print(f"{'='*100}\n")

    header = data[0:512]
    for i in range(0, len(header), 16):
        chunk = header[i:i+16]
        hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
        text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
        print(f"  {i:6d}: {hex_str:<48} | {text}")

if __name__ == '__main__':
    main()
