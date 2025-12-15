"""
Comprehensive scan of LIVE graphic clip to find the date field.
We know the exact expected date, so scan EVERY offset for it.
"""
import struct
import datetime
from clipmate_parser import ClipmateParser

live_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
parser = ClipmateParser(live_dir)
clips = parser.parse_clips()

# Get ONE graphic clip with known date
test_clip = None
for clip in clips:
    if 'Graphic:12/7/2025 7:58:32 PM' in clip['title']:
        test_clip = clip
        break

if not test_clip:
    # Try first graphic clip
    test_clip = [c for c in clips if 'Graphic:' in c['title']][0]

print("="*80)
print(f"COMPREHENSIVE SCAN OF CLIP ID {test_clip['native_id']}")
print(f"Title: {test_clip['title']}")
print("="*80)

# Extract expected date
date_str = test_clip['title'].split('Graphic:')[1].strip()
expected = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
expected_unix = int(expected.timestamp())

print(f"\nExpected date: {expected}")
print(f"Expected Unix timestamp: {expected_unix}")

# Calculate TDateTime value
delta = expected - datetime.datetime(1899, 12, 30)
expected_tdatetime = delta.days + (delta.seconds / 86400.0)
print(f"Expected TDateTime: {expected_tdatetime}")

raw = test_clip['raw_data']
print(f"\nRecord size: {len(raw)} bytes")

print("\n" + "="*80)
print("SCANNING FOR UNIX TIMESTAMP (Int32)")
print("="*80)

for offset in range(len(raw) - 3):
    val = struct.unpack('<I', raw[offset:offset+4])[0]

    # Check if close to expected (within 1 hour)
    if abs(val - expected_unix) < 3600:
        print(
            f"Offset {offset:3d}: {val} -> {datetime.datetime.fromtimestamp(val)}")
        print(f"  Hex: {raw[offset:offset+4].hex()}")
        print(f"  Diff: {abs(val - expected_unix)} seconds")

print("\n" + "="*80)
print("SCANNING FOR TDateTime (Double)")
print("="*80)

for offset in range(len(raw) - 7):
    try:
        val = struct.unpack('<d', raw[offset:offset+8])[0]

        # Check if in reasonable range and close to expected
        if 45900 < val < 46100:  # Dec 2025 range
            dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=val)
            diff = abs((dt - expected).total_seconds())

            if diff < 86400:  # Within 24 hours
                print(f"Offset {offset:3d}: {val:.6f} -> {dt}")
                print(f"  Hex: {raw[offset:offset+8].hex()}")
                print(f"  Diff: {diff:.0f} seconds")
    except:
        pass

print("\n" + "="*80)
print("HEX DUMP OF KEY AREAS")
print("="*80)

areas = [
    ("Start (0-20)", 0, 20),
    ("After ID (8-24)", 8, 24),
    ("Around 150", 145, 165),
    ("Around 200", 195, 215),
    ("Around 420-450", 415, 455),
    ("End (548-568)", 548, 568),
]

for label, start, end in areas:
    if end <= len(raw):
        hex_str = raw[start:end].hex()
        print(f"\n{label}:")
        # Print in 16-byte rows
        for i in range(0, len(hex_str), 32):
            offset_label = start + i//2
            print(f"  {offset_label:3d}: {hex_str[i:i+32]}")
