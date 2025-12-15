#!/usr/bin/env python3
"""
Find the records visible in the screenshot and dump their raw binary data
to look for the timestamp that ClipMate displays
"""
import struct
from datetime import datetime
from clipmate_parser import ClipmateParser

# Records visible in screenshot with their displayed timestamps
SCREENSHOT_RECORDS = {
    5969: "12/11/2025 11:14:28 AM",
    5968: "12/11/2025 9:41:47 AM",
    5967: "12/11/2025 9:40:33 AM",
    5966: "12/11/2025 9:40:20 AM",
    5965: "12/11/2025 9:39:46 AM",
    5964: "12/11/2025 9:39:13 AM",
    5963: "12/11/2025 9:38:32 AM",
    5962: "12/11/2025 9:36:07 AM",
    5961: "12/11/2025 9:35:01 AM",
    5960: "12/11/2025 9:34:14 AM",
    5959: "12/11/2025 9:33:38 AM",
}

def datetime_to_delphi(dt_str):
    """Convert datetime string to Delphi TDateTime (days since 1899-12-30)"""
    dt = datetime.strptime(dt_str, "%m/%d/%Y %I:%M:%S %p")
    epoch = datetime(1899, 12, 30)
    delta = dt - epoch
    return delta.total_seconds() / 86400.0

def datetime_to_unix(dt_str):
    """Convert datetime string to Unix timestamp"""
    dt = datetime.strptime(dt_str, "%m/%d/%Y %I:%M:%S %p")
    return int(dt.timestamp())

def main():
    data_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"
    parser = ClipmateParser(data_dir)

    print("Parsing CLIP.dat...")
    records = parser.parse_clips()

    print(f"\nFound {len(records)} total records")
    print("\n" + "="*80)

    for record_id, expected_datetime in SCREENSHOT_RECORDS.items():
        print(f"\n=== Record ID {record_id} ===")
        print(f"Expected DateTime: {expected_datetime}")

        # Convert to various formats for searching
        delphi_datetime = datetime_to_delphi(expected_datetime)
        unix_timestamp = datetime_to_unix(expected_datetime)

        print(f"Delphi TDateTime: {delphi_datetime:.10f}")
        print(f"Unix Timestamp: {unix_timestamp}")
        print(f"Delphi as double bytes: {struct.pack('<d', delphi_datetime).hex()}")
        print(f"Unix as 4-byte int: {struct.pack('<I', unix_timestamp).hex()}")
        print(f"Unix as 8-byte int: {struct.pack('<Q', unix_timestamp).hex()}")

        # Find the record
        found_record = None
        for rec in records:
            if rec.get('id') == record_id:
                found_record = rec
                break

        if found_record:
            print(f"\nRecord found!")
            print(f"Title: {found_record.get('title', 'N/A')[:60]}")

            raw_data = found_record.get('raw_data', b'')
            if raw_data:
                print(f"\nRaw data length: {len(raw_data)} bytes")

                # Search for the Delphi TDateTime value in the raw data
                delphi_bytes = struct.pack('<d', delphi_datetime)
                if delphi_bytes in raw_data:
                    offset = raw_data.index(delphi_bytes)
                    print(f"\n*** FOUND Delphi TDateTime at offset {offset} ***")

                # Search for Unix timestamp (4-byte)
                unix_bytes = struct.pack('<I', unix_timestamp)
                if unix_bytes in raw_data:
                    offset = raw_data.index(unix_bytes)
                    print(f"\n*** FOUND Unix timestamp (4-byte) at offset {offset} ***")

                # Search for Unix timestamp (8-byte)
                unix_bytes_8 = struct.pack('<Q', unix_timestamp)
                if unix_bytes_8 in raw_data:
                    offset = raw_data.index(unix_bytes_8)
                    print(f"\n*** FOUND Unix timestamp (8-byte) at offset {offset} ***")

                # Dump interesting byte ranges
                print(f"\nHex dump at various offsets:")
                for offset in [0, 203, 426, 430, 432, 454, 500, 520, 540, 560]:
                    if offset + 8 <= len(raw_data):
                        chunk = raw_data[offset:offset+8]
                        print(f"  Offset {offset:3d}: {chunk.hex()} | ", end='')

                        # Try interpreting as different types
                        if len(chunk) >= 8:
                            as_double = struct.unpack('<d', chunk)[0]
                            as_int64 = struct.unpack('<Q', chunk)[0]
                            as_int32 = struct.unpack('<I', chunk[:4])[0]
                            print(f"double={as_double:.2f}, i64={as_int64}, i32={as_int32}")
                        else:
                            print()
        else:
            print(f"Record {record_id} NOT FOUND in parsed data")

        print("="*80)

if __name__ == '__main__':
    main()
