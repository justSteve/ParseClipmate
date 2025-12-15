import struct
import os
import datetime
from dateutil import parser as dateutil_parser

# Import GUID to timestamp mapping
try:
    from guid_timestamp_mapping import get_timestamp_for_guid
    TIMESTAMP_MAPPING_AVAILABLE = True
except ImportError:
    TIMESTAMP_MAPPING_AVAILABLE = False
    def get_timestamp_for_guid(guid):
        return None

def clean_string(data):
    try:
        # Decode as latin1 (common for older Windows apps) or utf-8
        # ClipMate likely uses ANSI/Windows-1252
        text = data.decode('mbcs', errors='ignore') # mbcs uses system locale
        # Stop at first null byte
        if '\x00' in text:
            text = text.split('\x00')[0]
        return text.strip()
    except:
        return ""

class BlobManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.index = {} # ID -> (blb_filename, start_block)
        self.load_indices()
        
    def load_indices(self):
        # Load blobpng.dat, BLOBJPG.dat, BLOBBLOB.dat
        for name in ['blobpng', 'BLOBJPG', 'BLOBBLOB']:
            dat_path = os.path.join(self.base_dir, f"{name}.dat")
            if os.path.exists(dat_path):
                print(f"Loading index from {dat_path}...")
                with open(dat_path, 'rb') as f:
                    data = f.read()
                    # Scan for records: 01 ID 01 Block Count (14 bytes)
                    for i in range(len(data)-13):
                        if data[i] == 1 and data[i+5] == 1:
                            clip_id = struct.unpack('<I', data[i+1:i+5])[0]
                            block = struct.unpack('<I', data[i+6:i+10])[0]
                            self.index[clip_id] = (f"{name}.blb", block)
                            
    def get_blob(self, clip_id, size):
        if clip_id not in self.index:
            return None
            
        filename, block = self.index[clip_id]
        path = os.path.join(self.base_dir, filename)
        
        if not os.path.exists(path):
            return None
            
        # Calc offset
        # Block is 1-based
        offset = (block - 1) * 8192 + 530
        
        try:
            with open(path, 'rb') as f:
                f.seek(offset)
                data = f.read(size)
                return data, filename
        except:
            return None

class ClipmateParser:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.clip_dat = os.path.join(data_dir, 'CLIP.dat')
        self.blobtxt_dat = os.path.join(data_dir, 'BLOBTXT.dat')
        self.blob_manager = BlobManager(data_dir)
        
    def find_header_offset(self, f):
        # Scan for the first GUID-like pattern to determine alignment
        # Layout A: GUID at 46
        # Layout B: GUID at 454
        
        chunk = f.read(50000)
        f.seek(0)
        
        import re
        # Pattern: {XXXXXXXX-
        # Find all matches
        matches = [m.start() for m in re.finditer(rb'\{[0-9A-F]{8}-', chunk, re.IGNORECASE)]
        
        # Check for Layout B alignment (GUID at 454)
        for pos in matches:
            # If this is Layout B, record start is pos - 454
            rec_start = pos - 454
            if rec_start >= 0:
                # Verify? Maybe check ID at 0?
                # For now, just return it if it looks plausible
                print(f"Detected Layout B alignment at {rec_start} (GUID at {pos})")
                return rec_start

        # Check for Layout A alignment (GUID at 46)
        for pos in matches:
            rec_start = pos - 46
            if rec_start >= 0:
                print(f"Detected Layout A alignment at {rec_start} (GUID at {pos})")
                return rec_start
        
        print("Could not detect alignment, defaulting to 0")
        return 0

    def parse_clips(self):
        records = []
        if not os.path.exists(self.clip_dat):
            print(f"File not found: {self.clip_dat}")
            return records

        if TIMESTAMP_MAPPING_AVAILABLE:
            print(f"Parsing {self.clip_dat} (using GUID timestamp mapping)...")
        else:
            print(f"Parsing {self.clip_dat} (no timestamp mapping available)...")
        with open(self.clip_dat, 'rb') as f:
            header_size = self.find_header_offset(f)
            f.seek(header_size)
            
            record_size = 568
            index = 0
            while True:
                data = f.read(record_size)
                if len(data) < record_size:
                    break
                
                # Skip empty records (all zeros)
                if all(b == 0 for b in data):
                    index += 1
                    continue

                try:
                    # Detect Layout
                    # Layout A (Old): GUID at 46
                    # Layout B (New): ID at 0, GUID at 454
                    
                    layout = 'unknown'
                    
                    # Check Layout B (ID at 0)
                    try:
                        id_val = struct.unpack('<I', data[0:4])[0]
                        if 0 < id_val < 1000000:
                            # Check GUID at 454
                            guid_check = clean_string(data[454:492])
                            if guid_check.startswith('{') and len(guid_check) == 38:
                                layout = 'B'
                    except: pass
                    
                    if layout == 'unknown':
                        # Check Layout A (GUID at 46)
                        guid_check = clean_string(data[46:84])
                        if guid_check.startswith('{') and len(guid_check) == 38:
                            layout = 'A'
                            
                    if layout == 'B':
                        # Parse using Layout B
                        native_id = struct.unpack('<I', data[0:4])[0]
                        
                        # Title starts at 10 (0x0A), not 16
                        title = clean_string(data[10:100]) 
                        
                        creator = clean_string(data[72:140]) # Source at 72
                        url = "" 
                        guid1 = clean_string(data[454:492])
                        
                        try:
                            size = struct.unpack('<I', data[422:426])[0]
                        except: size = 0
                        
                        # Date: Try to get from GUID timestamp mapping first
                        created_at = None

                        # Method 1: Use GUID timestamp mapping (from XML export)
                        if TIMESTAMP_MAPPING_AVAILABLE and guid1:
                            timestamp_str = get_timestamp_for_guid(guid1)
                            if timestamp_str:
                                try:
                                    # Parse ISO 8601 format: 2025-12-13T06:04:04.214-06:00
                                    dt = dateutil_parser.parse(timestamp_str)
                                    created_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    pass

                        # Method 2: Parse from Title for Graphic clips (fallback)
                        if not created_at and title.startswith("Graphic:"):
                            try:
                                # Graphic:12/1/2025 10:41:22 PM
                                date_str = title.split('Graphic:')[1].strip()
                                dt = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
                                created_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass

                        # Method 3: Unknown (no timestamp found)
                        if not created_at:
                             created_at = "Unknown"

                    else:
                        # Parse using Layout A (Old)
                        native_id = 0 # Didn't parse ID in Layout A
                        guid1 = clean_string(data[46:84]) 
                        title = clean_string(data[170:230])
                        creator = clean_string(data[232:300])
                        url = clean_string(data[308:450])
                        
                        try:
                            ts = struct.unpack('<I', data[151:155])[0]
                            if ts > 0:
                                created_at = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                created_at = "Unknown"
                        except:
                            created_at = "Unknown"
                            
                        try:
                            size = struct.unpack('<I', data[14:18])[0]
                        except: size = 0

                    if index < 5 or (layout == 'B' and index < 20):
                        print(f"--- Record {index} (Layout {layout}) ---")
                        print(f"Parsed GUID: {guid1}")
                        print(f"Parsed Title: {title}")
                        print(f"Parsed ID: {native_id}")
                        print(f"Parsed Size: {size}")
                        print(f"Parsed Date: {created_at}")

                    record = {
                        'id': index,
                        'guid': guid1,
                        'title': title,
                        'creator': creator,
                        'url': url,
                        'created_at': created_at,
                        'size': size,
                        'native_id': native_id,
                        'raw_data': data
                    }
                    records.append(record)
                except Exception as e:
                    print(f"Error parsing record {index}: {e}")
                
                index += 1
        return records

    def parse_blobtxt(self):
        records = []
        # Blob parsing is currently unreliable due to unknown linking format.
        # Returning empty list to avoid garbage content.
        return records
        
        if not os.path.exists(self.blobtxt_dat):
            return records
            
        blob_file = self.blobtxt_dat.replace('.dat', '.blb')
        if not os.path.exists(blob_file):
            return records
            
        blob_size = os.path.getsize(blob_file)
        
        print(f"Parsing {self.blobtxt_dat} (scanning for pointers)...")
        with open(self.blobtxt_dat, 'rb') as f:
            # Skip likely header
            f.seek(4096)
            
            record_size = 56
            while True:
                data = f.read(record_size)
                if len(data) < record_size:
                    break
                
                try:
                    # Try to interpret as [ClipID, BlobID, Offset, Size]
                    # This is a guess, but common for these DBs
                    # We look for reasonable values
                    ints = struct.unpack('<IIII', data[:16])
                    clip_id, blob_id, offset, size = ints
                    
                    # Validation heuristics
                    if size > 0 and size < 10000000 and offset + size <= blob_size:
                        # Valid-looking pointer
                        content = self.read_blob_content(offset, size, blob_file)
                        if content:
                            try:
                                text = content.decode('latin1', errors='ignore') # Text blobs are usually text
                                records.append({
                                    'clip_id': clip_id,
                                    'content': text
                                })
                            except:
                                pass
                except:
                    pass
        return records

    def read_blob_content(self, offset, size, blob_file_path):
        if not os.path.exists(blob_file_path):
            return None
        with open(blob_file_path, 'rb') as f:
            f.seek(offset)
            return f.read(size)


if __name__ == "__main__":
    parser = ClipmateParser('/root/projects/ParseClipmate/exploration')
    clips = parser.parse_clips()
    print(f"Parsed {len(clips)} clips")
    for c in clips[:5]:
        print(f"Title: {c['title']}")
        print(f"URL: {c['url']}")
        print("-" * 20)
