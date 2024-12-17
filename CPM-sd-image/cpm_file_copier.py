"""
CP/M 2.2 Disk Image File Handler

This program provides tools for working with CP/M 2.2 disk images, allowing extraction
and insertion of files. It handles the complex CP/M directory structure and file 
allocation system.

Capabilities:
- Extract files from CP/M disk images to a modern filesystem
- Copy files from a modern filesystem into CP/M disk images
- Create new CP/M disk images with CP/M and CBIOS installed
- Handle multiple user areas (0-15)
- Support multiple drives (A-P)
- Process files of any size (automatically splits across multiple extents)
- Preserve CP/M file attributes and structure
- Works with 8MB disk images using 4KB blocks

Usage Examples:

1. Create a new disk image with one drive and install CP/M:
   python cp_file_handler.py --init --drives 1 --hex-path path/to/hexfiles
   
2. Copy files to drive A, user area 0:
   a. Create directory structure:
      mkdir -p to_img/A/0
   b. Copy your files into to_img/A/0/
   c. Run the copy command:
      python cp_file_handler.py --copy --image my_disk.img

3. Extract files from drive A:
   a. Files will be extracted to from_img/A/0/ etc.
   b. Run extract command:
      python cp_file_handler.py --image my_disk.img

Options:
  --image FILE    Specify CP/M disk image (default: cpm-zeroed.img)
  --to DIR        Source directory for copying files to image (default: to_img)
  --from DIR      Target directory for extracting files (default: from_img)
  --copy          Copy files to the image (default is to extract)
  --init          Initialize a new disk image
  --drives N      Number of drives for new image (1-16, default 16)
  --force         Force overwrite of existing image
  --hex-path DIR  Base path for hex files (default: hexFiles)
  --cpm FILE      Path to CP/M hex file (default: hexFiles/cpm22.hex)
  --cbios FILE    Path to CBIOS hex file (default: hexFiles/cbios128.hex)

Directory Structure:
  When extracting files (--from):
    from_img/
      A/           # Drive A
        0/         # User 0
        1/         # User 1
        ...
      B/           # Drive B
        0/
        ...
      
  When copying files (--to):
    to_img/
      A/           # Files to copy to drive A
        0/         # Files for user 0
        1/         # Files for user 1
        ...
      B/           # Files to copy to drive B
        0/
        ...

System Track (Track 0) Layout:
  0x0000 - 0x15FF : CP/M 2.2 system (loaded to 0xD000 in memory)
  0x1600 - ...    : CBIOS (loaded to 0xE600 in memory)

Notes:
- When initializing a disk, CP/M and CBIOS hex files are processed and written to track 0
- CP/M hex segments found above 0xE600 are overwritten by CBIOS segments
- CBIOS segments are always written last to ensure they take precedence
- Directory starts at 0x4000 for drive A
- Each directory entry is 32 bytes
- File allocation uses 4KB blocks
- Maximum file size per extent is 32KB (8 blocks * 4KB)

CP/M 2.2 Directory Entry Format (32 bytes):
Offset  Size    Description
0       1       User number (0-15). 0xE5 indicates a deleted entry
1       8       Filename, ASCII padded with spaces
9       3       Filetype, ASCII padded with spaces
12      1       EX - Extent counter, low byte (0-31)
13      1       S1 - Reserved, should be 0
14      1       S2 - Extent counter, high byte
15      1       RC - Number of 128-byte records used in this extent
16      16      Block numbers - Eight 16-bit values stored LSB first

Recent Updates:
- Fixed handling of CP/M hex segments that overlap with CBIOS area
- Improved track 0 initialization with proper segment ordering
- Added verification of track 0 contents after writing
- Added detailed segment analysis output
- Fixed directory initialization for single-drive images
- Added better error handling for missing hex files
- Added force option for skipping confirmation prompts
- Added hex file path configuration options
- Improved debug output and progress reporting
"""

import os
import sys
import struct
import argparse
from typing import List, Tuple

# Constants based on the provided specifications
DRIVES = 16  # A: to P:
DRIVE_SIZE_MB = 8
BLOCK_SIZE = 4096
DIRECTORY_ENTRIES_PER_DRIVE = 512
CPM_SECTOR_SIZE = 128
BLOCKS_PER_EXTENT = 8  # 8 blocks per extent (16 bytes / 2 bytes per block number)
SD_SECTOR_SIZE = 512
BLOCKED_SECTORS_PER_TRACK = 32
TRACKS_PER_DRIVE = 512
RESERVED_BLOCKS = 4  # File data starts at block 4
UNUSED_DIR_MARKER = 0xE5  # Marker for unused directory entries
UNUSED_DATA_MARKER = 0x00  # Marker for unused data blocks

# Default values
DEFAULT_IMAGE_FILE = "cpm-new.img"
DEFAULT_TO_DIR = "to_img"
DEFAULT_FROM_DIR = "from_img"
DEFAULT_HEX_PATH = os.path.join("Z80 CPM and bootloader (basmon)/hexFiles")  # Base path for hex files
DEFAULT_CPM_HEX = os.path.join(DEFAULT_HEX_PATH, "cpm22.hex")
DEFAULT_CBIOS_HEX = os.path.join(DEFAULT_HEX_PATH, "cbios128.hex")

# Track 0 offsets for CP/M and CBIOS
CPM_DISK_OFFSET = 0x0000    # CP/M starts at beginning of track 0
CBIOS_DISK_OFFSET = 0x1600  # CBIOS starts at 0x1600 in track 0

def parse_intel_hex_line(line: str) -> tuple[int, int, int, bytes, int]:
    """
    Parse a single line of Intel HEX format.
    Returns (byte_count, address, record_type, data, checksum)
    """
    if not line.startswith(':'):
        raise ValueError("Invalid HEX record (missing start marker)")
        
    try:
        line = line.strip()
        byte_count = int(line[1:3], 16)
        address = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        
        # Calculate where data ends based on byte count
        data_end = 9 + (byte_count * 2)
        data = bytes.fromhex(line[9:data_end])
        
        checksum = int(line[data_end:data_end+2], 16)
        
        # Verify checksum
        calc_sum = byte_count
        calc_sum += (address >> 8) & 0xFF
        calc_sum += address & 0xFF
        calc_sum += record_type
        calc_sum += sum(data)
        calc_sum = ((~calc_sum) + 1) & 0xFF
        
        if calc_sum != checksum:
            raise ValueError(f"Checksum mismatch: expected {checksum:02X}, calculated {calc_sum:02X}")
            
        return byte_count, address, record_type, data, checksum
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid HEX record format: {str(e)}")

def parse_intel_hex(hex_content: str) -> list[tuple[int, bytes]]:
    """
    Parse complete Intel HEX format file and return list of (address, data) segments.
    Handles extended segment addresses and verifies checksums.
    """
    segments = []
    base_address = 0
    
    for line in hex_content.strip().split('\n'):
        if not line:
            continue
            
        try:
            byte_count, address, record_type, data, checksum = parse_intel_hex_line(line)
            
            if record_type == 0:  # Data record
                absolute_address = base_address + address
                segments.append((absolute_address, data))
                
            elif record_type == 1:  # End of file
                break
                
            elif record_type == 2:  # Extended segment address
                base_address = int.from_bytes(data, byteorder='big') << 4
                
            elif record_type == 4:  # Extended linear address
                base_address = int.from_bytes(data, byteorder='big') << 16
                
        except ValueError as e:
            print(f"Warning: Skipping invalid HEX record: {e}")
            continue
            
    return segments

def verify_track0(image_file: str):
    """Verify track 0 contents to ensure both CP/M and CBIOS are present"""
    print("\nVerifying track 0 contents:")
    try:
        with open(image_file, 'rb') as f:
            # Check CP/M area (0x0000-0x15FF)
            f.seek(0x0000)
            cpm_data = f.read(0x1600)
            cpm_sum = sum(cpm_data) & 0xFF
            print(f"CP/M area (0x0000-0x15FF):")
            print(f"  First bytes: {' '.join([f'{b:02X}' for b in cpm_data[:16]])}")
            print(f"  Checksum: 0x{cpm_sum:02X}")
            print(f"  Non-zero bytes: {sum(1 for b in cpm_data if b != 0)}")

            # Check CBIOS area (0x1600-0x1FFF)
            f.seek(0x1600)
            bios_data = f.read(0xA00)  # Read up to end of track
            bios_sum = sum(bios_data) & 0xFF
            print(f"\nCBIOS area (0x1600-0x1FFF):")
            print(f"  First bytes: {' '.join([f'{b:02X}' for b in bios_data[:16]])}")
            print(f"  Checksum: 0x{bios_sum:02X}")
            print(f"  Non-zero bytes: {sum(1 for b in bios_data if b != 0)}")

    except Exception as e:
        print(f"Error verifying track 0: {e}")

def write_hex_to_image(image_file: str, hex_content: str, base_offset: int = 0):
    """
    Write Intel HEX file content to disk image at specified base offset.
    The hex files contain memory addresses which we ignore - we write sequentially
    from the base_offset instead.
    
    Args:
        image_file: Path to disk image file
        hex_content: Intel HEX format content
        base_offset: Disk offset where to start writing the data
                    CCP goes at 0x0000, BIOS at 0x1600 in track 0
    """
    segments = parse_intel_hex(hex_content)
    
    # Sort segments by memory address to maintain proper order
    segments.sort(key=lambda x: x[0])
    
    with open(image_file, 'r+b') as f:
        current_offset = base_offset
        for _, data in segments:
            # Double check we're not writing beyond track 0
            if current_offset >= 0x2000:  # Track 0 max size
                print(f"Warning: Attempting to write beyond track 0 at offset 0x{current_offset:04X}")
                break
                
            f.seek(current_offset)
            f.write(data)
            print(f"Wrote {len(data)} bytes at disk offset 0x{current_offset:04X}")
            current_offset += len(data)
        
        print(f"Total bytes written: {current_offset - base_offset}")
        
        # After writing, verify the data (only in track 0)
        if base_offset < 0x2000:
            print("Verifying track 0 data...")
            f.seek(base_offset)
            data = f.read(current_offset - base_offset)
            checksum = sum(data) & 0xFF
            print(f"Track 0 checksum: 0x{checksum:02X}")

def get_drive_offset(drive_index: int) -> int:
    """Calculate offset for given drive index."""
    if drive_index == 0:  # Drive A
        return 0x4000  # Directory starts at 0x4000 for drive A
    return drive_index * DRIVE_SIZE_MB * 1024 * 1024

def read_directory(image_file: str, drive_index: int) -> List[Tuple[str, int, List[int], int, int, int]]:
    """
    Read directory entries, handling multiple extents.
    Returns list of tuples: (filename, user_number, block_list, extent_low, extent_high, record_count)
    """
    directory = []
    offset = get_drive_offset(drive_index)
    with open(image_file, 'rb') as f:
        f.seek(offset)
        for _ in range(DIRECTORY_ENTRIES_PER_DRIVE):
            entry = f.read(32)
            if entry[0] == UNUSED_DIR_MARKER:  # Empty entry
                continue
            user_number = entry[0]
            if user_number == UNUSED_DIR_MARKER:
                continue
            
            filename = entry[1:9].decode('ascii').strip()
            extension = entry[9:12].decode('ascii').strip()
            full_name = f"{filename}.{extension}" if extension else filename
            
            # Handle extent counters
            extent_low = entry[12]  # EX byte
            s1 = entry[13]      # Reserved byte (should be 0)
            extent_high = entry[14]  # S2 byte
            record_count = entry[15]
            
            # Read block numbers as 16-bit values
            blocks = []
            block_data = entry[16:32]  # 16 bytes for block allocation
            for i in range(0, 16, 2):  # Process 2 bytes at a time
                block_number = struct.unpack('<H', block_data[i:i+2])[0]
                if block_number != 0:  # Only include non-zero blocks
                    blocks.append(block_number)
            
            directory.append((full_name, user_number, blocks, extent_low, extent_high, record_count))
    
    return directory

def map_memory_to_disk_offset(memory_addr: int, section: str) -> int:
    """
    Convert a memory address to its corresponding disk offset
    For CPM: memory 0xD000 -> disk 0x0000
    For CBIOS: memory 0xE600 -> disk 0x1600
    """
    if section == "CPM":
        return memory_addr - 0xD000  # Map 0xD000 -> 0x0000
    else:  # CBIOS
        return 0x1600 + (memory_addr - 0xE600)  # Map 0xE600 -> 0x1600

def write_track0_image(image_file: str, cpm_hex: str, cbios_hex: str):
    """
    Write track 0 with proper segment handling and CBIOS precedence.
    CP/M segments between 0xD000 and 0xE5FF
    CBIOS segments start at 0xE600 and overwrite any overlapping CP/M segments
    """
    # Parse both hex files
    cpm_segments = parse_intel_hex(cpm_hex)
    cbios_segments = parse_intel_hex(cbios_hex)
    
    # Calculate total size
    total_size = 24 * 512  # 24 sectors * 512 bytes = 12KB
    
    print("\nAnalyzing segments:")
    print("\nCP/M segments:")
    for addr, data in sorted(cpm_segments, key=lambda x: x[0]):
        # Note but don't warn about overlapping segments - they'll be overwritten
        if addr >= 0xE600:
            print(f"  Note: CP/M segment at 0x{addr:04X} will be overwritten by CBIOS")
        print(f"  Memory 0x{addr:04X}-0x{addr+len(data)-1:04X}: {len(data)} bytes")
    
    print("\nCBIOS segments:")
    for addr, data in sorted(cbios_segments, key=lambda x: x[0]):
        print(f"  Memory 0x{addr:04X}-0x{addr+len(data)-1:04X}: {len(data)} bytes")
        
    with open(image_file, 'r+b') as f:
        # Zero out track 0
        f.seek(0)
        f.write(bytes([0] * total_size))
        
        # Write CP/M segments
        print("\nWriting CP/M segments...")
        for addr, data in sorted(cpm_segments, key=lambda x: x[0]):
            disk_offset = addr - 0xD000  # Map memory address to disk offset
            if disk_offset >= 0:  # Only write if it maps to disk
                f.seek(disk_offset)
                f.write(data)
                print(f"  Memory 0x{addr:04X} -> Disk 0x{disk_offset:04X}, {len(data)} bytes")
            
        # Write CBIOS segments - these will overwrite any overlapping CP/M segments
        print("\nWriting CBIOS segments...")
        for addr, data in sorted(cbios_segments, key=lambda x: x[0]):
            if addr >= 0xE600:
                disk_offset = 0x1600 + (addr - 0xE600)
                if disk_offset + len(data) <= total_size:
                    f.seek(disk_offset)
                    f.write(data)
                    print(f"  Memory 0x{addr:04X} -> Disk 0x{disk_offset:04X}, {len(data)} bytes")
                else:
                    print(f"Warning: CBIOS segment at 0x{addr:04X} would exceed track 0")
            else:
                print(f"Warning: CBIOS segment at unexpected address 0x{addr:04X}")
            
        # Verify the data
        print("\nVerifying track 0...")
        f.seek(0)
        track_data = f.read(total_size)
        non_zero = sum(1 for b in track_data if b != 0)
        print(f"Track 0: {non_zero} non-zero bytes of {total_size} total")
        
        # Show detailed segment analysis
        segments = []
        current_segment = None
        for i in range(0, total_size):
            f.seek(i)
            byte = f.read(1)[0]
            if byte != 0:
                if current_segment is None:
                    current_segment = [i, i]
                else:
                    current_segment[1] = i
            elif current_segment is not None:
                segments.append(current_segment)
                current_segment = None
                
        if current_segment:
            segments.append(current_segment)
            
        print("\nDetailed disk layout:")
        for start, end in segments:
            f.seek(start)
            data = f.read(end - start + 1)
            checksum = sum(data) & 0xFF
            area = "CP/M" if start < 0x1600 else "CBIOS"
            print(f"{area} 0x{start:04X}-0x{end:04X}: {end-start+1} bytes, checksum 0x{checksum:02X}")

def create_blank_disk_image(image_file: str, drives: int = 16, cpm_hex=None, cbios_hex=None):
    """
    Create a blank CP/M disk image and write system to track 0.
    The image file will be created in the current working directory.
    
    Args:
        image_file (str): Name of the image file to create
        drives (int): Number of drives to initialize (1-16)
        cpm_hex (str, optional): CP/M hex content
        cbios_hex (str, optional): CBIOS hex content
    """
    # Ensure the image file is created in current directory
    image_path = os.path.basename(image_file)
    
    # Calculate total size
    drive_size = DRIVE_SIZE_MB * 1024 * 1024  # 8MB per drive
    total_size = drive_size * drives

    print(f"\nCreating disk image '{image_path}' in {os.getcwd()}")
    print(f"Total size: {total_size / (1024*1024):.1f} MB")

    # Create the file in current directory
    with open(image_path, 'wb') as f:
        # Write zeros to the entire file
        buffer_size = 1024 * 1024  # 1MB buffer
        zeros = bytes([0] * buffer_size)
        
        bytes_written = 0
        while bytes_written < total_size:
            remaining = total_size - bytes_written
            to_write = min(buffer_size, remaining)
            if to_write < buffer_size:
                zeros = bytes([0] * to_write)
            f.write(zeros)
            bytes_written += to_write
            print(f"Writing disk image: {(bytes_written * 100) // total_size}% complete", end='\r')
        
        print("\nInitializing directories...")
        
        # Initialize directory areas for each drive
        for drive in range(drives):
            dir_offset = get_drive_offset(drive)
            f.seek(dir_offset)
            
            # Write empty directory entries
            dir_entry = bytes([UNUSED_DIR_MARKER] + [0] * 31)
            for _ in range(DIRECTORY_ENTRIES_PER_DRIVE):
                f.write(dir_entry)

    # Write CP/M and CBIOS as one block if both are provided
    if cpm_hex and cbios_hex:
        print("\nWriting system to track 0...")
        write_track0_image(image_path, cpm_hex, cbios_hex)
    else:
        print("Warning: Both CP/M and CBIOS hex files required for system track")

    print(f"\nDisk image created successfully: {image_path}")

def main():
    parser = argparse.ArgumentParser(description="CP/M 2.2 disk image manipulation tool")
    parser.add_argument("--image", default=DEFAULT_IMAGE_FILE, help=f"CP/M disk image file (default: {DEFAULT_IMAGE_FILE})")
    parser.add_argument("--to", default=DEFAULT_TO_DIR, help=f"Source directory for files to copy to image (default: {DEFAULT_TO_DIR})")
    parser.add_argument("--from", dest="from_dir", default=DEFAULT_FROM_DIR, help=f"Target directory for extracted files (default: {DEFAULT_FROM_DIR})")
    parser.add_argument("--copy", action="store_true", help="Copy files to the image (default is to extract)")
    parser.add_argument("--init", default=True, action="store_true", help="Initialize a new disk image")
    parser.add_argument("--drives", type=int, default=16, help="Number of drives for new image (1-16, default 16)")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing image")
    parser.add_argument("--hex-path", default=DEFAULT_HEX_PATH, help=f"Base path for hex files (default: {DEFAULT_HEX_PATH})")
    parser.add_argument("--cpm", default=DEFAULT_CPM_HEX, help=f"Path to CP/M hex file (default: {DEFAULT_CPM_HEX})")
    parser.add_argument("--cbios", default=DEFAULT_CBIOS_HEX, help=f"Path to CBIOS hex file (default: {DEFAULT_CBIOS_HEX})")
    args = parser.parse_args()

    # Update hex file paths if hex-path is provided
    if args.hex_path != DEFAULT_HEX_PATH:
        if args.cpm == DEFAULT_CPM_HEX:
            args.cpm = os.path.join(args.hex_path, "cpm22.hex")
        if args.cbios == DEFAULT_CBIOS_HEX:
            args.cbios = os.path.join(args.hex_path, "cbios128.hex")

    # Print debug information
    print("\nDebug Information:")
    print(f"Hex Path: {args.hex_path}")
    print(f"Current Directory: {os.getcwd()}")

    # Normalize paths
    args.hex_path = os.path.normpath(args.hex_path)
    print(f"Normalized Hex Path: {args.hex_path}")
    print(f"CPM Path: {args.cpm}")
    print(f"CBIOS Path: {args.cbios}")

    # Verify the paths exist
    print("\nPath Verification:")
    print(f"Hex directory exists: {os.path.exists(args.hex_path)}")
    print(f"CPM file exists: {os.path.exists(args.cpm)}")
    print(f"CBIOS file exists: {os.path.exists(args.cbios)}")

    # Handle initialization
    if args.init:
        if args.drives < 1 or args.drives > 16:
            print("Error: Number of drives must be between 1 and 16")
            return

        # Check if hex files exist at the specified locations
        if not os.path.exists(args.cpm):
            print(f"Warning: CP/M hex file not found at {args.cpm}")
            if not args.force:
                response = input("Continue without CP/M? (y/N) ").lower()
                if response != 'y':
                    print("Operation cancelled.")
                    return
            args.cpm = None
            
        if not os.path.exists(args.cbios):
            print(f"Warning: CBIOS hex file not found at {args.cbios}")
            if not args.force:
                response = input("Continue without CBIOS? (y/N) ").lower()
                if response != 'y':
                    print("Operation cancelled.")
                    return
            args.cbios = None

        # Read hex files
        cpm_hex = None
        if args.cpm:
            try:
                with open(args.cpm, 'r') as f:
                    cpm_hex = f.read()
            except OSError as e:
                print(f"Error reading CP/M hex file: {e}")
                if not args.force:
                    return

        cbios_hex = None
        if args.cbios:
            try:
                with open(args.cbios, 'r') as f:
                    cbios_hex = f.read()
            except OSError as e:
                print(f"Error reading CBIOS hex file: {e}")
                if not args.force:
                    return

        # Create the disk image
        if os.path.exists(args.image) and not args.force:
            response = input(f"File {args.image} exists. Overwrite? (y/N) ").lower()
            if response != 'y':
                print("Operation cancelled.")
                return

        print("\nInitializing disk image with:")
        print(f"Number of drives: {args.drives}")
        print(f"CP/M file: {args.cpm}")
        print(f"CBIOS file: {args.cbios}")
        
        create_blank_disk_image(args.image, args.drives, cpm_hex, cbios_hex)
    else:
        print("No operation specified. Use --init to create a new disk image.")

if __name__ == "__main__":
    main()