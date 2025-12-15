"""
Verify that offset 203 contains Unix timestamps for multiple records.
Test across all available archives to confirm the pattern.
"""
import struct
import datetime
from clipmate_parser import ClipmateParser


def test_offset_203(archive_dir):
    """Test if offset 203 contains valid Unix timestamps"""
    parser = ClipmateParser(archive_dir)
    clips = parser.parse_clips()

    print(f"\nTesting {archive_dir}")
    print("=" * 80)

    valid_dates = 0
    invalid_dates = 0
    tested = 0

    for clip in clips[:50]:  # Test first 50 records
        if len(clip['raw_data']) < 207:
            continue

        tested += 1
        raw = clip['raw_data']
        ts_val = struct.unpack('<I', raw[203:207])[0]

        # Check if it's a valid Unix timestamp (2020-2030)
        if 1577836800 < ts_val < 1893456000:
            try:
                dt = datetime.datetime.fromtimestamp(ts_val)
                valid_dates += 1

                if tested <= 10:  # Show first 10
                    print(
                        f"  ID {clip['native_id']:5d} | Offset 203: {ts_val} -> {dt}")
            except:
                invalid_dates += 1
        else:
            invalid_dates += 1
            if tested <= 3:  # Show first few failures
                print(
                    f"  ID {clip['native_id']:5d} | Offset 203: {ts_val} (INVALID)")

    print(
        f"\nResults: {valid_dates}/{tested} records have valid dates at offset 203")
    print(f"Success rate: {100*valid_dates/tested:.1f}%" if tested >
          0 else "No records tested")

    return valid_dates, invalid_dates, tested


# Test all archives
archives = [
    'exploration',
    'archives/ClipMate7_DB_My Clips_2025-09-02_1733',
    'archives/ClipMate7_DB_My Clips_2025-09-10_1632',
    'archives/ClipMate7_DB_My Clips_2025-09-15_0030',
    'archives/ClipMate7_DB_My Clips_2025-09-30_2137',
]

print("\n" + "="*80)
print("DATE FIELD VALIDATION TEST - Offset 203")
print("="*80)

total_valid = 0
total_invalid = 0
total_tested = 0

for archive in archives:
    try:
        valid, invalid, tested = test_offset_203(archive)
        total_valid += valid
        total_invalid += invalid
        total_tested += tested
    except Exception as e:
        print(f"\nError testing {archive}: {e}")

print("\n" + "="*80)
print("OVERALL SUMMARY")
print("="*80)
print(f"Total records tested: {total_tested}")
print(f"Valid dates found: {total_valid}")
print(f"Invalid/missing dates: {total_invalid}")
print(
    f"Overall success rate: {100*total_valid/total_tested:.1f}%" if total_tested > 0 else "No records")

if total_valid > total_tested * 0.5:
    print("\n✓ CONFIRMED: Offset 203 contains Unix timestamp date field!")
    print("  This offset should be used in the parser for date extraction.")
else:
    print("\n✗ Offset 203 does not reliably contain date information.")
    print("  Further investigation needed.")
