import re
import sys

def extract_strings(filename, min_len=15):
    with open(filename, "rb") as f:
        data = f.read()
    
    # Regex for printable characters
    # We look for longer sequences to avoid noise
    pattern = rb"[\x20-\x7E]{" + str(min_len).encode() + rb",}"
    
    matches = re.findall(pattern, data)
    
    for m in matches:
        try:
            s = m.decode('utf-8')
            # Filter out strings that look like pure garbage (e.g. too many symbols)
            if len(s) > min_len:
                print(f"--- STRING LEN {len(s)} ---")
                print(s)
                print("\n")
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_strings.py <file>")
        sys.exit(1)
    
    extract_strings(sys.argv[1])
