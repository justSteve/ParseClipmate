import struct
import datetime

def analyze_hex():
    hex_str = "5c1600000101000000012267656d696e69636f64656173736973742e6167656e74596f6c6f4d6f6465223a20747275652c00000000000000000000000000000000000000000000014d53454447450000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001005592eaf80ecd4201f0bb08000168747470733a2f2f646f63732e636c6f75642e676f6f676c652e636f6d2f67656d696e692f646f63732f636f64656173736973742f7573652d6167656e7469632d636861742d706169722d70726f6772616d6d6572000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000109040000010000010000018100000001000001fa0600000100005c44f70ecd42010000000001000000000100000000010000017b42394536313534422d303837312d343733392d423439312d4545323531383833303134337d00017b45323142363246322d344346412d343931332d394237392d3446393535463446323032447d0001005592eaf80ecd4200000000005b160000561f640233acb5584c33891b0bd2d92f01"
    data = bytes.fromhex(hex_str)
    
    target_dt = datetime.datetime(2025, 12, 1, 15, 22, 20)
    print(f"Target Date: {target_dt}")
    
    # Unix
    unix_ts = int(target_dt.timestamp())
    print(f"Unix TS: {unix_ts}")
    
    # TDateTime (Days since 1899-12-30)
    delta = target_dt - datetime.datetime(1899, 12, 30)
    td_val = delta.days + (delta.seconds / 86400.0)
    print(f"TDateTime: {td_val}")
    
    # FileTime (100ns since 1601-01-01)
    delta_ft = target_dt - datetime.datetime(1601, 1, 1)
    ft_val = int(delta_ft.total_seconds() * 10000000)
    print(f"FileTime: {ft_val}")
    
    # Scan
    for i in range(len(data) - 8):
        # Int32
        val32 = struct.unpack('<I', data[i:i+4])[0]
        if abs(val32 - unix_ts) < 86400: # Within a day
            print(f"Possible Unix match at {i}: {val32}")
            
        # Double
        val_dbl = struct.unpack('<d', data[i:i+8])[0]
        if abs(val_dbl - td_val) < 1.0:
            print(f"Possible TDateTime match at {i}: {val_dbl}")
            
    # Scan all Int32s for Unix Date (2020-2030)
    print("\nScanning all Int32s (Unix 2020-2030):")
    for i in range(len(data) - 4):
        val32 = struct.unpack('<I', data[i:i+4])[0]
        if 1577836800 < val32 < 1893456000:
            dt = datetime.datetime.fromtimestamp(val32)
            print(f"Offset {i}: {val32} -> {dt}")

    # Scan all Int32s for DOS Date/Time
    print("\nScanning all Int32s (DOS Date/Time):")
    for i in range(len(data) - 4):
        val32 = struct.unpack('<I', data[i:i+4])[0]
        # DOS Date/Time is usually packed into 4 bytes (Date high, Time low or vice versa)
        # Low 16: Time, High 16: Date
        time_part = val32 & 0xFFFF
        date_part = (val32 >> 16) & 0xFFFF
        
        # Date: Y(7) M(4) D(5)
        year = ((date_part >> 9) & 0x7F) + 1980
        month = (date_part >> 5) & 0x0F
        day = date_part & 0x1F
        
        if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
             # Time: H(5) M(6) S(5)
             hour = (time_part >> 11) & 0x1F
             minute = (time_part >> 5) & 0x3F
             second = (time_part & 0x1F) * 2
             if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 60:
                 print(f"Offset {i}: DOS {year}-{month}-{day} {hour}:{minute}:{second}")

    # Scan for Integer Dates (Days since X)
    print("\nScanning for Integer Dates:")
    target_date = datetime.date(2025, 12, 1)
    bases = {
        "0001-01-01": datetime.date(1, 1, 1),
        "1899-12-30": datetime.date(1899, 12, 30),
        "1900-01-01": datetime.date(1900, 1, 1),
        "1970-01-01": datetime.date(1970, 1, 1)
    }
    
    for base_name, base_date in bases.items():
        days = (target_date - base_date).days
        # Check +1/-1 just in case
        targets = [days, days+1, days-1]
        
        for t in targets:
            t_bytes_le = struct.pack('<I', t)
            t_bytes_be = struct.pack('>I', t)
            
            if t_bytes_le in data:
                print(f"FOUND {base_name} days ({t}) LE at {data.index(t_bytes_le)}")
            if t_bytes_be in data:
                print(f"FOUND {base_name} days ({t}) BE at {data.index(t_bytes_be)}")
                
            # Also check 2-byte short if small enough
            if t < 65536:
                t_bytes_le_s = struct.pack('<H', t)
                if t_bytes_le_s in data:
                     print(f"FOUND {base_name} days ({t}) Short LE at {data.index(t_bytes_le_s)}")

if __name__ == "__main__":
    analyze_hex()
