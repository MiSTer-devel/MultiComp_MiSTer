#!/usr/bin/env python3
# Direct port of the original Perl script
# Usage: python hex_addr_remap.py <hex-offset> foo.hex > foo2.hex
import sys
import re

# Check arguments
if len(sys.argv) != 3:
    print("Usage: python hex_addr_remap.py <hex-offset> <input-file>")
    sys.exit(1)

offset = int(sys.argv[1], 16)  # Convert hex string to integer

try:
    with open(sys.argv[2], 'r') as infile:
        for line in infile:
            # Match the same pattern as the Perl script
            match = re.match(r'(\:)([0-9A-F][0-9A-F])([0-9A-F]{4})([0-9A-F][0-9A-F])(\w+)', line.upper())
            if match:
                # Extract components exactly as in Perl
                len_hex = int(match.group(2), 16)  # 2 digits
                adr = int(match.group(3), 16)      # 4 digits
                typ = int(match.group(4), 16)      # 2 digits
                dat = match.group(5)               # data and checksum
                char = len(dat)

                # Adjust address
                adr = 0xffff & (adr - offset)

                # Calculate sum as in original
                sum_val = len_hex + (adr & 0xff) + ((adr>>8) & 0xff) + typ

                # Build output string
                output = f":{len_hex:02X}{adr:04X}{typ:02X}"

                # Process data bytes
                for i in range(0, char-2, 2):
                    hex_val = dat[i:i+2]
                    output += f"{int(hex_val, 16):02X}"
                    sum_val = sum_val + int(hex_val, 16)

                # Calculate and append new checksum
                new_csum = ((sum_val ^ 0xff) + 1) & 0xff
                output += f"{new_csum:02X}"

                # Print with single \r
                sys.stdout.write(output + "\r")
                
        # Add EOF record at the end
        sys.stdout.write(":00000001FF\r")

except FileNotFoundError:
    print(f"Could not open input file {sys.argv[2]}")
    sys.exit(1)