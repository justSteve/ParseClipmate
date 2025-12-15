#!/usr/bin/env python3
"""
Search for DBISAM/Delphi field names in ClipMate.exe
"""
import re

def extract_strings(filename, min_length=4):
    """Extract printable strings from binary file"""
    with open(filename, 'rb') as f:
        result = []
        current_string = b""

        while True:
            byte = f.read(1)
            if not byte:
                break

            if 32 <= byte[0] <= 126:
                current_string += byte
            else:
                if len(current_string) >= min_length:
                    result.append(current_string.decode('ascii', errors='ignore'))
                current_string = b""

        if len(current_string) >= min_length:
            result.append(current_string.decode('ascii', errors='ignore'))

        return result

def main():
    exe_path = r"C:\Program Files (x86)\ClipMate7\ClipMate.exe"

    print("Extracting strings from ClipMate.exe...")
    strings = extract_strings(exe_path, min_length=3)

    # Look for DBISAM/Delphi specific terms
    print("\n=== DBISAM References ===")
    dbisam_matches = [s for s in strings if 'dbisam' in s.lower() or 'elevate' in s.lower()]
    for match in dbisam_matches[:30]:
        print(match)

    # Look for TDateTime or Delphi date/time types
    print("\n=== TDateTime and Delphi Types ===")
    tdatetime_matches = [s for s in strings if 'tdatetime' in s.lower() or 'tdate' in s.lower() or 'ttime' in s.lower()]
    for match in tdatetime_matches[:30]:
        print(match)

    # Look for potential field names (CamelCase or field-like patterns)
    print("\n=== Potential Field Names (CamelCase) ===")
    camel_pattern = re.compile(r'^[A-Z][a-z]+[A-Z][a-zA-Z]*$')
    camel_matches = [s for s in strings if camel_pattern.match(s) and 4 <= len(s) <= 30]

    # Filter for date/time related
    date_camel = [s for s in camel_matches if any(kw in s.lower() for kw in ['date', 'time', 'created', 'captured', 'saved', 'stamp'])]
    for match in date_camel[:30]:
        print(match)

    # Look for database table names
    print("\n=== Potential Table Names ===")
    table_matches = [s for s in strings if s.lower() in ['clip', 'clips', 'cliptable', 'clipdata', 'blob', 'blobpng', 'blobjpg']]
    for match in table_matches:
        print(match)

    # Look for strings that might be database field identifiers
    print("\n=== Field-like Identifiers ===")
    field_like = [s for s in strings if 5 <= len(s) <= 25 and (
        s.startswith('fld') or
        s.startswith('col') or
        '_' in s and s.replace('_', '').isalnum()
    )]
    date_fields = [f for f in field_like if any(kw in f.lower() for kw in ['date', 'time', 'created', 'stamp', 'capture'])]
    for field in date_fields[:40]:
        print(field)

    # Look for format strings that might show field names
    print("\n=== Format Strings with Field References ===")
    format_matches = [s for s in strings if '%' in s and any(kw in s.lower() for kw in ['date', 'time', 'created'])]
    for match in format_matches[:30]:
        print(match)

if __name__ == '__main__':
    main()
