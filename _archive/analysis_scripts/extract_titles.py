#!/usr/bin/env python3
"""
Extract titles for our test records to see if timestamps are embedded.
We found that graphic clips have "Graphic:12/14/2025 HH:MM:SS" in their titles.
"""
import struct
import re
from datetime import datetime

# Known test records
TEST_RECORDS = [
    (6021, "12/14/2025 11:25:30 AM"),
    (6020, "12/14/2025 10:38:25 AM"),
    (6019, "12/14/2025 10:38:01 AM"),
    (6018, "12/14/2025 9:35:03 AM"),
    (6017, "12/14/2025 8:58:00 AM"),
    (6016, "12/13/2025 4:06:46 PM"),
    (6001, "12/13/2025 6:04:04 AM"),
]

def extract_title_from_record(data, record_pos):
    """Extract title from a 568-byte record in CLIP.dat"""
    record = data[record_pos:record_pos + 568]

    # Title is at offset +10, null-terminated string
    title_start = 10
    title_bytes = bytearray()

    for i in range(title_start, min(title_start + 400, len(record))):
        if record[i] == 0:
            break
        title_bytes.append(record[i])

    try:
        title = title_bytes.decode('latin-1', errors='ignore')
        return title
    except:
        return "(could not decode)"

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        data = f.read()

    print("="*100)
    print("EXTRACTING TITLES FROM TEST RECORDS")
    print("="*100 + "\n")

    for record_id, expected_timestamp in TEST_RECORDS:
        id_bytes = struct.pack('<I', record_id)
        pos = data.find(id_bytes)

        if pos == -1:
            print(f"Record {record_id}: NOT FOUND")
            continue

        # Determine record start (ID is not necessarily at offset 0)
        # From previous analysis, we know ID can be at different positions
        # Let's check around the found position for the actual record start
        possible_starts = []

        # Try assuming ID is at offset 0 (Layout B)
        if pos % 568 == 0:
            possible_starts.append(pos)

        # Try assuming 568-byte record boundaries
        record_num = pos // 568
        possible_starts.append(record_num * 568)

        # Try nearby 568-byte boundaries
        for offset in range(max(0, pos - 568), pos + 10, 568):
            if offset not in possible_starts:
                possible_starts.append(offset)

        print(f"\nRecord {record_id} - Expected: {expected_timestamp}")
        print(f"  ID found at offset: {pos}")

        best_title = None
        best_score = -1

        for start in possible_starts[:3]:  # Check top 3 possibilities
            title = extract_title_from_record(data, start)

            # Score the title (printable chars = good)
            score = sum(1 for c in title if 32 <= ord(c) < 127)

            if score > best_score:
                best_score = score
                best_title = title

        # Clean title for printing
        clean_title = ''.join(c if 32 <= ord(c) < 127 else '.' for c in best_title)
        print(f"  Title: \"{clean_title}\"")

        # Check if title contains a timestamp
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M'
        match = re.search(date_pattern, best_title)

        if match:
            found_timestamp = match.group()
            print(f"  *** TIMESTAMP IN TITLE: {found_timestamp} ***")

            # Parse and compare
            try:
                title_dt = datetime.strptime(found_timestamp, "%m/%d/%Y %I:%M:%S %p")
                expected_dt = datetime.strptime(expected_timestamp, "%m/%d/%Y %I:%M:%S %p")
                diff = abs((title_dt - expected_dt).total_seconds())
                print(f"  Difference from expected: {diff:.0f} seconds")

                if diff < 5:
                    print(f"  *** EXACT MATCH! ***")
            except:
                pass

if __name__ == '__main__':
    main()
