import struct
import os

def analyze_header():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    path = os.path.join(base_dir, 'CLIP.dat')
    
    print(f"Analyzing header of {path}...")
    with open(path, 'rb') as f:
        # Read first 4KB (Header is usually variable size depending on field count)
        header = f.read(4096)
        
    print(f"Header Hex (First 128 bytes):")
    print(header[:128].hex())
    
    print("\nScanning first 1024 bytes for potential offsets:")
    # Look for TITLE offset (10) and size (90)
    # 0A 00 ... 5A 00
    
    # Look for TIMESTAMP offset (151?)
    # 97 00
    
    for i in range(0, 1024, 2):
        val = struct.unpack('<H', header[i:i+2])[0]
        if val == 10:
            print(f"  Found 10 (TITLE Offset?) at {i}")
            # Check for 90 (Size) nearby
            for j in range(max(0, i-20), min(1024, i+20), 2):
                val2 = struct.unpack('<H', header[j:j+2])[0]
                if val2 == 90:
                    print(f"    Found 90 (TITLE Size?) at {j}")
                    
        if val == 151:
             print(f"  Found 151 (TIMESTAMP Offset?) at {i}")
             
    # Dump first 512 bytes formatted
    print("\nHex Dump (0-512):")
    for i in range(0, 512, 16):
        print(f"{i:04X}: {header[i:i+16].hex()}")

if __name__ == "__main__":
    analyze_header()
