#!/usr/bin/env python3
"""
Check if GUIDs contain embedded timestamps (UUID version 1)
"""
import uuid
from datetime import datetime, timezone
import os
from clipmate_parser import ClipmateParser

def uuid_to_datetime(guid_str):
    """Extract timestamp from UUID v1 if present"""
    try:
        u = uuid.UUID(guid_str)
        if u.version == 1:
            # UUID v1 contains timestamp
            timestamp = u.time
            # UUID timestamp is 100-nanosecond intervals since Oct 15, 1582
            # Convert to Unix timestamp
            unix_time = (timestamp - 0x01b21dd213814000) / 10000000
            return datetime.fromtimestamp(unix_time)
        return None
    except:
        return None

def main():
    data_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"
    parser = ClipmateParser(data_dir)

    print("Parsing CLIP.dat...")
    records = parser.parse_clips()

    # Check first 20 records
    print(f"\nChecking GUIDs for embedded timestamps:\n")

    for i, record in enumerate(records[:50]):
        guid = record.get('guid', '')
        record_id = record.get('id', 'Unknown')
        title = record.get('title', 'No title')[:50]

        if guid:
            dt = uuid_to_datetime(guid)
            if dt:
                print(f"Record {record_id}: {guid}")
                print(f"  Title: {title}")
                print(f"  UUID Timestamp: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
                print()

    # Now check records from our screenshot
    target_ids = {5969, 5968, 5967, 5966, 5965, 5964, 5963, 5962, 5961, 5960, 5959}
    target_records = [r for r in records if r.get('id') in target_ids]

    if target_records:
        print(f"\n=== Records from Screenshot ===\n")
        for record in target_records:
            guid = record.get('guid', '')
            record_id = record.get('id', 'Unknown')
            title = record.get('title', 'No title')[:50]

            print(f"Record {record_id}: {guid}")
            print(f"  Title: {title}")

            dt = uuid_to_datetime(guid)
            if dt:
                print(f"  UUID Timestamp: {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
            else:
                print(f"  UUID is not v1 (version: {uuid.UUID(guid).version if guid else 'N/A'})")
            print()
    else:
        print(f"\nTarget records not found in CLIP.dat")

if __name__ == '__main__':
    main()
