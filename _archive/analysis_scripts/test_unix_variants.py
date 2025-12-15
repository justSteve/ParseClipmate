"""
Try interpreting the varying bytes around offset 430 as Unix timestamps.
Looking at patterns like 4a090fcd, 700e0fcd, dd0b0fcd
"""
import struct
import datetime
from clipmate_parser import ClipmateParser

live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

# Get text-only clips
text_clips = [
    c for c in clips
    if 'Graphic:' not in c['title']
    and c['size'] < 10240
    and c['native_id'] > 5900
][:15]

print("="*80)
print("TESTING VARIOUS INTERPRETATIONS AROUND OFFSET 428-436")
print("="*80)

for clip in text_clips:
    raw = clip['raw_data']

    print(f"\nID {clip['native_id']:4d}: {clip['title'][:50]}")
    print(f"  Creator: {clip['creator'][:30]}")

    # Show hex context
    if len(raw) >= 440:
        print(f"  Hex 425-440: {raw[425:440].hex()}")

    # Try different 4-byte interpretations as Unix timestamp
    for offset in [428, 429, 430, 431, 432]:
        if len(raw) >= offset + 4:
            # Little-endian Int32
            val_le = struct.unpack('<I', raw[offset:offset+4])[0]

            # Check if it's a reasonable Unix timestamp (2020-2030)
            if 1577836800 < val_le < 1893456000:
                try:
                    dt = datetime.datetime.fromtimestamp(val_le)
                    print(f"  Offset {offset} (LE Int32): {val_le} -> {dt}")
                except:
                    pass

            # Big-endian Int32
            val_be = struct.unpack('>I', raw[offset:offset+4])[0]
            if 1577836800 < val_be < 1893456000:
                try:
                    dt = datetime.datetime.fromtimestamp(val_be)
                    print(f"  Offset {offset} (BE Int32): {val_be} -> {dt}")
                except:
                    pass

print("\n" + "="*80)
print("CHECKING IF BYTES ARE REVERSED/SWAPPED")
print("="*80)

for clip in text_clips[:5]:
    raw = clip['raw_data']
    print(f"\nID {clip['native_id']}: {clip['title'][:40]}")

    # Extract the varying 4 bytes (looks like 4a090fcd, 700e0fcd, dd0b0fcd pattern)
    if len(raw) >= 434:
        bytes_430_434 = raw[430:434]
        print(f"  Bytes at 430-434: {bytes_430_434.hex()}")

        # Try various byte orderings
        b0, b1, b2, b3 = bytes_430_434

        # Original order
        val1 = struct.unpack('<I', bytes([b0, b1, b2, b3]))[0]
        print(f"    As-is (LE): {val1}")

        # Reverse bytes
        val2 = struct.unpack('>I', bytes([b0, b1, b2, b3]))[0]
        if 1577836800 < val2 < 1893456000:
            dt = datetime.datetime.fromtimestamp(val2)
            print(f"    Reversed (BE): {val2} -> {dt} *** POSSIBLE MATCH ***")

        # Swap pairs
        val3 = struct.unpack('<I', bytes([b2, b3, b0, b1]))[0]
        if 1577836800 < val3 < 1893456000:
            dt = datetime.datetime.fromtimestamp(val3)
            print(f"    Swapped pairs: {val3} -> {dt} *** POSSIBLE MATCH ***")
