#!/usr/bin/env python3
"""
Try to find the timestamp for record 5969 in various date/time formats
"""
import struct
from datetime import datetime, timedelta

def main():
    clipdata_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/ClipData.dat"

    with open(clipdata_path, 'rb') as f:
        data = f.read()

    # Target: Record 5969, timestamp "12/11/2025 11:14:28 AM"
    target_datetime = datetime(2025, 12, 11, 11, 14, 28)

    # Convert to various formats for comparison
    unix_timestamp = int(target_datetime.timestamp())
    windows_filetime = int((target_datetime - datetime(1601, 1, 1)).total_seconds() * 10000000)
    delphi_datetime = (target_datetime - datetime(1899, 12, 30)).total_seconds() / 86400.0

    print(f"Target: 12/11/2025 11:14:28 AM")
    print(f"Unix timestamp: {unix_timestamp} (0x{unix_timestamp:08x})")
    print(f"Windows FILETIME: {windows_filetime} (0x{windows_filetime:016x})")
    print(f"Delphi TDateTime: {delphi_datetime:.10f}")
    print()

    # From earlier scan, record 5969 was found at offset 13887
    record_offset = 13887
    record_size = 568  # Assuming similar structure

    record_data = data[record_offset:record_offset + record_size]

    print(f"=== Analyzing record at offset {record_offset} ===\n")

    # Try to find date in various formats at every offset
    matches = []

    for offset in range(len(record_data) - 8):
        chunk_8 = record_data[offset:offset + 8]
        chunk_4 = record_data[offset:offset + 4]

        # Try as Unix timestamp (4-byte)
        try:
            as_unix_4 = struct.unpack('<I', chunk_4)[0]
            as_datetime_4 = datetime.fromtimestamp(as_unix_4)
            # Check if within 1 hour of target
            if abs((as_datetime_4 - target_datetime).total_seconds()) < 3600:
                matches.append((offset, 'Unix-4byte', as_datetime_4, chunk_4.hex()))
        except:
            pass

        # Try as Unix timestamp (8-byte)
        try:
            as_unix_8 = struct.unpack('<Q', chunk_8)[0]
            if as_unix_8 < 2**32:  # Reasonable range
                as_datetime_8 = datetime.fromtimestamp(as_unix_8)
                if abs((as_datetime_8 - target_datetime).total_seconds()) < 3600:
                    matches.append((offset, 'Unix-8byte', as_datetime_8, chunk_8.hex()))
        except:
            pass

        # Try as Windows FILETIME (8-byte)
        try:
            as_filetime = struct.unpack('<Q', chunk_8)[0]
            if 100000000000000000 < as_filetime < 200000000000000000:  # Reasonable range
                as_datetime_ft = datetime(1601, 1, 1) + timedelta(microseconds=as_filetime / 10)
                if abs((as_datetime_ft - target_datetime).total_seconds()) < 3600:
                    matches.append((offset, 'Windows FILETIME', as_datetime_ft, chunk_8.hex()))
        except:
            pass

        # Try as Delphi TDateTime (8-byte double)
        try:
            as_delphi = struct.unpack('<d', chunk_8)[0]
            if 46000 < as_delphi < 46010:  # Around 12/11/2025
                as_datetime_delphi = datetime(1899, 12, 30) + timedelta(days=as_delphi)
                if abs((as_datetime_delphi - target_datetime).total_seconds()) < 3600:
                    matches.append((offset, 'Delphi TDateTime', as_datetime_delphi, chunk_8.hex()))
        except:
            pass

        # Try as MS-DOS date/time (4-byte)
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
                    as_datetime_dos = datetime(year, month, day, hour, minute, second)
                    if abs((as_datetime_dos - target_datetime).total_seconds()) < 3600:
                        matches.append((offset, 'MS-DOS datetime', as_datetime_dos, chunk_4.hex()))
        except:
            pass

    if matches:
        print("*** FOUND MATCHING TIMESTAMPS ***\n")
        for offset, format_name, dt, hex_val in matches:
            print(f"Offset {offset}: {format_name}")
            print(f"  Value: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
            print(f"  Hex: {hex_val}")
            print(f"  Difference from target: {(dt - target_datetime).total_seconds():.1f} seconds")
            print()
    else:
        print("NO MATCHING TIMESTAMPS FOUND")
        print("\nDumping record hex for manual inspection:")
        for i in range(0, min(568, len(record_data)), 16):
            chunk = record_data[i:i+16]
            hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
            print(f"  {i:3d}: {hex_str}")

if __name__ == '__main__':
    main()
