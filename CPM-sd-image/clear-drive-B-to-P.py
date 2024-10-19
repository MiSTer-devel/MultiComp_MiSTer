import os
import sys

def clear_drive(f, drive_offset, drive_size):
    # Clear directory entries
    f.seek(drive_offset)
    empty_dir_entry = b'\xE5' * 32  # CP/M uses 0xE5 to mark unused directory entries
    for _ in range(512):  # 512 directory entries per drive
        f.write(empty_dir_entry)
    
    # Zero out the rest of the drive
    remaining_size = drive_size - (32 * 512)
    f.write(b'\x00' * remaining_size)

def zero_drives_and_clear_directories(image_path, start_drive='B', end_drive='P'):
    drive_size = 8 * 1024 * 1024  # 8 MB per drive

    with open(image_path, 'r+b') as f:
        for drive in range(ord(start_drive), ord(end_drive) + 1):
            drive_offset = (drive - ord('A')) * drive_size
            clear_drive(f, drive_offset, drive_size)

if __name__ == "__main__":
    image_path = "cpm.img"  # Corrected default image file name
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        sys.exit(1)
    
    zero_drives_and_clear_directories(image_path)
    print(f"Drives B through P in {image_path} have been cleared and zeroed.")