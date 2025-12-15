#!/usr/bin/env python3
"""
Parse ClipData.dat structure to find timestamps
"""
import struct
from datetime import datetime, timedelta
import os

def try_parse_as_datetime(data, offset, formats=['delphi', 'unix32', 'unix64', 'filetime', 'msdos']):
    """Try to parse bytes at offset as various datetime formats"""
    results = []

    if offset + 8 > len(data):
        return results

    chunk_8 = data[offset:offset+8]
    chunk_4 = data[offset:offset+4]

    # Delphi TDateTime (8-byte double)
    if 'delphi' in formats:
        try:
            as_double = struct.unpack('<d', chunk_8)[0]
            if 40000 < as_double < 50000:  # Reasonable date range (2009-2036)
                dt = datetime(1899, 12, 30) + timedelta(days=as_double)
                results.append(('Delphi TDateTime', dt, chunk_8.hex()))
        except:
            pass

    # Unix timestamp (4-byte)
    if 'unix32' in formats:
        try:
            as_unix = struct.unpack('<I', chunk_4)[0]
            if 1000000000 < as_unix < 2000000000:  # ~2001-2033
                dt = datetime.fromtimestamp(as_unix)
                results.append(('Unix 32-bit', dt, chunk_4.hex()))
        except:
            pass

    # Unix timestamp (8-byte)
    if 'unix64' in formats:
        try:
            as_unix = struct.unpack('<Q', chunk_8)[0]
            if 1000000000 < as_unix < 2000000000:  # ~2001-2033
                dt = datetime.fromtimestamp(as_unix)
                results.append(('Unix 64-bit', dt, chunk_8.hex()))
        except:
            pass

    # Windows FILETIME
    if 'filetime' in formats:
        try:
            as_filetime = struct.unpack('<Q', chunk_8)[0]
            if 100000000000000000 < as_filetime < 200000000000000000:
                dt = datetime(1601, 1, 1) + timedelta(microseconds=as_filetime / 10)
                results.append(('Windows FILETIME', dt, chunk_8.hex()))
        except:
            pass

    # MS-DOS datetime
    if 'msdos' in formats:
        try:
            dos_datetime = struct.unpack('<I', chunk_4)[0]
            dos_time = dos_datetime & 0xFFFF
            dos_date = (dos_datetime >> 16) & 0xFFFF

            if dos_date > 0:
                year = 1980 + ((dos_date >> 9) & 0x7F)
                month = (dos_date >> 5) & 0x0F
                day = dos_date & 0x1F

                hour = (dos_time >> 11) & 0x1F
                minute = (dos_time >> 5) & 0x3F
                second = (dos_time & 0x1F) * 2

                if 2000 < year < 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                    dt = datetime(year, month, day, hour, minute, second)
                    results.append(('MS-DOS datetime', dt, chunk_4.hex()))
        except:
            pass

    return results

def find_record_structure(data, record_id, expected_datetime_str):
    """Find a specific record and analyze its structure"""
    expected_dt = datetime.strptime(expected_datetime_str, "%m/%d/%Y %I:%M:%S %p")
    id_bytes = struct.pack('<I', record_id)

    print(f"\n{'='*80}")
    print(f"Searching for Record ID {record_id}: {expected_datetime_str}")
    print(f"{'='*80}")

    # Find all occurrences of this record ID
    positions = []
    offset = 0
    while True:
        pos = data.find(id_bytes, offset)
        if pos == -1:
            break
        positions.append(pos)
        offset = pos + 1

    print(f"Found {len(positions)} occurrences at positions: {positions}\n")

    # Analyze each occurrence
    for idx, pos in enumerate(positions):
        print(f"--- Occurrence #{idx+1} at offset {pos} ---")

        # Extract context (100 bytes before and after)
        start = max(0, pos - 100)
        end = min(len(data), pos + 200)
        context = data[start:end]

        # Try to find timestamp in this context
        found_timestamps = []
        for i in range(len(context) - 8):
            actual_offset = start + i
            timestamps = try_parse_as_datetime(data, actual_offset)

            for fmt, dt, hex_val in timestamps:
                # Check if within 1 hour of expected
                diff_seconds = abs((dt - expected_dt).total_seconds())
                if diff_seconds < 3600:
                    found_timestamps.append((actual_offset, fmt, dt, hex_val, diff_seconds))

        if found_timestamps:
            print(f"\n*** FOUND {len(found_timestamps)} MATCHING TIMESTAMP(S) ***")
            for ts_offset, fmt, dt, hex_val, diff in found_timestamps:
                offset_from_id = ts_offset - pos
                print(f"\nOffset {ts_offset} ({offset_from_id:+d} from ID):")
                print(f"  Format: {fmt}")
                print(f"  Value: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
                print(f"  Hex: {hex_val}")
                print(f"  Difference: {diff:.1f} seconds")
        else:
            print("\nNo matching timestamps found in this context")

        # Dump hex for manual inspection
        print(f"\nHex dump around offset {pos}:")
        for i in range(0, min(120, len(context)), 16):
            chunk = context[i:i+16]
            actual_offset = start + i
            hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])

            # Highlight the ID position
            marker = "  <-- ID HERE" if start + i <= pos < start + i + 16 else ""
            print(f"  {actual_offset:6d}: {hex_str}{marker}")

        print()

def scan_entire_file_for_timestamps(data):
    """Scan entire file for any timestamps in Dec 2025"""
    print(f"\n{'='*80}")
    print("Scanning entire file for December 2025 timestamps...")
    print(f"{'='*80}\n")

    dec_2025_timestamps = []

    for offset in range(0, len(data) - 8, 4):  # Check every 4 bytes
        timestamps = try_parse_as_datetime(data, offset)

        for fmt, dt, hex_val in timestamps:
            # Check if in December 2025
            if dt.year == 2025 and dt.month == 12:
                dec_2025_timestamps.append((offset, fmt, dt, hex_val))

    if dec_2025_timestamps:
        print(f"Found {len(dec_2025_timestamps)} timestamps in December 2025:\n")

        # Group by format
        by_format = {}
        for offset, fmt, dt, hex_val in dec_2025_timestamps:
            if fmt not in by_format:
                by_format[fmt] = []
            by_format[fmt].append((offset, dt, hex_val))

        for fmt, entries in by_format.items():
            print(f"\n{fmt} ({len(entries)} found):")
            for offset, dt, hex_val in entries[:20]:  # First 20
                print(f"  Offset {offset:6d}: {dt.strftime('%m/%d/%Y %I:%M:%S %p')} [{hex_val}]")
            if len(entries) > 20:
                print(f"  ... and {len(entries) - 20} more")
    else:
        print("No December 2025 timestamps found")

def main():
    clipdata_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/ClipData.dat"

    with open(clipdata_path, 'rb') as f:
        data = f.read()

    print(f"ClipData.dat file size: {len(data):,} bytes")

    # First, scan entire file for any Dec 2025 timestamps
    scan_entire_file_for_timestamps(data)

    # Then analyze specific records from the screenshot
    test_records = [
        (5969, "12/11/2025 11:14:28 AM"),
        (5968, "12/11/2025 9:41:47 AM"),
        (5967, "12/11/2025 9:40:33 AM"),
    ]

    for record_id, dt_str in test_records:
        find_record_structure(data, record_id, dt_str)

if __name__ == '__main__':
    main()
