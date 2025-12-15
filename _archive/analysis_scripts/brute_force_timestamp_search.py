#!/usr/bin/env python3
"""
Brute force search - try interpreting EVERY 4-byte sequence as a timestamp
with different epochs and scales
"""
import struct
from datetime import datetime, timedelta

def try_all_interpretations(bytes_val, expected_dt):
    """Try all possible timestamp interpretations of a 4-byte value"""
    matches = []

    # Interpret as unsigned int (little endian)
    val_le = struct.unpack('<I', bytes_val)[0]

    # Interpret as unsigned int (big endian)
    val_be = struct.unpack('>I', bytes_val)[0]

    # Interpret as signed int (little endian)
    val_signed_le = struct.unpack('<i', bytes_val)[0]

    # Try different epochs and scales
    epochs_to_try = [
        ("Unix (1970)", datetime(1970, 1, 1), 1),  # Standard Unix
        ("2000", datetime(2000, 1, 1), 1),  # Y2K epoch
        ("1899 (Delphi)", datetime(1899, 12, 30), 1),  # Delphi epoch (seconds)
        ("1899 (Delphi days)", datetime(1899, 12, 30), 86400),  # Delphi epoch (days as int)
        ("1980 (DOS)", datetime(1980, 1, 1), 1),  # DOS epoch
        ("1601 (Win)", datetime(1601, 1, 1), 1),  # Windows epoch (seconds)
    ]

    for name, epoch, scale in epochs_to_try:
        # Try little endian
        try:
            dt = epoch + timedelta(seconds=val_le * scale)
            if 2020 < dt.year < 2030:
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 86400:  # Within 24 hours
                    matches.append((name + " LE", dt, diff))
        except:
            pass

        # Try big endian
        try:
            dt = epoch + timedelta(seconds=val_be * scale)
            if 2020 < dt.year < 2030:
                diff = abs((dt - expected_dt).total_seconds())
                if diff < 86400:
                    matches.append((name + " BE", dt, diff))
        except:
            pass

        # Try signed (negative offsets)
        if val_signed_le < 0:
            try:
                dt = epoch + timedelta(seconds=abs(val_signed_le) * scale)
                if 2020 < dt.year < 2030:
                    diff = abs((dt - expected_dt).total_seconds())
                    if diff < 86400:
                        matches.append((name + " Signed", dt, diff))
            except:
                pass

    return matches

def main():
    clip_path = r"c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat"

    with open(clip_path, 'rb') as f:
        data = f.read()

    # Focus on record 5969
    record_id = 5969
    expected_dt_str = "12/11/2025 11:14:28 AM"
    expected_dt = datetime.strptime(expected_dt_str, "%m/%d/%Y %I:%M:%S %p")

    id_offset = 53197
    record_start = id_offset - 373
    record_data = data[record_start:record_start + 568]

    print(f"Brute force search for Record {record_id}")
    print(f"Expected: {expected_dt_str}\n")
    print("="*100 + "\n")

    all_matches = []

    # Try every 4-byte sequence in the record
    for offset in range(0, len(record_data) - 4):
        bytes_val = record_data[offset:offset+4]

        # Skip all-zero bytes
        if bytes_val == b'\x00\x00\x00\x00':
            continue

        matches = try_all_interpretations(bytes_val, expected_dt)

        for fmt, dt, diff in matches:
            all_matches.append((offset, fmt, dt, diff, bytes_val.hex()))

    # Sort by best match
    all_matches.sort(key=lambda x: x[3])

    if all_matches:
        print(f"Found {len(all_matches)} potential matches:\n")

        for offset, fmt, dt, diff, hex_val in all_matches[:20]:  # Top 20
            match_marker = ""
            if diff < 1:
                match_marker = " *** PERFECT ***"
            elif diff < 60:
                match_marker = " *** EXCELLENT ***"
            elif diff < 300:
                match_marker = " *** GOOD ***"

            print(f"Offset +{offset:3d}: {fmt:<25} {dt.strftime('%m/%d/%Y %I:%M:%S %p')}")
            print(f"  Hex: {hex_val}, Diff: {diff:.1f}s{match_marker}\n")
    else:
        print("No matches found\n")

if __name__ == '__main__':
    main()
