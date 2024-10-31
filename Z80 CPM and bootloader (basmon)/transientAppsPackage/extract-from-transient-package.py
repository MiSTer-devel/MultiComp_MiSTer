import os

def parse_hex_byte(hex_chars):
    """Convert two hex characters to a byte."""
    try:
        return int(hex_chars, 16)
    except ValueError:
        return None

def parse_hex_line(line):
    """Parse an Intel HEX format line and return the data bytes."""
    # Skip leading U0 lines
    if line.startswith('U0'):
        return []
    # Skip empty lines
    if not line.strip():
        return []
    # Remove any whitespace and verify format
    line = line.strip()
    if not line.startswith(':'):
        return []
    
    # Convert hex string to bytes
    data = []
    i = 1  # Skip the starting ':'
    while i < len(line):
        if i+1 < len(line):
            byte = parse_hex_byte(line[i:i+2])
            if byte is not None:
                data.append(byte)
        i += 2
    
    return data

def extract_files(filename):
    """Extract files from CPM211FilesPkg.txt."""
    current_file = None
    current_data = bytearray()
    checksum = 0
    
    # Get the directory of the input file to save extracted files in the same location
    output_dir = os.path.dirname(filename)
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for new file header
        if line.startswith('A:DOWNLOAD'):
            # Save previous file if exists
            if current_file:
                output_path = os.path.join(output_dir, current_file.lower())
                with open(output_path, 'wb') as outf:
                    outf.write(current_data)
                print(f"Extracted: {current_file} ({len(current_data)} bytes)")
            
            # Start new file
            current_file = line.split()[1]
            current_data = bytearray()
            checksum = 0
            i += 1
            continue
        
        # Check for end of file marker
        if '>' in line:
            # Parse data up to '>'
            end_pos = line.index('>')
            if end_pos > 0:
                data_portion = line[:end_pos]
                if data_portion.startswith(':'):
                    data_bytes = parse_hex_line(data_portion)
                    if data_bytes:
                        current_data.extend(data_bytes)
                        for byte in data_bytes:
                            checksum = (checksum + byte) & 0xFF
            
            # Get format marker and checksum after '>'
            if len(line) > end_pos + 1:
                try:
                    trailer = line[end_pos+1:].strip()
                    if len(trailer) >= 4:
                        format_marker = trailer[0:2]
                        expected_checksum = parse_hex_byte(trailer[2:4])
                        
                        if format_marker != '00':
                            print(f"Warning: Invalid format marker in {current_file}")
                            print(f"Expected: 00, Got: {format_marker}")
                        else:
                            print(f"Format marker verified for {current_file}")
                            
                        if expected_checksum != checksum:
                            print(f"Warning: Checksum mismatch in {current_file}")
                            print(f"Expected: {expected_checksum:02X}, Got: {checksum:02X}")
                        else:
                            print(f"Checksum verified for {current_file}")
                except:
                    print(f"Warning: Could not verify format marker and checksum for {current_file}")
            
            # Save the file
            if current_file:
                output_path = os.path.join(output_dir, current_file.lower())
                with open(output_path, 'wb') as outf:
                    outf.write(current_data)
                print(f"Extracted: {current_file} ({len(current_data)} bytes)")
                current_file = None
                current_data = bytearray()
                checksum = 0
            
        else:
            # Parse regular hex data line
            data_bytes = parse_hex_line(line)
            if data_bytes:
                current_data.extend(data_bytes)
                for byte in data_bytes:
                    checksum = (checksum + byte) & 0xFF
        
        i += 1

def main():
    # Use relative path for input file
    input_file = "Z80 CPM and bootloader (basmon)/transientAppsPackage/CPM211FilesPkg.txt"    
    
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}")
        return
    
    print(f"Extracting files from {input_file}...")
    extract_files(input_file)
    print("Extraction complete!")

if __name__ == "__main__":
    main()