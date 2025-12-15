#!/usr/bin/env python3
"""
Extract strings from ClipMate.exe to find date/time field references
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

            # Check if printable ASCII
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
    strings = extract_strings(exe_path)
    print(f"Found {len(strings)} strings\n")

    # Search for date/time related strings
    keywords = [
        'date', 'time', 'created', 'timestamp', 'datetime',
        'tdate', 'tdatetime', 'capture', 'saved', 'recorded',
        'clip', 'field', 'table', 'column', 'record'
    ]

    matches = []
    for s in strings:
        lower = s.lower()
        for keyword in keywords:
            if keyword in lower and len(s) > 5:
                matches.append(s)
                break

    # Remove duplicates and sort
    matches = sorted(set(matches))

    print("=== Date/Time Related Strings ===")
    for match in matches[:100]:  # First 100 matches
        print(match)

    print(f"\n\nTotal matches: {len(matches)}")

    # Look specifically for SQL-like statements
    print("\n\n=== SQL-like Statements ===")
    sql_patterns = [s for s in strings if 'SELECT' in s.upper() or 'FROM' in s.upper() or 'WHERE' in s.upper()]
    for sql in sql_patterns[:20]:
        print(sql)

    # Look for field names that might be in the database
    print("\n\n=== Potential Field Names ===")
    field_patterns = [s for s in strings if s.isupper() and 4 <= len(s) <= 20 and s.isalpha()]
    date_fields = [f for f in field_patterns if 'DATE' in f or 'TIME' in f or 'CREATED' in f]
    for field in date_fields[:30]:
        print(field)

if __name__ == '__main__':
    main()
