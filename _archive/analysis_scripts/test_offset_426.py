"""
Decode the consistent byte pattern found at offset 426-434
"""
from clipmate_parser import ClipmateParser
import struct
import datetime

# The hex pattern we see: 700e0fcd42
# Let's try it as part of an 8-byte double at different alignments

hex_patterns = [
    "fa700e0fcd420100",  # From offset 426
    "700e0fcd42010000",  # From offset 427
]

print("Testing byte patterns as TDateTime (double):")
print("="*70)

for pattern in hex_patterns:
    bytes_data = bytes.fromhex(pattern)

    try:
        # Little-endian double
        val = struct.unpack('<d', bytes_data)[0]
        print(f"\nPattern: {pattern}")
        print(f"As double: {val}")

        # Try as TDateTime (days since 1899-12-30)
        if 40000 < val < 50000:  # Reasonable range for 2010-2035
            base_date = datetime.datetime(1899, 12, 30)
            result_date = base_date + datetime.timedelta(days=val)
            print(f"As TDateTime: {result_date}")

    except Exception as e:
        print(f"Error: {e}")

# Now check actual live data
print("\n\n" + "="*70)
print("Checking actual LIVE data at offset 426:")
print("="*70)


live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

# Get most recent clips
recent = sorted(clips, key=lambda x: x['native_id'], reverse=True)[:10]

for clip in recent:
    raw = clip['raw_data']

    # Try offset 426 as TDateTime
    if len(raw) >= 434:
        bytes_data = raw[426:434]
        try:
            val = struct.unpack('<d', bytes_data)[0]

            if 40000 < val < 50000:
                base_date = datetime.datetime(1899, 12, 30)
                result_date = base_date + datetime.timedelta(days=val)

                print(f"\nID {clip['native_id']:4d}: {clip['title'][:50]}")
                print(f"  Offset 426: {result_date}")
                print(f"  Raw: {bytes_data.hex()}")
        except:
            pass

print("\n\n" + "="*70)
print("TESTING GRAPHIC CLIPS - Compare with title dates:")
print("="*70)

graphic_clips = [c for c in clips if 'Graphic:' in c['title']][:5]

for clip in graphic_clips:
    # Extract expected date from title
    try:
        date_str = clip['title'].split('Graphic:')[1].strip()
        expected = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')

        # Parse from offset 426
        raw = clip['raw_data']
        if len(raw) >= 434:
            val = struct.unpack('<d', raw[426:434])[0]
            if 40000 < val < 50000:
                parsed = datetime.datetime(
                    1899, 12, 30) + datetime.timedelta(days=val)

                diff_seconds = abs((parsed - expected).total_seconds())

                print(f"\nID {clip['native_id']}: {clip['title'][:50]}")
                print(f"  Expected:  {expected}")
                print(f"  Parsed:    {parsed}")
                print(f"  Diff:      {diff_seconds:.0f} seconds")

                if diff_seconds < 60:
                    print(f"  *** EXCELLENT MATCH! ***")
                elif diff_seconds < 3600:
                    print(f"  *** GOOD MATCH (within 1 hour) ***")
    except:
        pass
