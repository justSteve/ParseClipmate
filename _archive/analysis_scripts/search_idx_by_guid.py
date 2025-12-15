#!/usr/bin/env python3
"""
Search CLIP.idx for timestamps using GUID as the foreign key.
CLIP.idx doesn't contain record IDs, so it must link to CLIP.dat via GUIDs.
"""
import struct
from datetime import datetime, timedelta

# Test records with expected timestamps
TEST_RECORDS = [
    (6021, "12/14/2025 10:47:10 AM"),  # From mostrecent.jpg
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def extract_guid_from_clip_dat(data, record_id):
    """Extract GUID for a record ID from CLIP.dat"""
    id_bytes = struct.pack('<I', record_id)
    pos = data.find(id_bytes)

    if pos == -1:
        return None

    # GUID is at offset +454 in Layout B (568-byte records)
    record_num = pos // 568
    record_start = record_num * 568
    guid_offset = record_start + 454

    if guid_offset + 38 > len(data):
        return None

    guid_bytes = data[guid_offset:guid_offset + 38]
    try:
        guid_str = guid_bytes.decode('ascii', errors='ignore').strip('\x00')
        return guid_str
    except:
        return None

def search_for_timestamp(data, guid, expected_dt):
    """Search for GUID in data and check for timestamps nearby"""
    if not guid or len(guid) < 10:
        return None

    # Search for GUID (or part of it) in the data
    guid_part = guid[1:20].encode('ascii')  # Skip leading '{', take first chunk

    pos = data.find(guid_part)
    if pos == -1:
        return None

    results = []

    # Search within ±200 bytes of GUID
    search_start = max(0, pos - 200)
    search_end = min(len(data), pos + 200)

    for offset in range(search_start, search_end - 8):
        bytes_4 = data[offset:offset+4]
        bytes_8 = data[offset:offset+8]

        # Try Unix timestamp
        try:
            ts = struct.unpack('<I', bytes_4)[0]
            if 1733000000 < ts < 1735000000:
                dt = datetime.fromtimestamp(ts)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 3600:
                    results.append({
                        'offset': offset,
                        'offset_from_guid': offset - pos,
                        'format': 'Unix32',
                        'datetime': dt,
                        'diff_seconds': diff,
                        'hex': bytes_4.hex()
                    })
        except:
            pass

        # Try Delphi TDateTime
        try:
            delphi = struct.unpack('<d', bytes_8)[0]
            if 46000 < delphi < 46020:
                dt = datetime(1899, 12, 30) + timedelta(days=delphi)
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 3600:
                    results.append({
                        'offset': offset,
                        'offset_from_guid': offset - pos,
                        'format': 'Delphi',
                        'datetime': dt,
                        'diff_seconds': diff,
                        'hex': bytes_8.hex()
                    })
        except:
            pass

        # Try MS-DOS datetime
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
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 3600:
                        results.append({
                            'offset': offset,
                            'offset_from_guid': offset - pos,
                            'format': 'MS-DOS',
                            'datetime': dt,
                            'diff_seconds': diff,
                            'hex': bytes_4.hex()
                        })
        except:
            pass

    return results

def main():
    clip_dat_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"
    clip_idx_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.idx"

    with open(clip_dat_path, 'rb') as f:
        clip_dat = f.read()

    with open(clip_idx_path, 'rb') as f:
        clip_idx = f.read()

    print("="*100)
    print("SEARCHING CLIP.IDX FOR TIMESTAMPS USING GUID AS FOREIGN KEY")
    print("="*100)
    print(f"\nCLIP.dat: {len(clip_dat):,} bytes")
    print(f"CLIP.idx: {len(clip_idx):,} bytes\n")

    matches_found = 0

    for record_id, timestamp_str in TEST_RECORDS:
        expected_dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")

        # Extract GUID from CLIP.dat
        guid = extract_guid_from_clip_dat(clip_dat, record_id)

        print(f"Record {record_id} - Expected: {timestamp_str}")

        if not guid:
            print(f"  GUID not found in CLIP.dat")
            continue

        print(f"  GUID: {guid}")

        # Search for timestamps near this GUID in CLIP.idx
        results = search_for_timestamp(clip_idx, guid, expected_dt)

        if results:
            print(f"  *** TIMESTAMPS FOUND in CLIP.idx! ***")
            matches_found += 1

            for r in results:
                marker = " *** MATCH ***" if r['diff_seconds'] < 60 else ""
                print(f"    Offset {r['offset']} ({r['offset_from_guid']:+4d} from GUID):")
                print(f"      Format: {r['format']}")
                print(f"      DateTime: {r['datetime'].strftime('%m/%d/%Y %I:%M:%S %p')}")
                print(f"      Difference: {r['diff_seconds']:.1f} seconds{marker}")
                print(f"      Hex: {r['hex']}")
        else:
            print(f"  No timestamps found near GUID in CLIP.idx")

        print()

    print(f"{'='*100}")
    print(f"SUMMARY: Found timestamps for {matches_found} out of {len(TEST_RECORDS)} records")
    print(f"{'='*100}")

    if matches_found > 0:
        print("\n*** SUCCESS! The timestamp foreign key relationship is GUID-based in CLIP.idx! ***")
    else:
        print("\nNo matches found. Timestamps may be stored elsewhere or in a different format.")

if __name__ == '__main__':
    main()
