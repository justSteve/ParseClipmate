"""
Focus on TEXT-ONLY clips (non-graphic, non-binary) to find the date field.
These should have timestamps stored in a standard format.
"""
import struct
import datetime
from clipmate_parser import ClipmateParser

live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

# Filter for text-only clips:
# - No "Graphic:" in title
# - Small size (< 10KB = 10240 bytes, likely text)
# - Recent (high ID numbers)
text_clips = [
    c for c in clips
    if 'Graphic:' not in c['title']
    and c['size'] < 10240
    and c['native_id'] > 5900
]

print("="*80)
print(f"ANALYZING {len(text_clips)} TEXT-ONLY CLIPS")
print("="*80)

# Test different offset ranges for TDateTime
test_offsets = list(range(428, 445, 2))  # Test even offsets from 428-444

print("\nScanning all offsets for TDateTime patterns...")
print("-"*80)

offset_hits = {}

for clip in text_clips[:20]:  # Test first 20 text clips
    raw = clip['raw_data']

    for offset in test_offsets:
        if len(raw) < offset + 8:
            continue

        try:
            val = struct.unpack('<d', raw[offset:offset+8])[0]

            # Check for December 2025 range
            if 45995 < val < 46005:  # Dec 2025 (around day 46000)
                dt = datetime.datetime(1899, 12, 30) + \
                    datetime.timedelta(days=val)

                # Track which offsets work
                if offset not in offset_hits:
                    offset_hits[offset] = []
                offset_hits[offset].append((clip['native_id'], dt, val))
        except:
            pass

print(f"\nResults: Found date patterns at {len(offset_hits)} offset(s)")
print("="*80)

for offset in sorted(offset_hits.keys()):
    print(f"\nOffset {offset}: {len(offset_hits[offset])} matches")
    for clip_id, dt, val in offset_hits[offset][:5]:
        print(f"  ID {clip_id}: {dt} (TDateTime: {val:.6f})")

# Now show detailed info for the most promising offset
if offset_hits:
    best_offset = max(offset_hits.keys(), key=lambda k: len(offset_hits[k]))

    print("\n" + "="*80)
    print(f"DETAILED ANALYSIS OF OFFSET {best_offset} (most matches)")
    print("="*80)

    for clip in text_clips[:10]:
        raw = clip['raw_data']

        if len(raw) >= best_offset + 8:
            try:
                val = struct.unpack('<d', raw[best_offset:best_offset+8])[0]

                if 45990 < val < 46010:  # Extended range for December 2025
                    dt = datetime.datetime(
                        1899, 12, 30) + datetime.timedelta(days=val)

                    print(f"\nID {clip['native_id']:4d}: {clip['title'][:50]}")
                    print(f"  Creator: {clip['creator'][:30]}")
                    print(f"  Date: {dt}")
                    print(f"  Hex: {raw[best_offset:best_offset+8].hex()}")
            except:
                pass

    print("\n" + "="*80)
    print(
        f"*** RECOMMENDATION: Use offset {best_offset} for date field (TDateTime) ***")
    print("="*80)
else:
    print("\n*** NO CONSISTENT DATE PATTERN FOUND ***")
    print("Showing raw data from sample clips for manual inspection:")

    for clip in text_clips[:3]:
        raw = clip['raw_data']
        print(f"\nID {clip['native_id']}: {clip['title'][:50]}")
        print(f"  Creator: {clip['creator']}")

        # Show hex at various offsets
        for offset in [420, 425, 430, 435, 440, 445, 450]:
            if len(raw) >= offset + 8:
                print(f"  Offset {offset}: {raw[offset:offset+8].hex()}")
