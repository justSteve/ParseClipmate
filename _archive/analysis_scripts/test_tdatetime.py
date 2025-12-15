"""
Test TDateTime (Delphi double) format at specific offsets in Graphic records.
TDateTime = days since 1899-12-30 as a double.
"""
import struct
import datetime
from clipmate_parser import ClipmateParser


def parse_tdatetime(bytes_data):
    """Parse TDateTime from 8 bytes (little-endian double)"""
    try:
        days = struct.unpack('<d', bytes_data)[0]
        base_date = datetime.datetime(1899, 12, 30)
        result_date = base_date + datetime.timedelta(days=days)
        return result_date
    except:
        return None


def main():
    archive = 'archives/ClipMate7_DB_My Clips_2025-09-30_2137'

    parser = ClipmateParser(archive)
    clips = parser.parse_clips()

    graphic_clips = [c for c in clips if c['title'].startswith('Graphic:')]

    print("="*80)
    print("TESTING TDateTime AT VARIOUS OFFSETS")
    print("="*80)

    # Test offsets around 430-440
    test_offsets = [426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436]

    for clip in graphic_clips[:5]:
        try:
            date_str = clip['title'].split('Graphic:')[1].strip()
            expected_dt = datetime.datetime.strptime(
                date_str, '%m/%d/%Y %I:%M:%S %p')

            print(f"\nID: {clip['native_id']} | Expected: {expected_dt}")

            raw = clip['raw_data']

            best_match = None
            best_diff = float('inf')

            for offset in test_offsets:
                if len(raw) < offset + 8:
                    continue

                parsed_dt = parse_tdatetime(raw[offset:offset+8])

                if parsed_dt and datetime.datetime(2020, 1, 1) < parsed_dt < datetime.datetime(2030, 1, 1):
                    diff = abs((parsed_dt - expected_dt).total_seconds())

                    if diff < best_diff:
                        best_diff = diff
                        best_match = (offset, parsed_dt)

                    if diff < 86400:  # Show if within 24 hours
                        print(
                            f"  Offset {offset}: {parsed_dt} (diff: {diff:.0f}s)")

            if best_match:
                offset, dt = best_match
                print(
                    f"  >>> BEST: Offset {offset} -> {dt} (diff: {best_diff:.0f}s)")

                # Show hex
                hex_str = raw[offset:offset+8].hex()
                print(f"  >>> Hex: {hex_str}")

        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "="*80)
    print("COMPREHENSIVE TEST ON ALL GRAPHIC RECORDS")
    print("="*80)

    # Test all graphic records to find the consistent offset
    offset_votes = {}

    for clip in graphic_clips:
        try:
            date_str = clip['title'].split('Graphic:')[1].strip()
            expected_dt = datetime.datetime.strptime(
                date_str, '%m/%d/%Y %I:%M:%S %p')

            raw = clip['raw_data']

            for offset in test_offsets:
                if len(raw) < offset + 8:
                    continue

                parsed_dt = parse_tdatetime(raw[offset:offset+8])

                if parsed_dt and datetime.datetime(2020, 1, 1) < parsed_dt < datetime.datetime(2030, 1, 1):
                    diff = abs((parsed_dt - expected_dt).total_seconds())

                    if diff < 300:  # Within 5 minutes
                        if offset not in offset_votes:
                            offset_votes[offset] = 0
                        offset_votes[offset] += 1
        except:
            pass

    print("\nOffset voting results (within 5 minutes of expected):")
    for offset, count in sorted(offset_votes.items(), key=lambda x: x[1], reverse=True):
        print(f"  Offset {offset}: {count} matches")

    if offset_votes:
        best_offset = max(offset_votes.items(), key=lambda x: x[1])[0]
        print(
            f"\n*** RECOMMENDED DATE FIELD OFFSET: {best_offset} (TDateTime format) ***")


if __name__ == "__main__":
    main()
