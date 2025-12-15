#!/usr/bin/env python3
"""
Parse ClipMate XML export to extract GUID->timestamp mappings.
This is the solution to the timestamp mystery!
"""
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def parse_xml_timestamps(xml_path):
    """Parse XML export and extract GUID to timestamp mapping"""
    print(f"Parsing {xml_path}...")

    # Parse XML incrementally to handle large file
    guid_to_timestamp = {}
    guid_to_title = {}

    try:
        # Use iterparse for memory efficiency
        context = ET.iterparse(xml_path, events=('start', 'end'))
        context = iter(context)

        current_clip = {}
        in_clip = False

        for event, elem in context:
            if event == 'start' and elem.tag == 'Clip':
                in_clip = True
                current_clip = {}

            elif event == 'end' and in_clip:
                if elem.tag == 'ID':
                    current_clip['guid'] = elem.text
                elif elem.tag == 'TIMESTAMP':
                    current_clip['timestamp'] = elem.text
                elif elem.tag == 'TITLE':
                    current_clip['title'] = elem.text
                elif elem.tag == 'Clip':
                    # End of clip, save mapping
                    if 'guid' in current_clip and 'timestamp' in current_clip:
                        guid = current_clip['guid']
                        timestamp = current_clip['timestamp']
                        title = current_clip.get('title', '')

                        guid_to_timestamp[guid] = timestamp
                        guid_to_title[guid] = title

                    in_clip = False
                    current_clip = {}

                    # Clear element to free memory
                    elem.clear()

        print(f"Extracted {len(guid_to_timestamp)} GUID to timestamp mappings\n")
        return guid_to_timestamp, guid_to_title

    except Exception as e:
        print(f"Error parsing XML: {e}")
        return {}, {}

def test_mappings(guid_to_timestamp, guid_to_title):
    """Test the mappings with our known test records"""
    test_guids = {
        '{2E401BC1-C828-42E8-8083-EA7036CEE334}': ('6001', '2025-12-13T06:04:04'),
        '{4C572B0E-67D5-4BD9-B94B-3ABB27A9C74C}': ('6017', '2025-12-14T08:58:00'),
        '{AE63C3E6-6FE4-4302-BF91-03272223B5AD}': ('6018', '2025-12-14T09:35:03'),
        '{10D124FD-AF21-44F8-B982-8FC0A61C0E02}': ('6019', '2025-12-14T10:38:01'),
        '{E43E1A4B-3F20-437D-BD64-F04B35F92AA0}': ('6020', '2025-12-14T10:38:25'),
        '{2F309264-EF3E-4351-82C9-6D33D95A69B3}': ('6021', '2025-12-14T10:47:10'),
    }

    print("="*100)
    print("TESTING GUID TO TIMESTAMP MAPPINGS")
    print("="*100 + "\n")

    matches = 0
    for guid, (record_id, expected_ts) in test_guids.items():
        if guid in guid_to_timestamp:
            actual_ts = guid_to_timestamp[guid]
            title = guid_to_title.get(guid, '')[:60]

            # Compare timestamps (ignore milliseconds and timezone)
            expected_prefix = expected_ts
            actual_prefix = actual_ts[:len(expected_prefix)]

            match = expected_prefix == actual_prefix
            matches += match

            marker = "[OK] MATCH" if match else "[X] MISMATCH"
            print(f"Record {record_id}: {marker}")
            print(f"  GUID: {guid}")
            print(f"  Expected: {expected_ts}...")
            print(f"  Actual:   {actual_ts}")
            print(f"  Title: {title}")
            print()
        else:
            print(f"Record {record_id}: GUID NOT FOUND in XML")
            print(f"  GUID: {guid}\n")

    print(f"{'='*100}")
    print(f"RESULTS: {matches}/{len(test_guids)} test records matched")
    print(f"{'='*100}\n")

    return matches == len(test_guids)

def save_mapping_to_file(guid_to_timestamp, output_path):
    """Save GUID→timestamp mapping to a Python file for use in parser"""
    print(f"Saving mapping to {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""\n')
        f.write("GUID to timestamp mapping extracted from ClipMate XML export.\n")
        f.write("Use this to add timestamps to parsed clips.\n")
        f.write('"""\n\n')
        f.write("GUID_TO_TIMESTAMP = {\n")

        for guid, timestamp in sorted(guid_to_timestamp.items()):
            f.write(f"    '{guid}': '{timestamp}',\n")

        f.write("}\n\n")

        f.write("def get_timestamp_for_guid(guid):\n")
        f.write('    """Get timestamp for a GUID, or None if not found"""\n')
        f.write("    return GUID_TO_TIMESTAMP.get(guid)\n")

    print(f"Saved {len(guid_to_timestamp)} mappings to {output_path}\n")

def main():
    xml_path = r"C:\myStuff\ParseClipmate\ClipMate_Export_MYDESK_My Clips_2025-12-15_044754.XML"
    output_path = r"C:\myStuff\ParseClipmate\guid_timestamp_mapping.py"

    print("="*100)
    print("PARSING CLIPMATE XML EXPORT TO SOLVE TIMESTAMP MYSTERY")
    print("="*100 + "\n")

    # Parse XML
    guid_to_timestamp, guid_to_title = parse_xml_timestamps(xml_path)

    if not guid_to_timestamp:
        print("ERROR: No mappings extracted from XML")
        return

    # Test with known records
    success = test_mappings(guid_to_timestamp, guid_to_title)

    # Save mapping
    save_mapping_to_file(guid_to_timestamp, output_path)

    if success:
        print("*** SUCCESS! ***")
        print("\nThe timestamp mystery is solved:")
        print("  1. Timestamps ARE stored in the database (accessible via ClipMate export)")
        print("  2. The mapping is GUID→timestamp")
        print("  3. We can now use guid_timestamp_mapping.py in the parser")
        print("\nNext step: Update clipmate_parser.py to import and use this mapping")
    else:
        print("*** WARNING: Some test records did not match ***")
        print("The mapping may be incomplete or incorrect")

if __name__ == '__main__':
    main()
