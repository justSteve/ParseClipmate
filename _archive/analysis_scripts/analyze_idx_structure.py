import struct
import os

def analyze_idx():
    path = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7/CLIP.idx'
    with open(path, 'rb') as f:
        data = f.read(1024)
        
    print(f"File size: {os.path.getsize(path)}")
    print("First 64 bytes hex:")
    print(data[:64].hex())
    
    # Try to read as ID (4) + Offset (4)
    print("\nScanning as ID(4)+Offset(4):")
    for i in range(0, 128, 8):
        rec = data[i:i+8]
        if len(rec) < 8: break
        id_val = struct.unpack('<I', rec[0:4])[0]
        offset = struct.unpack('<I', rec[4:8])[0]
        print(f"  ID: {id_val}, Offset: {offset}")

    # Try to read as ID(4) + Date(4) + Offset(4)?
    print("\nScanning as ID(4)+Date(4)+Offset(4) (12 bytes):")
    for i in range(0, 128, 12):
        rec = data[i:i+12]
        if len(rec) < 12: break
        v1 = struct.unpack('<I', rec[0:4])[0]
        v2 = struct.unpack('<I', rec[4:8])[0]
        v3 = struct.unpack('<I', rec[8:12])[0]
        print(f"  V1: {v1}, V2: {v2}, V3: {v3}")

if __name__ == "__main__":
    analyze_idx()
