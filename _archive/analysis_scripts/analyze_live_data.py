"""
Focus on LIVE ClipMate data to find the timestamp field.
We know:
1. There's a screen capture clip with a date in the title
2. There's a file location clip
3. The actual timestamp must be stored separately from the title
"""
import struct
import os
import datetime
from clipmate_parser import ClipmateParser


def analyze_live_clips():
    live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'

    parser = ClipmateParser(live_dir)
    clips = parser.parse_clips()

    print("="*80)
    print(f"LIVE CLIPMATE DATA ANALYSIS")
    print(f"Total clips: {len(clips)}")
    print("="*80)

    # Find the most recent clips (highest IDs)
    sorted_clips = sorted(clips, key=lambda x: x['native_id'], reverse=True)

    print("\nMOST RECENT 10 CLIPS:")
    print("-"*80)

    for i, clip in enumerate(sorted_clips[:10]):
        print(f"\n#{i+1} - ID: {clip['native_id']}")
        print(f"  Title: {clip['title'][:70]}")
        print(f"  Creator: {clip['creator'][:50]}")
        print(f"  Size: {clip['size']}")

        # Look for ANY reasonable timestamps in the record
        raw = clip['raw_data']

        # Check multiple date format possibilities
        date_candidates = []

        # Unix timestamp (Int32) - scan entire record
        for offset in range(0, min(len(raw)-3, 568), 4):
            try:
                val = struct.unpack('<I', raw[offset:offset+4])[0]
                # Recent dates (last 30 days to next 7 days)
                if 1733000000 < val < 1734500000:  # Dec 1 - Dec 18, 2025
                    dt = datetime.datetime.fromtimestamp(val)
                    date_candidates.append((offset, 'Unix', dt, val))
            except:
                pass

        # TDateTime (Double) - scan entire record
        for offset in range(0, min(len(raw)-7, 568), 4):
            try:
                val = struct.unpack('<d', raw[offset:offset+8])[0]
                if 45900 < val < 46000:  # Late 2025
                    base_date = datetime.datetime(1899, 12, 30)
                    dt = base_date + datetime.timedelta(days=val)
                    date_candidates.append((offset, 'TDateTime', dt, val))
            except:
                pass

        if date_candidates:
            print(f"  FOUND {len(date_candidates)} date candidate(s):")
            for offset, fmt, dt, val in date_candidates[:5]:
                print(f"    Offset {offset:3d} ({fmt:10s}): {dt} | Raw: {val}")
        else:
            print(f"  No dates found in expected range")

            # Show hex at key offsets for manual inspection
            print(f"  Raw data samples:")
            for offset in [4, 8, 151, 203, 422, 426, 430]:
                if len(raw) >= offset + 8:
                    hex_val = raw[offset:offset+8].hex()
                    print(f"    Offset {offset:3d}: {hex_val}")

    # Now look specifically at Graphic clips
    print("\n\n" + "="*80)
    print("GRAPHIC CLIPS (with dates in titles):")
    print("="*80)

    graphic_clips = [c for c in clips if 'Graphic:' in c['title']]

    for clip in graphic_clips[:5]:
        print(f"\nID: {clip['native_id']} | Title: {clip['title']}")

        # Try to extract expected date from title
        if 'Graphic:' in clip['title']:
            try:
                date_part = clip['title'].split('Graphic:')[1].strip()
                # Try different date formats
                for fmt in ['%m/%d/%Y %I:%M:%S %p', '%m/%d/%Y %H:%M:%S']:
                    try:
                        expected = datetime.datetime.strptime(date_part, fmt)
                        print(
                            f"  Expected timestamp: {expected} ({int(expected.timestamp())})")

                        # Search for this exact timestamp
                        raw = clip['raw_data']
                        target_ts = int(expected.timestamp())
                        target_bytes = struct.pack('<I', target_ts)

                        if target_bytes in raw:
                            offset = raw.index(target_bytes)
                            print(
                                f"  *** FOUND EXACT MATCH at offset {offset}! ***")
                        else:
                            # Try ±60 seconds
                            for delta in range(-60, 61):
                                test_ts = target_ts + delta
                                test_bytes = struct.pack('<I', test_ts)
                                if test_bytes in raw:
                                    offset = raw.index(test_bytes)
                                    dt = datetime.datetime.fromtimestamp(
                                        test_ts)
                                    print(
                                        f"  *** FOUND CLOSE MATCH at offset {offset} ({delta}s diff): {dt} ***")
                                    break
                        break
                    except:
                        continue
            except:
                pass

        # Scan for any reasonable timestamp
        raw = clip['raw_data']
        print(f"  Scanning all offsets for recent dates...")

        recent_dates = []
        for offset in range(len(raw) - 3):
            try:
                val = struct.unpack('<I', raw[offset:offset+4])[0]
                if 1733000000 < val < 1734500000:
                    dt = datetime.datetime.fromtimestamp(val)
                    recent_dates.append((offset, dt, val))
            except:
                pass

        if recent_dates:
            print(f"  Found {len(recent_dates)} timestamps in Dec 2025 range:")
            for offset, dt, val in recent_dates[:10]:
                print(f"    Offset {offset:3d}: {dt}")


if __name__ == "__main__":
    analyze_live_clips()
