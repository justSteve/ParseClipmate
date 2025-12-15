#!/usr/bin/env python3
"""
Examine the record at offset 128,168 in CLIP.dat
This is what ClipMate reads when displaying a clip with timestamp
"""
import struct
from datetime import datetime, timedelta

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        f.seek(128168)
        record_data = f.read(568)

    print(f"Record at offset 128,168 in CLIP.dat ({len(record_data)} bytes)")
    print("="*100 + "\n")

    # Try to parse record ID at various common offsets
    possible_id_offsets = [0, 373, 454]

    for offset in possible_id_offsets:
        if offset + 4 <= len(record_data):
            record_id = struct.unpack('<I', record_data[offset:offset+4])[0]
            if 1000 < record_id < 10000:  # Reasonable range
                print(f"Possible Record ID at offset +{offset}: {record_id}")

    # Dump the entire record in hex
    print(f"\nFull record hex dump:")
    for i in range(0, len(record_data), 16):
        chunk = record_data[i:i+16]
        hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])

        # Try to decode as text
        text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])

        print(f"  {128168 + i:6d} (+{i:3d}): {hex_str:<48} | {text}")

    # Now search for timestamps at EVERY offset
    print(f"\n\nSearching for timestamps (trying all major formats):")
    print("="*100 + "\n")

    found_timestamps = []

    for offset in range(0, len(record_data) - 8):
        bytes_4 = record_data[offset:offset+4]
        bytes_8 = record_data[offset:offset+8]

        # Skip all zeros
        if bytes_8 == b'\x00' * 8:
            continue

        # Try Unix timestamp
        try:
            ts = struct.unpack('<I', bytes_4)[0]
            if 1733000000 < ts < 1735000000:  # December 2025 range
                dt = datetime.fromtimestamp(ts)
                found_timestamps.append((offset, 'Unix32', dt, bytes_4.hex()))
        except:
            pass

        # Try Delphi TDateTime
        try:
            delphi = struct.unpack('<d', bytes_8)[0]
            if 46000 < delphi < 46020:  # December 2025 range
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                found_timestamps.append((offset, 'Delphi', dt, bytes_8.hex()))
        except:
            pass

        # Try Windows FILETIME
        try:
            ft = struct.unpack('<Q', bytes_8)[0]
            if 100000000000000000 < ft < 200000000000000000:
                dt = datetime(1601, 1, 1) + timedelta(microseconds=ft / 10)
                if 2025 == dt.year and dt.month == 12:
                    found_timestamps.append((offset, 'FILETIME', dt, bytes_8.hex()))
        except:
            pass

    if found_timestamps:
        print(f"Found {len(found_timestamps)} timestamp candidates:\n")
        for offset, fmt, dt, hex_val in found_timestamps:
            print(f"  Offset +{offset:3d}: {fmt:<10} {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
            print(f"    Hex: {hex_val}\n")
    else:
        print("No timestamps found in standard formats")

if __name__ == '__main__':
    main()
