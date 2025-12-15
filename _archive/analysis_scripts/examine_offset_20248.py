#!/usr/bin/env python3
"""
Examine offset 20,248 in CLIP.dat for December 13 timestamps
"""
import struct
from datetime import datetime, timedelta

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        f.seek(20248)
        data = f.read(6248)

    print(f"Read {len(data)} bytes from offset 20,248")
    print("="*100 + "\n")

    # Search for ALL timestamps in this chunk (December 13 or 14, 2025)
    timestamps_found = []

    for offset in range(0, len(data) - 8):
        bytes_4 = data[offset:offset+4]
        bytes_8 = data[offset:offset+8]

        # Skip all zeros
        if bytes_8 == b'\x00' * 8:
            continue

        # Try Unix timestamp (Dec 13-14 range)
        try:
            ts = struct.unpack('<I', bytes_4)[0]
            if 1733990000 < ts < 1734300000:  # Dec 12-15, 2025 range
                dt = datetime.fromtimestamp(ts)
                timestamps_found.append((offset, 'Unix32', dt, bytes_4.hex()))
        except:
            pass

        # Try Delphi TDateTime
        try:
            delphi = struct.unpack('<d', bytes_8)[0]
            if 46010 < delphi < 46015:  # Dec 12-15, 2025 range
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                timestamps_found.append((offset, 'Delphi', dt, bytes_8.hex()))
        except:
            pass

    if timestamps_found:
        print(f"Found {len(timestamps_found)} timestamp candidate(s) in December 12-15 range:\n")

        # Group by date
        by_date = {}
        for offset, fmt, dt, hex_val in timestamps_found:
            date_key = dt.strftime('%m/%d/%Y')
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append((offset, fmt, dt, hex_val))

        for date_key in sorted(by_date.keys()):
            print(f"\n{date_key}:")
            for offset, fmt, dt, hex_val in by_date[date_key]:
                abs_offset = 20248 + offset
                print(f"  Offset {abs_offset:6d} (+{offset:4d}): {fmt:<10} {dt.strftime('%I:%M:%S %p')}")
                print(f"    Hex: {hex_val}")

        # Look for record IDs near these timestamps
        print(f"\n\nSearching for record IDs near timestamps:")
        print("="*100)

        # Look for record IDs from mostrecent.jpg (6006-6021)
        for record_id in range(6006, 6022):
            id_bytes = struct.pack('<I', record_id)
            pos = data.find(id_bytes)
            if pos != -1:
                abs_offset = 20248 + pos
                print(f"\nRecord ID {record_id} found at offset {abs_offset} (+{pos})")

                # Check for timestamps within 200 bytes
                nearby_timestamps = [
                    (offset, fmt, dt, hex_val)
                    for offset, fmt, dt, hex_val in timestamps_found
                    if abs(offset - pos) < 200
                ]

                if nearby_timestamps:
                    print(f"  Timestamps within 200 bytes:")
                    for ts_offset, fmt, dt, hex_val in nearby_timestamps:
                        dist = ts_offset - pos
                        print(f"    {dist:+4d} bytes: {fmt} = {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
    else:
        print("No timestamps found in December 12-15 range")

        # Dump first 1000 bytes for inspection
        print(f"\nFirst 1000 bytes of data at offset 20,248:")
        for i in range(0, min(1000, len(data)), 16):
            chunk = data[i:i+16]
            hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
            text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
            print(f"  {20248+i:6d} (+{i:4d}): {hex_str:<48} | {text}")

if __name__ == '__main__':
    main()
