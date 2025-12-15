"""
Decode the varying byte patterns at offset 430 as TDateTime.
"""
import struct
import datetime
from clipmate_parser import ClipmateParser

live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

# Get recent clips sorted by ID
recent = sorted(clips, key=lambda x: x['native_id'], reverse=True)[:20]

print("="*80)
print("TESTING OFFSET 430-438 AS TDateTime")
print("="*80)

for clip in recent:
    raw = clip['raw_data']

    if len(raw) >= 438:
        # Extract 8 bytes starting at 430
        bytes_data = raw[430:438]
        hex_str = bytes_data.hex()

        try:
            val = struct.unpack('<d', bytes_data)[0]

            # Check if in reasonable range for 2025
            if 45900 < val < 46050:
                dt = datetime.datetime(1899, 12, 30) + \
                    datetime.timedelta(days=val)

                print(f"\nID {clip['native_id']:4d}: {clip['title'][:45]}")
                print(f"  Creator: {clip['creator'][:30]}")
                print(f"  Hex at 430: {hex_str}")
                print(f"  TDateTime: {val:.8f}")
                print(f"  Parsed date: {dt}")
        except:
            pass

print("\n\n" + "="*80)
print("VERIFYING WITH GRAPHIC CLIPS (compare with title date)")
print("="*80)

graphic_clips = [c for c in clips if 'Graphic:' in c['title']][:5]

for clip in graphic_clips:
    try:
        date_str = clip['title'].split('Graphic:')[1].strip()
        expected = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')

        raw = clip['raw_data']
        val = struct.unpack('<d', raw[430:438])[0]

        if 45900 < val < 46050:
            parsed = datetime.datetime(
                1899, 12, 30) + datetime.timedelta(days=val)
            diff_seconds = abs((parsed - expected).total_seconds())

            print(f"\nID {clip['native_id']}: {clip['title'][:50]}")
            print(f"  Expected:  {expected}")
            print(f"  Parsed:    {parsed}")
            print(f"  Diff:      {diff_seconds:.1f} seconds")

            if diff_seconds < 2:
                print(f"  *** PERFECT MATCH! ***")
            elif diff_seconds < 60:
                print(f"  *** VERY CLOSE! ***")
    except Exception as e:
        pass
