import struct
import os

import struct
import os

def analyze_schema():
    path = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.dat'
    
    with open(path, 'rb') as f:
        header = f.read(4096)
        
    field_names = [b'TITLE', b'TIMESTAMP']
    
    for name in field_names:
        try:
            idx = header.index(name)
            print(f"\nField: {name.decode()}")
            print(f"  Name Offset: {idx}")
            
            # Dump 100 bytes before and 100 bytes after
            start = max(0, idx - 100)
            end = min(len(header), idx + 100)
            context = header[start:end]
            print(f"  Context Hex ({start}-{end}):")
            print(context.hex())
            
            # Print relative offsets of non-zero bytes
            print("  Non-zero bytes relative to Name:")
            for i in range(len(context)):
                byte = context[i]
                if byte != 0:
                    rel_offset = (start + i) - idx
                    # Skip the name itself
                    if 0 <= rel_offset < len(name): continue
                    print(f"    {rel_offset}: {byte:02X} ({byte})")
        except ValueError:
            print(f"Field {name.decode()} not found in header dump (might be case sensitive or partial)")

if __name__ == "__main__":
    analyze_schema()
