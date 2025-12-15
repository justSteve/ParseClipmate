#!/usr/bin/env python3
"""
Deep analysis of CLIP.idx - the main index file for CLIP.dat.
CLIP.idx (677KB) is almost the same size as CLIP.dat (679KB), suggesting it might
mirror the record structure with additional index data (like timestamps!).
"""
import struct
from datetime import datetime, timedelta

# Known test records
TEST_RECORDS = [
    (6021, "12/14/2025 11:25:30 AM"),
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6016, "12/13/2025 4:06:46 PM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def parse_all_timestamps(data, offset, context_size=200):
    """Parse timestamps in all formats from a region"""
    matches = []

    for i in range(max(0, offset - context_size), min(len(data) - 8, offset + context_size)):
        bytes_4 = data[i:i+4]
        bytes_8 = data[i:i+8]

        # Unix 32-bit
        try:
            ts = struct.unpack('<I', bytes_4)[0]
            if 1733000000 < ts < 1735000000:
                dt = datetime.fromtimestamp(ts)
                matches.append((i, 'Unix32', dt, bytes_4.hex()))
        except:
            pass

        # Delphi TDateTime
        try:
            delphi = struct.unpack('<d', bytes_8)[0]
            if 46000 < delphi < 46020:
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                matches.append((i, 'Delphi', dt, bytes_8.hex()))
        except:
            pass

        # MS-DOS datetime
        try:
            dos = struct.unpack('<I', bytes_4)[0]
            time_part = dos & 0xFFFF
            date_part = (dos >> 16) & 0xFFFF

            if date_part > 0:
                second = (time_part & 0x1F) * 2
                minute = (time_part >> 5) & 0x3F
                hour = (time_part >> 11) & 0x1F
                day = date_part & 0x1F
                month = (date_part >> 5) & 0x0F
                year = ((date_part >> 9) & 0x7F) + 1980

                if 2025 <= year <= 2026 and 1 <= month <= 12 and 1 <= day <= 31:
                    dt = datetime(year, month, day, hour, minute, second)
                    matches.append((i, 'MS-DOS', dt, bytes_4.hex()))
        except:
            pass

    return matches

def analyze_clip_idx():
    """Analyze CLIP.idx structure"""
    clip_idx_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.idx"
    clip_dat_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_idx_path, 'rb') as f:
        idx_data = f.read()

    with open(clip_dat_path, 'rb') as f:
        dat_data = f.read()

    print("="*100)
    print("DEEP ANALYSIS OF CLIP.IDX")
    print("="*100)
    print(f"\nCLIP.idx size: {len(idx_data):,} bytes")
    print(f"CLIP.dat size: {len(dat_data):,} bytes")
    print(f"Size ratio: {len(idx_data) / len(dat_data):.2%}\n")

    # First, let's find where record 6021 is in CLIP.dat
    id_6021 = struct.pack('<I', 6021)
    pos_in_dat = dat_data.find(id_6021)

    print(f"Record 6021 position in CLIP.dat: {pos_in_dat}")
    print(f"Record number (assuming 568-byte records): {pos_in_dat // 568}\n")

    # Now scan CLIP.idx for record ID patterns
    print("Searching CLIP.idx for test record IDs...\n")

    for record_id, timestamp_str in TEST_RECORDS:
        expected_dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")
        id_bytes = struct.pack('<I', record_id)

        # Find all occurrences of this ID in CLIP.idx
        positions = []
        offset = 0
        while True:
            pos = idx_data.find(id_bytes, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1

        if positions:
            print(f"Record {record_id} - Expected: {timestamp_str}")
            print(f"  Found at {len(positions)} position(s) in CLIP.idx: {positions[:5]}{'...' if len(positions) > 5 else ''}\n")

            # Analyze first occurrence in detail
            pos = positions[0]

            # Show hex dump around this position
            print(f"  Hex dump around position {pos}:")
            dump_start = max(0, pos - 80)
            dump_end = min(len(idx_data), pos + 120)

            for i in range(dump_start, dump_end, 16):
                chunk = idx_data[i:min(i+16, len(idx_data))]
                hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
                text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
                marker = "  <-- ID" if i <= pos < i + 16 else ""
                print(f"    {i:6d}: {hex_str:<48} | {text}{marker}")

            # Search for timestamps in this region
            matches = parse_all_timestamps(idx_data, pos, context_size=100)

            if matches:
                print(f"\n  Timestamps found within ±100 bytes:")
                for ts_offset, fmt, dt, hex_val in matches:
                    diff = abs((dt - expected_dt).total_seconds())
                    offset_from_id = ts_offset - pos
                    marker = " *** MATCH ***" if diff < 60 else ""
                    print(f"    Offset {ts_offset} ({offset_from_id:+4d} from ID): {fmt:<10} {dt.strftime('%m/%d/%Y %I:%M:%S %p')} (diff: {diff:.0f}s){marker}")
            else:
                print(f"\n  No timestamps found within ±100 bytes")

            print()
        else:
            print(f"Record {record_id} NOT FOUND in CLIP.idx\n")

    # Also check the header of CLIP.idx for structure info
    print("\n" + "="*100)
    print("CLIP.idx HEADER (first 256 bytes)")
    print("="*100 + "\n")

    for i in range(0, min(256, len(idx_data)), 16):
        chunk = idx_data[i:i+16]
        hex_str = ' '.join([chunk[j:j+2].hex() for j in range(0, len(chunk), 2)])
        text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
        print(f"  {i:6d}: {hex_str:<48} | {text}")

if __name__ == '__main__':
    analyze_clip_idx()
