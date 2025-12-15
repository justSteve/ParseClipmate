"""
Deep analysis of date field locations across different record types.
Focus on records with actual content vs demo records.
"""
import struct
import datetime
from clipmate_parser import ClipmateParser


def analyze_record_extensively(record, record_idx):
    """Analyze all potential date fields in a single record"""
    raw = record['raw_data']
    native_id = record['native_id']
    title = record['title'][:50]

    print(f"\n{'='*80}")
    print(f"Record #{record_idx} | ID: {native_id} | Title: {title}")
    print('='*80)

    # Known date field locations to check
    check_offsets = [
        (151, 'Int32', 'Old location from debug output'),
        (203, 'Int32', 'Found in newer records'),
        (4, 'Int32', 'Near ID field'),
        (8, 'Int32', 'After ID'),
        (422, 'Int32', 'Near size field'),
        (426, 'Int32', 'After size field'),
        (500, 'Int32', 'Late in record'),
        (550, 'Int32', 'Near end of record'),
    ]

    valid_finds = []

    for offset, data_type, description in check_offsets:
        if len(raw) < offset + 4:
            continue

        try:
            val = struct.unpack('<I', raw[offset:offset+4])[0]

            # Check if it's a valid Unix timestamp (2020-2030)
            if 1577836800 < val < 1893456000:
                dt = datetime.datetime.fromtimestamp(val)
                valid_finds.append((offset, val, dt, description))
                print(
                    f"  [+] Offset {offset:3d}: {val} -> {dt} ({description})")
        except:
            pass

    if not valid_finds:
        print("  [-] No valid date fields found")

        # Show some raw values at key offsets for manual inspection
        print("\n  Raw values at key offsets:")
        for offset, _, desc in check_offsets[:5]:
            if len(raw) >= offset + 4:
                val = struct.unpack('<I', raw[offset:offset+4])[0]
                print(
                    f"    Offset {offset:3d}: {val:10d} (0x{val:08X}) - {desc}")

    return valid_finds


def main():
    # Use latest archive
    archive = 'archives/ClipMate7_DB_My Clips_2025-09-30_2137'

    parser = ClipmateParser(archive)
    clips = parser.parse_clips()

    print(f"\n{'#'*80}")
    print(f"# DEEP DATE FIELD ANALYSIS")
    print(f"# Archive: {archive}")
    print(f"# Total clips: {len(clips)}")
    print(f"{'#'*80}")

    # Analyze different types of records
    print("\n\n[1] DEMO RECORDS (IDs 2-5):")
    print("-" * 80)
    for i, clip in enumerate(clips):
        if clip['native_id'] in [2, 3, 4, 5]:
            analyze_record_extensively(clip, i)

    print("\n\n[2] RECENT RECORDS (Highest IDs):")
    print("-" * 80)
    # Get records sorted by ID
    sorted_clips = sorted(clips, key=lambda x: x['native_id'], reverse=True)
    for clip in sorted_clips[:5]:
        idx = clips.index(clip)
        analyze_record_extensively(clip, idx)

    print("\n\n[3] GRAPHIC RECORDS (with date in title):")
    print("-" * 80)
    graphic_clips = [c for c in clips if c['title'].startswith('Graphic:')]
    for clip in graphic_clips[:3]:
        idx = clips.index(clip)
        results = analyze_record_extensively(clip, idx)

        # Extract expected date from title for comparison
        if clip['title'].startswith('Graphic:'):
            try:
                date_str = clip['title'].split('Graphic:')[1].strip()
                expected_dt = datetime.datetime.strptime(
                    date_str, '%m/%d/%Y %I:%M:%S %p')
                print(f"\n  Expected date from title: {expected_dt}")

                if results:
                    for offset, val, dt, desc in results:
                        diff = abs((dt - expected_dt).total_seconds())
                        if diff < 3600:  # Within 1 hour
                            print(
                                f"  [MATCH] Offset {offset} is within {diff:.0f} seconds")
            except:
                pass

    print("\n\n[4] RANDOM SAMPLE:")
    print("-" * 80)
    import random
    sample = random.sample([c for c in clips if c['native_id'] > 1000], min(
        5, len([c for c in clips if c['native_id'] > 1000])))
    for clip in sample:
        idx = clips.index(clip)
        analyze_record_extensively(clip, idx)


if __name__ == "__main__":
    main()
