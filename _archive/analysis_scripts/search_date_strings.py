#!/usr/bin/env python3
"""
Search for date strings or any December 2025 patterns in all files.
Maybe timestamps are stored as text or in a custom format we haven't tried.
"""
import os
import re

def search_file_for_dates(file_path):
    """Search a file for any date-like patterns"""
    try:
        # Try reading as text first
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        except:
            with open(file_path, 'rb') as f:
                text_content = f.read().decode('latin-1', errors='ignore')

        # Date patterns to search for
        patterns = [
            r'12/1[34]/2025',  # MM/DD/YYYY
            r'2025-12-1[34]',  # YYYY-MM-DD
            r'Dec\s*1[34]',    # Dec 13, Dec 14
            r'12-1[34]-25',    # MM-DD-YY
            r'1[34]\s*Dec',    # 13 Dec, 14 Dec
        ]

        matches = []
        for pattern in patterns:
            found = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in found:
                start = max(0, match.start() - 30)
                end = min(len(text_content), match.end() + 30)
                context = text_content[start:end].replace('\n', ' ').replace('\r', '')
                matches.append((match.group(), context))

        return matches
    except Exception as e:
        return []

def main():
    base_dir = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7"

    print("="*100)
    print("SEARCHING FOR DATE STRINGS IN ALL FILES")
    print("="*100)
    print(f"\nLooking for any December 13-14, 2025 date patterns (text format)\n")

    # Get all files
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Skip very large blobs
            try:
                if os.path.getsize(file_path) < 5 * 1024 * 1024:  # < 5MB
                    all_files.append(file_path)
            except:
                pass

    files_with_matches = {}

    for file_path in all_files:
        filename = os.path.basename(file_path)
        matches = search_file_for_dates(file_path)

        if matches:
            files_with_matches[filename] = matches

    if files_with_matches:
        print(f"Found date strings in {len(files_with_matches)} file(s):\n")

        for filename, matches in files_with_matches.items():
            print(f"\n{'='*100}")
            print(f"FILE: {filename} ({len(matches)} match(es))")
            print(f"{'='*100}\n")

            for date_str, context in matches[:10]:  # Show first 10 matches
                try:
                    # Clean context for safe printing
                    clean_context = ''.join(c if 32 <= ord(c) < 127 else '.' for c in context)
                    print(f"  '{date_str}' in context: ...{clean_context}...")
                    print()
                except:
                    print(f"  '{date_str}' (context contains unprintable characters)")
                    print()

            if len(matches) > 10:
                print(f"  ... and {len(matches) - 10} more matches")
    else:
        print("NO date strings found in any files!")
        print("\nThis strongly suggests timestamps are NOT stored as text.")

if __name__ == '__main__':
    main()
