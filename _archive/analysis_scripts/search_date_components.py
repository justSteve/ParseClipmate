#!/usr/bin/env python3
"""
Search for date/time stored as separate component bytes
For 12/11/2025 11:14:28 AM:
  Year: 2025 (0x07E9)
  Month: 12 (0x0C)
  Day: 11 (0x0B)
  Hour: 11 (0x0B)
  Minute: 14 (0x0E)
  Second: 28 (0x1C)
"""
import struct

def search_for_components(data, record_start, record_id, year, month, day, hour, minute, second):
    """Search for date components near record"""
    record_data = data[record_start:record_start + 568]

    print(f"\nRecord {record_id}: {month}/{day}/{year} {hour}:{minute}:{second}")
    print(f"Looking for: year={year}(0x{year:04x}), month={month}, day={day}, hour={hour}, min={minute}, sec={second}")

    # Search for various byte patterns
    patterns_found = []

    # Pattern 1: Year as 2-byte LE, then month, day, hour, min, sec as individual bytes
    # [E9 07] [0C] [0B] [0B] [0E] [1C]
    pattern1 = struct.pack('<H', year) + bytes([month, day, hour, minute, second])
    pos = record_data.find(pattern1)
    if pos != -1:
        patterns_found.append((pos, 'Year2LE+bytes', pattern1.hex()))

    # Pattern 2: Year as 2-byte BE, then bytes
    pattern2 = struct.pack('>H', year) + bytes([month, day, hour, minute, second])
    pos = record_data.find(pattern2)
    if pos != -1:
        patterns_found.append((pos, 'Year2BE+bytes', pattern2.hex()))

    # Pattern 3: All as 2-byte LE values
    pattern3 = struct.pack('<HHHHHH', year, month, day, hour, minute, second)
    pos = record_data.find(pattern3)
    if pos != -1:
        patterns_found.append((pos, 'All2byteLE', pattern3.hex()))

    # Pattern 4: Just look for month, day, hour, minute, second sequence
    pattern4 = bytes([month, day, hour, minute, second])
    offset = 0
    while True:
        pos = record_data.find(pattern4, offset)
        if pos == -1:
            break
        # Check if year (2025) is nearby
        if pos >= 2:
            year_check = struct.unpack('<H', record_data[pos-2:pos])[0]
            if year_check == year:
                patterns_found.append((pos-2, 'Year2LE before', record_data[pos-2:pos+len(pattern4)].hex()))
        patterns_found.append((pos, 'Month-day-hour-min-sec', pattern4.hex()))
        offset = pos + 1
        if offset >= len(record_data):
            break

    # Pattern 5: Look for just the time components (hour, minute, second)
    pattern5 = bytes([hour, minute, second])
    offset = 0
    while True:
        pos = record_data.find(pattern5, offset)
        if pos == -1:
            break
        patterns_found.append((pos, 'Hour-min-sec', pattern5.hex()))
        offset = pos + 1
        if offset >= len(record_data):
            break

    # Pattern 6: BCD encoding (each digit in a nibble)
    # 2025 = 0x2025 in BCD, 12 = 0x12, etc
    year_bcd = 0x2025
    month_bcd = 0x12
    day_bcd = 0x11
    hour_bcd = 0x11
    min_bcd = 0x14
    sec_bcd = 0x28

    pattern6 = struct.pack('<HBBBBB', year_bcd, month_bcd, day_bcd, hour_bcd, min_bcd, sec_bcd)
    pos = record_data.find(pattern6)
    if pos != -1:
        patterns_found.append((pos, 'BCD encoding', pattern6.hex()))

    if patterns_found:
        print(f"  Found {len(patterns_found)} pattern match(es):")
        for offset, pattern_name, hex_val in patterns_found:
            print(f"    Offset +{offset:3d}: {pattern_name} = {hex_val}")
            # Show context
            context_start = max(0, offset - 8)
            context_end = min(len(record_data), offset + 20)
            context = record_data[context_start:context_end]
            print(f"      Context: {context.hex()}")
    else:
        print(f"  No component patterns found")

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        data = f.read()

    print(f"CLIP.dat size: {len(data):,} bytes")
    print("="*80)

    # Test records with their timestamps
    test_records = [
        (53197, 5969, 2025, 12, 11, 11, 14, 28),  # 12/11/2025 11:14:28 AM
        (53765, 5968, 2025, 12, 11, 9, 41, 47),   # 12/11/2025 9:41:47 AM
        (54333, 5967, 2025, 12, 11, 9, 40, 33),   # 12/11/2025 9:40:33 AM
    ]

    for id_offset, record_id, year, month, day, hour, minute, second in test_records:
        record_start = id_offset - 373  # ID is at offset +373
        search_for_components(data, record_start, record_id, year, month, day, hour, minute, second)

if __name__ == '__main__':
    main()
