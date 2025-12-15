#!/usr/bin/env python3
"""
Deep analysis of CLIP.dat records to find timestamp field
"""
import struct
from datetime import datetime, timedelta

def analyze_record_structure(data, offset, record_id, expected_dt_str):
    """Analyze every byte of a record structure"""
    print(f"\n{'='*80}")
    print(f"Record {record_id} at offset {offset}")
    print(f"Expected: {expected_dt_str}")
    print(f"{'='*80}\n")

    expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")

    # Try to determine record boundaries
    # Based on previous analysis, records are 568 bytes in Layout B
    record_start = offset - (offset % 568)
    record_data = data[record_start:record_start + 568]

    print(f"Record boundaries: {record_start} to {record_start + 568}")
    print(f"Record ID offset within record: {offset - record_start}\n")

    # Try EVERY possible timestamp interpretation at EVERY offset
    candidates = []

    for i in range(len(record_data) - 8):
        chunk_8 = record_data[i:i+8]
        chunk_4 = record_data[i:i+4]
        chunk_2 = record_data[i:i+2]

        # 1. Unix timestamp (4-byte, little endian)
        try:
            ts = struct.unpack('<I', chunk_4)[0]
            if 1000000000 < ts < 2000000000:
                dt = datetime.fromtimestamp(ts)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 86400:  # Within 24 hours
                    candidates.append((i, 'Unix32-LE', dt, diff, chunk_4.hex()))
        except:
            pass

        # 2. Unix timestamp (4-byte, big endian)
        try:
            ts = struct.unpack('>I', chunk_4)[0]
            if 1000000000 < ts < 2000000000:
                dt = datetime.fromtimestamp(ts)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 86400:
                    candidates.append((i, 'Unix32-BE', dt, diff, chunk_4.hex()))
        except:
            pass

        # 3. Delphi TDateTime (8-byte double, little endian)
        try:
            delphi = struct.unpack('<d', chunk_8)[0]
            if 46000 < delphi < 46010:
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 86400:
                    candidates.append((i, 'Delphi-LE', dt, diff, chunk_8.hex()))
        except:
            pass

        # 4. Delphi TDateTime (8-byte double, big endian)
        try:
            delphi = struct.unpack('>d', chunk_8)[0]
            if 46000 < delphi < 46010:
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 86400:
                    candidates.append((i, 'Delphi-BE', dt, diff, chunk_8.hex()))
        except:
            pass

        # 5. Windows FILETIME (8-byte)
        try:
            ft = struct.unpack('<Q', chunk_8)[0]
            if 100000000000000000 < ft < 200000000000000000:
                dt = datetime(1601, 1, 1) + timedelta(microseconds=ft / 10)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 86400:
                    candidates.append((i, 'FILETIME', dt, diff, chunk_8.hex()))
        except:
            pass

        # 6. MS-DOS datetime (4-byte)
        try:
            dos_val = struct.unpack('<I', chunk_4)[0]
            dos_time = dos_val & 0xFFFF
            dos_date = (dos_val >> 16) & 0xFFFF

            if dos_date > 0:
                year = 1980 + ((dos_date >> 9) & 0x7F)
                month = (dos_date >> 5) & 0x0F
                day = dos_date & 0x1F

                hour = (dos_time >> 11) & 0x1F
                minute = (dos_time >> 5) & 0x3F
                second = (dos_time & 0x1F) * 2

                if 2020 < year < 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                    dt = datetime(year, month, day, hour, minute, second)
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 86400:
                        candidates.append((i, 'DOS-datetime', dt, diff, chunk_4.hex()))
        except:
            pass

        # 7. Separate date/time components (various formats)
        # Year (2-byte): 2025
        if struct.unpack('<H', chunk_2)[0] == 2025:
            # Check if followed by month (1-12) and day (1-31)
            if i + 6 <= len(record_data):
                try:
                    month = struct.unpack('<H', record_data[i+2:i+4])[0]
                    day = struct.unpack('<H', record_data[i+4:i+6])[0]

                    if 1 <= month <= 12 and 1 <= day <= 31:
                        # Try to find hour/minute/second
                        if i + 12 <= len(record_data):
                            hour = struct.unpack('<H', record_data[i+6:i+8])[0]
                            minute = struct.unpack('<H', record_data[i+8:i+10])[0]
                            second = struct.unpack('<H', record_data[i+10:i+12])[0]

                            if 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60:
                                dt = datetime(2025, month, day, hour, minute, second)
                                diff = abs((dt - expected_dt).total_seconds())
                                if diff < 86400:
                                    candidates.append((i, 'Components-2byte', dt, diff, record_data[i:i+12].hex()))
                except:
                    pass

        # 8. Packed BCD datetime (various formats)
        # Year could be in BCD format
        # ...many other possibilities

    # Sort by closest match
    candidates.sort(key=lambda x: x[3])

    if candidates:
        print(f"Found {len(candidates)} candidate timestamp(s):\n")

        for offset_in_rec, fmt, dt, diff, hex_val in candidates[:10]:  # Top 10
            match_marker = ""
            if diff < 1:
                match_marker = " *** PERFECT MATCH ***"
            elif diff < 60:
                match_marker = " *** EXCELLENT MATCH ***"
            elif diff < 300:
                match_marker = " *** GOOD MATCH ***"

            print(f"  Offset {record_start + offset_in_rec} (record+{offset_in_rec:3d}): {fmt}")
            print(f"    DateTime: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
            print(f"    Hex: {hex_val}")
            print(f"    Difference: {diff:.1f} seconds{match_marker}\n")

    else:
        print("No candidate timestamps found\n")

    # Dump full record in hex
    print("Full record hex dump:")
    for i in range(0, len(record_data), 16):
        chunk = record_data[i:i+16]
        hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])

        marker = ""
        if i <= offset - record_start < i + 16:
            marker = "  <-- ID HERE"

        print(f"  {record_start + i:6d} (+{i:3d}): {hex_str}{marker}")

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        data = f.read()

    print(f"CLIP.dat size: {len(data):,} bytes")

    # Analyze the records we found
    test_records = [
        (53197, 5969, "12/11/2025 11:14:28 AM"),
        (53765, 5968, "12/11/2025 9:41:47 AM"),
        (54333, 5967, "12/11/2025 9:40:33 AM"),
    ]

    for offset, record_id, dt_str in test_records:
        analyze_record_structure(data, offset, record_id, dt_str)

if __name__ == '__main__':
    main()
