#!/usr/bin/env python3
"""
Analyze the 8 bytes at offset +528 in each record
"""
import struct
from datetime import datetime, timedelta

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        data = f.read()

    test_records = [
        (53197, 5969, "12/11/2025 11:14:28 AM"),
        (53765, 5968, "12/11/2025 9:41:47 AM"),
        (54333, 5967, "12/11/2025 9:40:33 AM"),
        (54901, 5966, "12/11/2025 9:40:20 AM"),
        (55469, 5965, "12/11/2025 9:39:46 AM"),
    ]

    print("Analyzing 8 bytes at offset +528 (relative to record start):\n")
    print(f"{'Record':<8} {'Expected DateTime':<25} {'Hex at +528':<20} {'Interpretations'}")
    print("="*100 + "\n")

    for id_offset, record_id, expected_dt_str in test_records:
        expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")

        # Calculate record start (records are 568 bytes, ID is at +373)
        record_start = id_offset - 373
        offset_528 = record_start + 528

        bytes_at_528 = data[offset_528:offset_528+8]
        hex_str = bytes_at_528.hex()

        print(f"{record_id:<8} {expected_dt_str:<25} {hex_str:<20}")

        # Try as Delphi TDateTime (8-byte double, little endian)
        try:
            delphi = struct.unpack('<d', bytes_at_528)[0]
            dt = datetime(1899, 12, 30) + timedelta(days=delphi)
            diff = abs((dt - expected_dt).total_seconds())
            print(f"  Delphi LE: {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s)")
        except:
            pass

        # Try as Delphi TDateTime (8-byte double, big endian)
        try:
            delphi = struct.unpack('>d', bytes_at_528)[0]
            dt = datetime(1899, 12, 30) + timedelta(days=delphi)
            diff = abs((dt - expected_dt).total_seconds())
            if 2020 < dt.year < 2030:
                print(f"  Delphi BE: {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s)")
        except:
            pass

        # Try first 4 bytes as Unix timestamp
        try:
            ts = struct.unpack('<I', bytes_at_528[:4])[0]
            if 1000000000 < ts < 2000000000:
                dt = datetime.fromtimestamp(ts)
                diff = abs((dt - expected_dt).total_seconds())
                print(f"  Unix32 (first 4): {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s)")
        except:
            pass

        # Try last 4 bytes as Unix timestamp
        try:
            ts = struct.unpack('<I', bytes_at_528[4:])[0]
            if 1000000000 < ts < 2000000000:
                dt = datetime.fromtimestamp(ts)
                diff = abs((dt - expected_dt).total_seconds())
                print(f"  Unix32 (last 4): {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s)")
        except:
            pass

        # Try as Windows FILETIME
        try:
            ft = struct.unpack('<Q', bytes_at_528)[0]
            if 100000000000000000 < ft < 200000000000000000:
                dt = datetime(1601, 1, 1) + timedelta(microseconds=ft / 10)
                diff = abs((dt - expected_dt).total_seconds())
                print(f"  FILETIME: {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.1f}s)")
        except:
            pass

        # Try treating first 4 bytes as float
        try:
            float_val = struct.unpack('<f', bytes_at_528[:4])[0]
            print(f"  Float (first 4): {float_val}")
        except:
            pass

        # Show bytes individually
        print(f"  Bytes: {' '.join([f'{b:02x}' for b in bytes_at_528])}")
        print()

if __name__ == '__main__':
    main()
