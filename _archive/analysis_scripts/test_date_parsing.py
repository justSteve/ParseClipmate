"""
Test script to analyze and parse date fields from CLIP.idx records.

Based on previous debugging, we know:
- Layout B records have a predictable structure
- Record ID 5724 was created on 12/1/2025 around 15:22:20
- Various date encoding schemes were tested without success

This script will:
1. Locate record 5724 in CLIP.idx
2. Analyze all possible date field locations
3. Test multiple date encoding formats
"""

import struct
import os
import datetime
from clipmate_parser import ClipmateParser, clean_string


def test_date_formats(data, target_date=None):
    """
    Test various date encoding formats at different offsets.

    Target date for record 5724: December 1, 2025, 15:22:20 (approx 3:22 PM)
    """
    if target_date is None:
        target_date = datetime.datetime(2025, 12, 1, 15, 22, 20)

    print(f"\nTarget Date: {target_date}")
    print("=" * 70)

    # Calculate expected values in different formats
    unix_ts = int(target_date.timestamp())  # 1764624140
    print(f"Expected Unix Timestamp: {unix_ts}")

    # TDateTime (Delphi): Days since 1899-12-30 (as double)
    delta = target_date - datetime.datetime(1899, 12, 30)
    tdatetime_val = delta.days + (delta.seconds / 86400.0)
    print(f"Expected TDateTime: {tdatetime_val}")

    # Windows FileTime: 100-nanosecond intervals since 1601-01-01
    delta_ft = target_date - datetime.datetime(1601, 1, 1)
    filetime_val = int(delta_ft.total_seconds() * 10000000)
    print(f"Expected FileTime: {filetime_val}")

    # DOS Date/Time (16-bit date + 16-bit time packed into 32 bits)
    dos_date = ((target_date.year - 1980) <<
                9) | (target_date.month << 5) | target_date.day
    dos_time = (target_date.hour << 11) | (
        target_date.minute << 5) | (target_date.second // 2)
    dos_datetime = (dos_date << 16) | dos_time
    print(f"Expected DOS DateTime: 0x{dos_datetime:08X}")

    print("\n" + "=" * 70)
    print("SCANNING RECORD DATA")
    print("=" * 70)

    results = []

    # Scan for Unix timestamps (32-bit int)
    print("\n[1] Scanning for Unix Timestamps (Int32)...")
    for offset in range(len(data) - 4):
        val = struct.unpack('<I', data[offset:offset+4])[0]

        # Check if it's within a reasonable range (2020-2030)
        if 1577836800 < val < 1893456000:  # Jan 1, 2020 to Jan 1, 2030
            try:
                dt = datetime.datetime.fromtimestamp(val)
                diff_seconds = abs((dt - target_date).total_seconds())

                if diff_seconds < 86400:  # Within 1 day
                    results.append({
                        'offset': offset,
                        'type': 'Unix Timestamp',
                        'value': val,
                        'date': dt,
                        'diff_seconds': diff_seconds
                    })
                    print(
                        f"  Offset {offset:3d}: {val} -> {dt} (diff: {diff_seconds:.0f}s)")
            except:
                pass

    # Scan for TDateTime values (64-bit double)
    print("\n[2] Scanning for TDateTime (Double)...")
    for offset in range(len(data) - 8):
        try:
            val = struct.unpack('<d', data[offset:offset+8])[0]

            # TDateTime range check (reasonable dates between 1900-2100)
            if 0 < val < 100000:
                try:
                    dt = datetime.datetime(
                        1899, 12, 30) + datetime.timedelta(days=val)

                    if datetime.datetime(2020, 1, 1) < dt < datetime.datetime(2030, 1, 1):
                        diff_seconds = abs((dt - target_date).total_seconds())

                        if diff_seconds < 86400:
                            results.append({
                                'offset': offset,
                                'type': 'TDateTime',
                                'value': val,
                                'date': dt,
                                'diff_seconds': diff_seconds
                            })
                            print(
                                f"  Offset {offset:3d}: {val:.6f} -> {dt} (diff: {diff_seconds:.0f}s)")
                except:
                    pass
        except:
            pass

    # Scan for FileTime (64-bit int)
    print("\n[3] Scanning for Windows FileTime (Int64)...")
    for offset in range(len(data) - 8):
        val = struct.unpack('<Q', data[offset:offset+8])[0]

        # FileTime range check
        if 100000000000000000 < val < 200000000000000000:  # Approx 1970-2100
            try:
                dt = datetime.datetime(1601, 1, 1) + \
                    datetime.timedelta(microseconds=val/10)

                if datetime.datetime(2020, 1, 1) < dt < datetime.datetime(2030, 1, 1):
                    diff_seconds = abs((dt - target_date).total_seconds())

                    if diff_seconds < 86400:
                        results.append({
                            'offset': offset,
                            'type': 'FileTime',
                            'value': val,
                            'date': dt,
                            'diff_seconds': diff_seconds
                        })
                        print(
                            f"  Offset {offset:3d}: {val} -> {dt} (diff: {diff_seconds:.0f}s)")
            except:
                pass

    # Scan for DOS DateTime (32-bit packed)
    print("\n[4] Scanning for DOS DateTime (Int32)...")
    for offset in range(len(data) - 4):
        val = struct.unpack('<I', data[offset:offset+4])[0]

        try:
            time_part = val & 0xFFFF
            date_part = (val >> 16) & 0xFFFF

            year = ((date_part >> 9) & 0x7F) + 1980
            month = (date_part >> 5) & 0x0F
            day = date_part & 0x1F

            if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                hour = (time_part >> 11) & 0x1F
                minute = (time_part >> 5) & 0x3F
                second = (time_part & 0x1F) * 2

                if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 60:
                    dt = datetime.datetime(
                        year, month, day, hour, minute, second)
                    diff_seconds = abs((dt - target_date).total_seconds())

                    if diff_seconds < 86400:
                        results.append({
                            'offset': offset,
                            'type': 'DOS DateTime',
                            'value': val,
                            'date': dt,
                            'diff_seconds': diff_seconds
                        })
                        print(
                            f"  Offset {offset:3d}: 0x{val:08X} -> {dt} (diff: {diff_seconds:.0f}s)")
        except:
            pass

    # Summary of best matches
    print("\n" + "=" * 70)
    print("BEST MATCHES (sorted by accuracy)")
    print("=" * 70)

    if results:
        results.sort(key=lambda x: x['diff_seconds'])
        for i, r in enumerate(results[:5], 1):
            print(f"{i}. Offset {r['offset']:3d} ({r['type']})")
            print(f"   Value: {r['value']}")
            print(f"   Date: {r['date']}")
            print(f"   Difference: {r['diff_seconds']:.0f} seconds")
            print()
    else:
        print("No date matches found!")

    return results


def main():
    # Use the exploration directory
    base_dir = r'exploration'

    if not os.path.exists(base_dir):
        print(f"Directory not found: {base_dir}")
        print("Trying archives directory...")
        base_dir = r'archives\ClipMate7_DB_My Clips_2025-09-02_1733'

    parser = ClipmateParser(base_dir)

    print("Parsing CLIP records...")
    clips = parser.parse_clips()

    # Find record 5724
    target_record = None
    for clip in clips:
        if clip['native_id'] == 5724:
            target_record = clip
            break

    if target_record:
        print(f"\nFound Record 5724:")
        print(f"  Title: {target_record['title']}")
        print(f"  GUID: {target_record['guid']}")
        print(f"  Creator: {target_record['creator']}")
        print(f"  Size: {target_record['size']}")

        # Analyze the raw data
        raw_data = target_record['raw_data']
        print(f"\nRecord size: {len(raw_data)} bytes")

        # Test date parsing
        results = test_date_formats(raw_data)

        if results:
            print(f"\n{'=' * 70}")
            print("RECOMMENDED DATE FIELD LOCATION")
            print('=' * 70)
            best = results[0]
            print(f"Offset: {best['offset']}")
            print(f"Type: {best['type']}")
            print(f"Date: {best['date']}")

    else:
        print("\nRecord 5724 not found. Analyzing first few records instead...")
        for i, clip in enumerate(clips[:10]):
            print(f"\nRecord {i+1} (ID: {clip['native_id']}):")
            print(f"  Title: {clip['title'][:50]}")
            results = test_date_formats(clip['raw_data'])
            if results:
                best = results[0]
                print(
                    f"  -> Best date match at offset {best['offset']}: {best['date']}")


if __name__ == "__main__":
    main()
