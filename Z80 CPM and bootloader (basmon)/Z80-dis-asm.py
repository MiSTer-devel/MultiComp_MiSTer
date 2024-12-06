import sys
from typing import Dict, List, Tuple

class Z80Disassembler:
    def __init__(self):
        # Complete Z80 instruction set
        self.instructions = {
            # 8-bit load group
            0x40: ("LD B,B", 1),
            0x41: ("LD B,C", 1),
            0x42: ("LD B,D", 1),
            0x43: ("LD B,E", 1),
            0x44: ("LD B,H", 1),
            0x45: ("LD B,L", 1),
            0x46: ("LD B,(HL)", 1),
            0x47: ("LD B,A", 1),
            0x48: ("LD C,B", 1),
            0x49: ("LD C,C", 1),
            0x4A: ("LD C,D", 1),
            0x4B: ("LD C,E", 1),
            0x4C: ("LD C,H", 1),
            0x4D: ("LD C,L", 1),
            0x4E: ("LD C,(HL)", 1),
            0x4F: ("LD C,A", 1),
            0x50: ("LD D,B", 1),
            0x51: ("LD D,C", 1),
            0x52: ("LD D,D", 1),
            0x53: ("LD D,E", 1),
            0x54: ("LD D,H", 1),
            0x55: ("LD D,L", 1),
            0x56: ("LD D,(HL)", 1),
            0x57: ("LD D,A", 1),
            0x58: ("LD E,B", 1),
            0x59: ("LD E,C", 1),
            0x5A: ("LD E,D", 1),
            0x5B: ("LD E,E", 1),
            0x5C: ("LD E,H", 1),
            0x5D: ("LD E,L", 1),
            0x5E: ("LD E,(HL)", 1),
            0x5F: ("LD E,A", 1),
            0x60: ("LD H,B", 1),
            0x61: ("LD H,C", 1),
            0x62: ("LD H,D", 1),
            0x63: ("LD H,E", 1),
            0x64: ("LD H,H", 1),
            0x65: ("LD H,L", 1),
            0x66: ("LD H,(HL)", 1),
            0x67: ("LD H,A", 1),
            0x68: ("LD L,B", 1),
            0x69: ("LD L,C", 1),
            0x6A: ("LD L,D", 1),
            0x6B: ("LD L,E", 1),
            0x6C: ("LD L,H", 1),
            0x6D: ("LD L,L", 1),
            0x6E: ("LD L,(HL)", 1),
            0x6F: ("LD L,A", 1),
            0x70: ("LD (HL),B", 1),
            0x71: ("LD (HL),C", 1),
            0x72: ("LD (HL),D", 1),
            0x73: ("LD (HL),E", 1),
            0x74: ("LD (HL),H", 1),
            0x75: ("LD (HL),L", 1),
            0x76: ("HALT", 1),
            0x77: ("LD (HL),A", 1),
            0x78: ("LD A,B", 1),
            0x79: ("LD A,C", 1),
            0x7A: ("LD A,D", 1),
            0x7B: ("LD A,E", 1),
            0x7C: ("LD A,H", 1),
            0x7D: ("LD A,L", 1),
            0x7E: ("LD A,(HL)", 1),
            0x7F: ("LD A,A", 1),

            # 16-bit load group
            0x01: ("LD BC,", 3),
            0x11: ("LD DE,", 3),
            0x21: ("LD HL,", 3),
            0x31: ("LD SP,", 3),
            0x2A: ("LD HL,(", 3),
            0x22: ("LD (", 3),  # LD (nn),HL
            0xF9: ("LD SP,HL", 1),
            0xC5: ("PUSH BC", 1),
            0xD5: ("PUSH DE", 1),
            0xE5: ("PUSH HL", 1),
            0xF5: ("PUSH AF", 1),
            0xC1: ("POP BC", 1),
            0xD1: ("POP DE", 1),
            0xE1: ("POP HL", 1),
            0xF1: ("POP AF", 1),

            # Exchange group
            0xEB: ("EX DE,HL", 1),
            0x08: ("EX AF,AF'", 1),
            0xE3: ("EX (SP),HL", 1),
            0xD9: ("EXX", 1),

            # 8-bit arithmetic/logical group
            0x80: ("ADD A,B", 1),
            0x81: ("ADD A,C", 1),
            0x82: ("ADD A,D", 1),
            0x83: ("ADD A,E", 1),
            0x84: ("ADD A,H", 1),
            0x85: ("ADD A,L", 1),
            0x86: ("ADD A,(HL)", 1),
            0x87: ("ADD A,A", 1),
            0x88: ("ADC A,B", 1),
            0x89: ("ADC A,C", 1),
            0x8A: ("ADC A,D", 1),
            0x8B: ("ADC A,E", 1),
            0x8C: ("ADC A,H", 1),
            0x8D: ("ADC A,L", 1),
            0x8E: ("ADC A,(HL)", 1),
            0x8F: ("ADC A,A", 1),
            0x90: ("SUB B", 1),
            0x91: ("SUB C", 1),
            0x92: ("SUB D", 1),
            0x93: ("SUB E", 1),
            0x94: ("SUB H", 1),
            0x95: ("SUB L", 1),
            0x96: ("SUB (HL)", 1),
            0x97: ("SUB A", 1),
            0x98: ("SBC A,B", 1),
            0x99: ("SBC A,C", 1),
            0x9A: ("SBC A,D", 1),
            0x9B: ("SBC A,E", 1),
            0x9C: ("SBC A,H", 1),
            0x9D: ("SBC A,L", 1),
            0x9E: ("SBC A,(HL)", 1),
            0x9F: ("SBC A,A", 1),
            0xA0: ("AND B", 1),
            0xA1: ("AND C", 1),
            0xA2: ("AND D", 1),
            0xA3: ("AND E", 1),
            0xA4: ("AND H", 1),
            0xA5: ("AND L", 1),
            0xA6: ("AND (HL)", 1),
            0xA7: ("AND A", 1),
            0xA8: ("XOR B", 1),
            0xA9: ("XOR C", 1),
            0xAA: ("XOR D", 1),
            0xAB: ("XOR E", 1),
            0xAC: ("XOR H", 1),
            0xAD: ("XOR L", 1),
            0xAE: ("XOR (HL)", 1),
            0xAF: ("XOR A", 1),
            0xB0: ("OR B", 1),
            0xB1: ("OR C", 1),
            0xB2: ("OR D", 1),
            0xB3: ("OR E", 1),
            0xB4: ("OR H", 1),
            0xB5: ("OR L", 1),
            0xB6: ("OR (HL)", 1),
            0xB7: ("OR A", 1),
            0xB8: ("CP B", 1),
            0xB9: ("CP C", 1),
            0xBA: ("CP D", 1),
            0xBB: ("CP E", 1),
            0xBC: ("CP H", 1),
            0xBD: ("CP L", 1),
            0xBE: ("CP (HL)", 1),
            0xBF: ("CP A", 1),
            0x04: ("INC B", 1),
            0x0C: ("INC C", 1),
            0x14: ("INC D", 1),
            0x1C: ("INC E", 1),
            0x24: ("INC H", 1),
            0x2C: ("INC L", 1),
            0x34: ("INC (HL)", 1),
            0x3C: ("INC A", 1),
            0x05: ("DEC B", 1),
            0x0D: ("DEC C", 1),
            0x15: ("DEC D", 1),
            0x1D: ("DEC E", 1),
            0x25: ("DEC H", 1),
            0x2D: ("DEC L", 1),
            0x35: ("DEC (HL)", 1),
            0x3D: ("DEC A", 1),

            # General purpose arithmetic and control groups
            0x27: ("DAA", 1),
            0x2F: ("CPL", 1),
            0x37: ("SCF", 1),
            0x3F: ("CCF", 1),
            0x00: ("NOP", 1),
            0x76: ("HALT", 1),
            0xF3: ("DI", 1),
            0xFB: ("EI", 1),

            # 16-bit arithmetic group
            0x09: ("ADD HL,BC", 1),
            0x19: ("ADD HL,DE", 1),
            0x29: ("ADD HL,HL", 1),
            0x39: ("ADD HL,SP", 1),
            0x03: ("INC BC", 1),
            0x13: ("INC DE", 1),
            0x23: ("INC HL", 1),
            0x33: ("INC SP", 1),
            0x0B: ("DEC BC", 1),
            0x1B: ("DEC DE", 1),
            0x2B: ("DEC HL", 1),
            0x3B: ("DEC SP", 1),

            # Rotate and shift group
            0x07: ("RLCA", 1),
            0x17: ("RLA", 1),
            0x0F: ("RRCA", 1),
            0x1F: ("RRA", 1),

            # Jump group
            0xC3: ("JP", 3),
            0xDA: ("JP C,", 3),
            0xD2: ("JP NC,", 3),
            0xCA: ("JP Z,", 3),
            0xC2: ("JP NZ,", 3),
            0xFA: ("JP M,", 3),
            0xF2: ("JP P,", 3),
            0xEA: ("JP PE,", 3),
            0xE2: ("JP PO,", 3),
            0x18: ("JR", 2),
            0x38: ("JR C,", 2),
            0x30: ("JR NC,", 2),
            0x28: ("JR Z,", 2),
            0x20: ("JR NZ,", 2),
            0xE9: ("JP (HL)", 1),
            0x10: ("DJNZ", 2),

            # Call and return group
            0xCD: ("CALL", 3),
            0xDC: ("CALL C,", 3),
            0xD4: ("CALL NC,", 3),
            0xCC: ("CALL Z,", 3),
            0xC4: ("CALL NZ,", 3),
            0xFC: ("CALL M,", 3),
            0xF4: ("CALL P,", 3),
            0xEC: ("CALL PE,", 3),
            0xE4: ("CALL PO,", 3),
            0xC9: ("RET", 1),
            0xD8: ("RET C", 1),
            0xD0: ("RET NC", 1),
            0xC8: ("RET Z", 1),
            0xC0: ("RET NZ", 1),
            0xF8: ("RET M", 1),
            0xF0: ("RET P", 1),
            0xE8: ("RET PE", 1),
            0xE0: ("RET PO", 1),
            0xC7: ("RST 00H", 1),
            0xCF: ("RST 08H", 1),
            0xD7: ("RST 10H", 1),
            0xDF: ("RST 18H", 1),
            0xE7: ("RST 20H", 1),
            0xEF: ("RST 28H", 1),
            0xF7: ("RST 30H", 1),
            0xFF: ("RST 38H", 1),

            # Input and output group
            0xDB: ("IN A,(", 2),
            0xD3: ("OUT (", 2),

            # Additional load instructions
            0x3E: ("LD A,", 2),
            0x06: ("LD B,", 2),
            0x0E: ("LD C,", 2),
            0x16: ("LD D,", 2),
            0x1E: ("LD E,", 2),
            0x26: ("LD H,", 2),
            0x2E: ("LD L,", 2),
            0x36: ("LD (HL),", 2),
            0x32: ("LD (", 3),  # LD (nn),A
            0x3A: ("LD A,(", 3),  # LD A,(nn)
        }

    def parse_hex_file(self, hex_content: str) -> Dict[int, int]:
        memory = {}
        for line in hex_content.splitlines():
            if not line.startswith(':'):
                continue
                
            # Remove the starting ':'
            line = line[1:]
            
# Parse the Intel HEX record
            byte_count = int(line[0:2], 16)
            address = int(line[2:6], 16)
            record_type = int(line[6:8], 16)
            data = line[8:8+byte_count*2]
            
            if record_type == 0:  # Data record
                for i in range(0, len(data), 2):
                    byte = int(data[i:i+2], 16)
                    memory[address + (i//2)] = byte
                    
        return memory

    def disassemble(self, memory: Dict[int, int], start_address: int = 0) -> List[str]:
        output = []
        current_address = start_address
        
        while current_address in memory:
            opcode = memory[current_address]
            
            # Check for CB prefix (bit instructions)
            if opcode == 0xCB and (current_address + 1) in memory:
                cb_opcode = memory[current_address + 1]
                instruction = self.decode_cb_instruction(cb_opcode)
                if instruction:
                    output.append(f"{current_address:04X}: {instruction}")
                    current_address += 2
                    continue

            # Check for ED prefix
            if opcode == 0xED and (current_address + 1) in memory:
                ed_opcode = memory[current_address + 1]
                instruction = self.decode_ed_instruction(ed_opcode)
                if instruction:
                    output.append(f"{current_address:04X}: {instruction}")
                    current_address += 2
                    continue

            # Check for DD/FD prefix (IX/IY instructions)
            if opcode in [0xDD, 0xFD]:
                prefix = "IX" if opcode == 0xDD else "IY"
                if (current_address + 1) in memory:
                    ix_opcode = memory[current_address + 1]
                    instruction = self.decode_indexed_instruction(ix_opcode, prefix)
                    if instruction:
                        output.append(f"{current_address:04X}: {instruction}")
                        current_address += 2
                        continue

            instruction_info = self.instructions.get(opcode)
            
            if instruction_info:
                mnemonic, length = instruction_info
                operand_bytes = []
                
                # Get operand bytes if any
                for i in range(1, length):
                    if current_address + i in memory:
                        operand_bytes.append(memory[current_address + i])
                
                # Format the instruction
                if length == 1:
                    line = f"{current_address:04X}: {mnemonic}"
                elif length == 2:
                    if len(operand_bytes) >= 1:
                        line = f"{current_address:04X}: {mnemonic}{operand_bytes[0]:02X}H"
                elif length == 3:
                    if len(operand_bytes) >= 2:
                        value = operand_bytes[0] + (operand_bytes[1] << 8)
                        if mnemonic.endswith("("):
                            line = f"{current_address:04X}: {mnemonic}{value:04X}H),A"
                        else:
                            line = f"{current_address:04X}: {mnemonic}{value:04X}H"
                
                output.append(line)
                current_address += length
            else:
                # Unknown opcode
                output.append(f"{current_address:04X}: DB {opcode:02X}H  ; Unknown opcode")
                current_address += 1
                
        return output

    def decode_cb_instruction(self, opcode: int) -> str:
        """Decode CB-prefixed bit manipulation instructions"""
        op_type = opcode >> 6
        bit_num = (opcode >> 3) & 0x07
        reg = opcode & 0x07
        
        reg_names = ['B', 'C', 'D', 'E', 'H', 'L', '(HL)', 'A']
        
        if op_type == 0:  # Rotates and shifts
            operations = ['RLC', 'RRC', 'RL', 'RR', 'SLA', 'SRA', 'SLL', 'SRL']
            return f"{operations[bit_num]} {reg_names[reg]}"
        elif op_type == 1:  # BIT
            return f"BIT {bit_num},{reg_names[reg]}"
        elif op_type == 2:  # RES
            return f"RES {bit_num},{reg_names[reg]}"
        elif op_type == 3:  # SET
            return f"SET {bit_num},{reg_names[reg]}"
        
        return None

    def decode_ed_instruction(self, opcode: int) -> str:
        """Decode ED-prefixed instructions"""
        ed_instructions = {
            0x40: "IN B,(C)",
            0x41: "OUT (C),B",
            0x42: "SBC HL,BC",
            0x43: "LD (nn),BC",
            0x44: "NEG",
            0x45: "RETN",
            0x46: "IM 0",
            0x47: "LD I,A",
            # Add more ED instructions as needed
        }
        return ed_instructions.get(opcode)

    def decode_indexed_instruction(self, opcode: int, prefix: str) -> str:
        """Decode IX/IY indexed instructions"""
        if opcode == 0x21:  # LD IX/IY,nn
            return f"LD {prefix},"
        elif opcode == 0x22:  # LD (nn),IX/IY
            return f"LD (,{prefix})"
        elif opcode == 0x2A:  # LD IX/IY,(nn)
            return f"LD {prefix},("
        # Add more indexed instructions as needed
        return None

def main(hex_file_path: str):
    try:
        with open(hex_file_path, 'r') as f:
            hex_content = f.read()
            
        disassembler = Z80Disassembler()
        memory = disassembler.parse_hex_file(hex_content)
        disassembly = disassembler.disassemble(memory)
        
        for line in disassembly:
            print(line)
            
    except FileNotFoundError:
        print(f"Error: Could not find file {hex_file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python z80_disassembler.py <hex_file>")
    else:
        main(sys.argv[1])