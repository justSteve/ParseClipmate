import struct
import os
import sys

# Add parent dir to path to import clipmate_parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clipmate_parser import ClipmateParser, clean_string

def dump_records():
    base_dir = r'c:/Users/steve/AppData/Roaming/Thornsoft Development/ClipMate7'
    parser = ClipmateParser(base_dir)
    
    print(f"Scanning CLIP.dat in {base_dir}...")
    
    with open(parser.clip_dat, 'rb') as f:
        header_offset = parser.find_header_offset(f)
        f.seek(header_offset)
        
        count = 0
        rec_5723 = None
        rec_5724 = None
        
        while True:
            data = f.read(568)
            if len(data) < 568: break
            
            try:
                native_id = struct.unpack('<I', data[0:4])[0]
            except: native_id = 0
            
            if native_id == 5723:
                rec_5723 = data
                print(f"Found Record 5723")
            elif native_id == 5724:
                rec_5724 = data
                print(f"Found Record 5724")
                
            if rec_5723 and rec_5724:
                break
                
            count += 1
            if count > 5000: break
            
    if rec_5723 and rec_5724:
        print("\nComparing Record 5723 and 5724:")
        print(f"Record Size: {len(rec_5723)}")
        
        # Print side by side hex
        print("Offset | 5723                                            | 5724")
        print("-------|-------------------------------------------------|-------------------------------------------------")
        for i in range(0, 568, 16):
            chunk1 = rec_5723[i:i+16]
            chunk2 = rec_5724[i:i+16]
            hex1 = chunk1.hex(' ')
            hex2 = chunk2.hex(' ')
            diff = " *" if chunk1 != chunk2 else ""
            print(f"{i:04X}   | {hex1:<47} | {hex2:<47}{diff}")

if __name__ == "__main__":
    dump_records()
