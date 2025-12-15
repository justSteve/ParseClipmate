"""
Focused analysis on Graphic records where we know the exact expected date.
We'll scan the entire record byte-by-byte looking for the expected date.
"""
import struct
import datetime
from clipmate_parser import ClipmateParser


def scan_for_exact_date(raw_data, target_date):
    """
    Scan all possible positions for the target date in various formats.
    Returns list of (offset, format_name, parsed_date) tuples
    """
    findings = []
    unix_ts = int(target_date.timestamp())

    # Scan every 4-byte position for Unix timestamp (allow ±5 minutes)
    for offset in range(len(raw_data) - 4):
        val = struct.unpack('<I', raw_data[offset:offset+4])[0]

        if abs(val - unix_ts) < 300:  # Within 5 minutes
            try:
                dt = datetime.datetime.fromtimestamp(val)
                diff_seconds = abs((dt - target_date).total_seconds())
                findings.append((offset, 'Unix LE', dt, diff_seconds))
            except:
                pass

    # Check big-endian too
    for offset in range(len(raw_data) - 4):
        val = struct.unpack('>I', raw_data[offset:offset+4])[0]

        if abs(val - unix_ts) < 300:
            try:
                dt = datetime.datetime.fromtimestamp(val)
                diff_seconds = abs((dt - target_date).total_seconds())
                findings.append((offset, 'Unix BE', dt, diff_seconds))
            except:
                pass

    return sorted(findings, key=lambda x: x[3])  # Sort by accuracy


def main():
    archive = 'archives/ClipMate7_DB_My Clips_2025-09-30_2137'

    parser = ClipmateParser(archive)
    clips = parser.parse_clips()

    # Find Graphic clips
    graphic_clips = [c for c in clips if c['title'].startswith('Graphic:')]

    print("="*80)
    print("SCANNING GRAPHIC RECORDS FOR EXACT DATE MATCHES")
    print("="*80)

    for clip in graphic_clips[:10]:  # Test first 10 graphic records
        try:
            date_str = clip['title'].split('Graphic:')[1].strip()
            expected_dt = datetime.datetime.strptime(
                date_str, '%m/%d/%Y %I:%M:%S %p')

            print(f"\nID: {clip['native_id']} | Title: {clip['title'][:60]}")
            print(f"Expected: {expected_dt}")

            findings = scan_for_exact_date(clip['raw_data'], expected_dt)

            if findings:
                print(f"Found {len(findings)} potential matches:")
                for offset, format_name, dt, diff in findings[:5]:
                    print(
                        f"  Offset {offset:3d} ({format_name:10s}): {dt} (diff: {diff:.0f}s)")

                    # Show hex context
                    start = max(0, offset-4)
                    end = min(len(clip['raw_data']), offset+8)
                    hex_context = clip['raw_data'][start:end].hex()
                    print(f"    Hex context: {hex_context}")
            else:
                print("  NO MATCHES FOUND")
                print(
                    f"  Unix timestamp expected: {int(expected_dt.timestamp())}")

                # Show hex dump of interesting sections
                print(f"\n  Hex dump of key areas:")
                for label, start, end in [
                    ("Start", 0, 20),
                    ("150-170", 150, 170),
                    ("200-220", 200, 220),
                    ("420-440", 420, 440),
                ]:
                    if end <= len(clip['raw_data']):
                        print(
                            f"    {label:12s}: {clip['raw_data'][start:end].hex()}")

        except Exception as e:
            print(f"Error processing {clip['native_id']}: {e}")


if __name__ == "__main__":
    main()
