import struct
import datetime
from clipmate_parser import ClipmateParser

live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

# Text clips only
text_clips = [c for c in clips if 'Graphic:' not in c['title']
              and c['size'] < 10240 and c['native_id'] > 5900][:10]

print("Testing offset 432 as TDateTime:")
print("="*70)

for clip in text_clips:
    raw = clip['raw_data']

    if len(raw) >= 440:
        val = struct.unpack('<d', raw[432:440])[0]

        print(f"\nID {clip['native_id']:4d}: {clip['title'][:45]}")
        print(f"  TDateTime value: {val:.8f}")

        if 45990 < val < 46010:
            dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=val)
            print(f"  Parsed date: {dt}")
            print(f"  *** VALID DATE IN DEC 2025 RANGE! ***")
        else:
            print(f"  Out of range for Dec 2025")
