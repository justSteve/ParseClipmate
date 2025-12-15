import struct
import datetime
from clipmate_parser import ClipmateParser

live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

graphic_clips = [c for c in clips if 'Graphic:' in c['title']][:10]

print("COMPARING OFFSET 426 (TDateTime) WITH GRAPHIC TITLE DATES:")
print("="*80)

for clip in graphic_clips:
    try:
        date_str = clip['title'].split('Graphic:')[1].strip()
        expected = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')

        raw = clip['raw_data']

        # Show hex at offset 426
        print(f"\nID {clip['native_id']:4d}: {clip['title'][:45]}")
        print(f"  Hex at 426-434: {raw[426:434].hex()}")

        val = struct.unpack('<d', raw[426:434])[0]
        print(f"  Double value: {val}")

        # Only parse if in reasonable range
        if 40000 < val < 50000:
            parsed = datetime.datetime(
                1899, 12, 30) + datetime.timedelta(days=val)

            diff_seconds = abs((parsed - expected).total_seconds())

            print(f"  Expected:  {expected}")
            print(f"  Parsed:    {parsed}")
            print(f"  Diff:      {diff_seconds:.1f} seconds")

            if diff_seconds < 5:
                print(f"  *** PERFECT MATCH! ***")
        else:
            print(f"  Value out of range for TDateTime")
    except Exception as e:
        print(f"  Error: {e}")
