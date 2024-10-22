import os
import struct
import argparse
from typing import List, Tuple

# Constants based on the provided specifications
DRIVES = 16  # A: to P:
DRIVE_SIZE_MB = 8
BLOCK_SIZE = 4096
DIRECTORY_ENTRIES_PER_DRIVE = 512
CPM_SECTOR_SIZE = 128
BLOCKS_PER_EXTENT = 16
SD_SECTOR_SIZE = 512
BLOCKED_SECTORS_PER_TRACK = 32
TRACKS_PER_DRIVE = 512
BLOCKS_PER_ENTRY = 8
RESERVED_BLOCKS = 4  # File data starts at block 4
UNUSED_DIR_MARKER = 0xE5  # Marker for unused directory entries
UNUSED_DATA_MARKER = 0x00  # Marker for unused data blocks

# Default values
DEFAULT_IMAGE_FILE = "cpm.img"
DEFAULT_TO_DIR = "to_img"
DEFAULT_FROM_DIR = "from_img"

def get_drive_offset(drive_index: int) -> int:
    if drive_index == 0:  # Drive A
        return 0x4000  # Correct offset for drive A directory
    return drive_index * DRIVE_SIZE_MB * 1024 * 1024

def read_directory(image_file: str, drive_index: int) -> List[Tuple[str, int, List[int], int, int]]:
    """
    Read directory entries, handling 16-bit block numbers.
    Returns list of tuples: (filename, user_number, block_list, extent, record_count)
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
            extent = struct.unpack('<H', entry[12:14])[0]
            s1 = entry[14]
            record_count = entry[15]
            
            # Read block numbers as 16-bit values
            blocks = []
            block_data = entry[16:32]  # 16 bytes for block allocation
            for i in range(0, 16, 2):  # Process 2 bytes at a time
                block_number = struct.unpack('<H', block_data[i:i+2])[0]
                if block_number != 0:  # Only include non-zero blocks
                    blocks.append(block_number)
            
            directory.append((full_name, user_number, blocks, extent, record_count))
    
    return directory

def calculate_needed_blocks(content_length: int) -> int:
    """
    Calculate number of blocks needed for a given content length.
    Even empty files need at least one block in CP/M.
    """
    return max(1, (content_length + BLOCK_SIZE - 1) // BLOCK_SIZE)

def find_free_blocks(image_file: str, drive_index: int, blocks_needed: int) -> List[int]:
    """Find consecutive free blocks for file allocation"""
    if blocks_needed > 16:
        raise Exception("File too large - CP/M allows maximum 16 blocks per extent")
    
    if blocks_needed < 1:
        raise Exception("Invalid blocks_needed value - must be at least 1")
        
    # Calculate total blocks in 8MB drive
    drive_size_blocks = (DRIVE_SIZE_MB * 1024 * 1024) // BLOCK_SIZE  # This gives us 2048 blocks for 8MB
    
    # Create block allocation map
    block_map = bytearray(drive_size_blocks)
    
    # Mark used blocks in allocation map
    offset = get_drive_offset(drive_index)
    with open(image_file, 'rb') as f:
        directory = read_directory(image_file, drive_index)
        for _, _, blocks, _, _ in directory:
            for block in blocks:
                if block != 0 and block < drive_size_blocks:
                    block_map[block] = 1

    # Find free blocks - try to allocate consecutively first
    consecutive_count = 0
    start_block = None

    # Start searching from reserved blocks
    for block in range(RESERVED_BLOCKS, drive_size_blocks):
        if not block_map[block]:
            if consecutive_count == 0:
                start_block = block
            consecutive_count += 1
            if consecutive_count == blocks_needed:
                return list(range(start_block, start_block + blocks_needed))
        else:
            consecutive_count = 0
            start_block = None

    # If we can't find consecutive blocks, fall back to non-consecutive allocation
    free_blocks = []
    for block in range(RESERVED_BLOCKS, drive_size_blocks):
        if not block_map[block]:
            free_blocks.append(block)
            if len(free_blocks) == blocks_needed:
                return free_blocks

    raise Exception(f"Not enough free blocks. Available: {len(free_blocks)}, needed: {blocks_needed}")

def write_file(image_file: str, drive_index: int, filename: str, user: int, content: bytes):
    """Write a file to the CP/M image, splitting across multiple extents if needed"""
    offset = get_drive_offset(drive_index)
    total_size = len(content)
    bytes_per_extent = BLOCKS_PER_EXTENT * BLOCK_SIZE
    num_extents = (total_size + bytes_per_extent - 1) // bytes_per_extent
    
    name, ext = os.path.splitext(filename)
    name = name.ljust(8)[:8]
    ext = ext[1:].ljust(3)[:3]
    
    for extent_num in range(num_extents):
        # Calculate content for this extent
        start_pos = extent_num * bytes_per_extent
        end_pos = min(start_pos + bytes_per_extent, total_size)
        extent_content = content[start_pos:end_pos]
        
        # Calculate blocks needed for this extent
        blocks_needed = calculate_needed_blocks(len(extent_content))
        blocks_needed = min(blocks_needed, BLOCKS_PER_EXTENT)
        
        # Find free blocks for this extent
        free_blocks = find_free_blocks(image_file, drive_index, blocks_needed)
        
        # Find free directory entry
        with open(image_file, 'r+b') as f:
            f.seek(offset)
            dir_entry_found = False
            for i in range(DIRECTORY_ENTRIES_PER_DRIVE):
                entry = f.read(32)
                if entry[0] == UNUSED_DIR_MARKER:
                    f.seek(offset + i * 32)
                    dir_entry_found = True
                    break
            
            if not dir_entry_found:
                raise Exception("No free directory entries")
            
            # Write directory entry
            f.write(bytes([user]))  # User number
            f.write(name.encode('ascii'))  # Filename
            f.write(ext.encode('ascii'))  # Extension
            f.write(struct.pack('<H', extent_num))  # Extent number
            f.write(b'\x00')  # S1
            
            # Calculate record count for this extent
            if len(extent_content) == 0:
                record_count = 0
            else:
                record_count = min(128, (len(extent_content) + CPM_SECTOR_SIZE - 1) // CPM_SECTOR_SIZE)
            f.write(bytes([record_count]))
            
            # Write block allocation
            block_data = bytearray(16)  # 16 bytes for block allocation
            for i, block in enumerate(free_blocks):
                if i < 8:  # CP/M supports up to 8 blocks per extent
                    struct.pack_into('<H', block_data, i * 2, block)
            f.write(block_data)
            
            # Write file content to allocated blocks
            for i, block in enumerate(free_blocks):
                block_offset = offset + block * BLOCK_SIZE
                f.seek(block_offset)
                content_start = i * BLOCK_SIZE
                content_end = min((i + 1) * BLOCK_SIZE, len(extent_content))
                block_content = extent_content[content_start:content_end]
                
                # Pad the last block
                if len(block_content) < BLOCK_SIZE:
                    block_content = block_content + bytes([UNUSED_DATA_MARKER] * (BLOCK_SIZE - len(block_content)))
                f.write(block_content)
            
def extract_file(image_file: str, drive_index: int, filename: str, user: int, blocks: List[int], extent: int, record_count: int) -> bytes:
    """Extract file content for a specific extent"""
    drive_offset = get_drive_offset(drive_index)
    content = b''
    
    with open(image_file, 'rb') as f:
        for block in blocks:
            if block == 0:
                break
            block_offset = drive_offset + block * BLOCK_SIZE
            f.seek(block_offset)
            content += f.read(BLOCK_SIZE)
    
    # Trim content based on record count
    if record_count > 0:
        return content[:record_count * CPM_SECTOR_SIZE]
    return content

def copy_files_to_image(image_file: str, source_dir: str, drive_letter: str, drive_index: int):
    for user in range(16):  # Users 0-15
        user_dir = os.path.join(source_dir, drive_letter, str(user))
        if not os.path.exists(user_dir):
            continue
        for filename in os.listdir(user_dir):
            with open(os.path.join(user_dir, filename), 'rb') as f:
                content = f.read()
            write_file(image_file, drive_index, filename, user, content)

def copy_files_from_image(image_file: str, target_dir: str):
    """Modified to handle multiple extents per file"""
    for drive_index, drive_letter in enumerate('ABCDEFGHIJKLMNOP'):
        print(f"Extracting files from drive {drive_letter}...")
        directory = read_directory(image_file, drive_index)
        
        # Group entries by filename and user number
        files = {}
        for filename, user, blocks, extent, record_count in directory:
            key = (filename, user)
            if key not in files:
                files[key] = []
            files[key].append((extent, blocks, record_count))
        
        # Process each file
        for (filename, user), extents in files.items():
            # Sort extents by extent number
            extents.sort(key=lambda x: x[0])
            
            # Combine content from all extents
            complete_content = b''
            for extent, blocks, record_count in extents:
                content = extract_file(image_file, drive_index, filename, user, blocks, extent, record_count)
                complete_content += content
            
            # Write the complete file
            user_dir = os.path.join(target_dir, drive_letter, str(user))
            os.makedirs(user_dir, exist_ok=True)
            with open(os.path.join(user_dir, filename), 'wb') as f:
                f.write(complete_content)
        
        print(f"Extracted {len(files)} files from drive {drive_letter}")

def main():
    parser = argparse.ArgumentParser(description="Extract files from or copy files to CP/M disk image")
    parser.add_argument("--image", default=DEFAULT_IMAGE_FILE, help=f"CP/M disk image file (default: {DEFAULT_IMAGE_FILE})")
    parser.add_argument("--to", default=DEFAULT_TO_DIR, help=f"Source directory for files to copy to image (default: {DEFAULT_TO_DIR})")
    parser.add_argument("--from", dest="from_dir", default=DEFAULT_FROM_DIR, help=f"Target directory for extracted files (default: {DEFAULT_FROM_DIR})")
    parser.add_argument("--copy", default='--copy', action="store_true", help="Copy files to the image (default is to extract)")
#    parser.add_argument("--copy", action="store_true", help="Copy files to the image (default is to extract)")
    args = parser.parse_args()

    if args.copy:
        for drive_index, drive_letter in enumerate('ABCDEFGHIJKLMNOP'):
            print(f"Copying files for drive {drive_letter}...")
            copy_files_to_image(args.image, args.to, drive_letter, drive_index)
            input("Press Enter to continue to the next drive...")
    else:
        copy_files_from_image(args.image, args.from_dir)

if __name__ == "__main__":
    main()