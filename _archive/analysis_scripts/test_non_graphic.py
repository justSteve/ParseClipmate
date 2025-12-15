"""
Test NON-graphic clips to see if they have date fields.
Maybe graphic clips don't store dates separately since they're in the title?
"""
import struct
import datetime
from clipmate_parser import ClipmateParser

live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

# Get recent NON-graphic clips
non_graphic = [c for c in clips if 'Graphic:' not in c['title']
               and c['native_id'] > 5900][:10]

print("="*80)
print("SCANNING NON-GRAPHIC CLIPS FOR DATE FIELDS")
print("="*80)

for clip in non_graphic:
    print(f"\nID {clip['native_id']:4d}: {clip['title'][:50]}")
    print(f"  Creator: {clip['creator']}")

    raw = clip['raw_data']

    # Scan for Unix timestamps from Dec 1-11, 2025
    found_dates = []
    for offset in range(len(raw) - 3):
        val = struct.unpack('<I', raw[offset:offset+4])[0]

        if 1733000000 < val < 1734000000:  # Dec 1-11, 2025
            dt = datetime.datetime.fromtimestamp(val)
            found_dates.append((offset, dt, val))

    if found_dates:
        print(f"  Found {len(found_dates)} date(s):")
        for offset, dt, val in found_dates[:3]:
            print(f"    Offset {offset:3d}: {dt} ({val})")
            print(f"      Hex: {raw[offset:offset+4].hex()}")
    else:
        print(f"  No dates found")
        # Show hex at common offsets
        for off in [426, 430, 434]:
            if len(raw) >= off + 8:
                print(f"    Offset {off}: {raw[off:off+8].hex()}")
