# CP/M 2.2 System Utilities included in cpm.img in the cpm.zip

The following utilities are included in the CP/M disk image:

## ASM.COM
The standard CP/M 8080 assembler. Translates 8080 assembly language source files (.ASM) into Intel HEX format object files (.HEX). Requires source files to be formatted as CP/M text files with line numbers.

## DDT.COM
Dynamic Debugging Tool - an interactive debugger and machine code monitor. Allows examination and modification of memory, setting breakpoints, and single-step program execution. Essential for program development and debugging.

## DISPLAY.COM
Used to display the contents of files on the console. Unlike TYPE, it can handle binary files by showing both ASCII and hexadecimal representations of file contents.

## DOWNLOAD.COM
Utility for receiving files over a serial connection. Used to transfer files from a host system to the CP/M system, typically using protocols like XMODEM.

## DUMP.COM
Displays file contents in hexadecimal format. Similar to DISPLAY but focused on hexadecimal output. Useful for examining binary files and debugging program data.

## ED.COM
The standard CP/M text editor. A line-oriented editor used for creating and modifying text files, including assembly language source code. Basic but functional for program development.

## LOAD.COM
Converts Intel HEX format files (.HEX) produced by ASM.COM into executable CP/M command files (.COM). Essential part of the program development toolchain.

## PIP.COM
Peripheral Interchange Program - the standard CP/M file copy utility. Can copy files between drives, combine files, and transfer data to/from peripheral devices. The Swiss Army knife of CP/M file operations.

## STAT.COM
Displays disk and file status information. Shows disk space usage, file sizes, and attributes. Can also be used to modify file attributes and assign logical devices.

## SUBMIT.COM
Batch file processor. Executes a series of CP/M commands from a text file, allowing automation of repetitive tasks. Similar in concept to DOS batch files or shell scripts.