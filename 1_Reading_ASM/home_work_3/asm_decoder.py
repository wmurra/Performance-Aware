from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from pathlib import Path

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
PINK = "\033[35m"
RESET = "\033[0m"

FIRST_MOV = [(RED, 6), (BLUE, 7), (RESET, 8), (GREEN, 10), (YELLOW, 12), (PINK, 15)]
IMMEDIATE = [(BLUE, 4), (YELLOW, 5), (RESET, 8), (PINK, 10)]
IMMEDIATE_REG_MEM_MOV = [(BLUE, 7), (RESET, 8), (GREEN, 10), (YELLOW, 12), (PINK, 15)]
ACCUMULATOR_MOV = [(BLUE, 7), (RESET, 8), (PINK, 10)]

REGISTER_MODE_WORD = {
    '000':'ax',
    '001':'cx',
    '010':'dx',
    '011':'bx',
    '100':'sp',
    '101':'bp',
    '110':'si',
    '111':'di',
}
REGISTER_MODE_BYTE = {
    '000':'al',
    '001':'cl',
    '010':'dl',
    '011':'bl',
    '100':'ah',
    '101':'ch',
    '110':'dh',
    '111':'bh',
}
MEMORY_MODE = {
    '000':('bx','si'),
    '001':('bx', 'di'),
    '010':('bp', 'si'),
    '011':('bp', 'di'),
    '100':('si'),
    '101':('di'),
    '110':('bp'),
    '111':('bx'),
}

def string_insert(original:str, substring:str, index:int):
    return original[:index] + substring + original[index:]

class Opcode(Enum):
    UNKNOWN = 0
    MOV = 1
    ADD = 2
    SUB = 3
    CMP = 4
    JZN = 5

# OPCODE_TABLE = {
#     "100010": Opcode.MOV, 
#     "1011": Opcode.MOV,
#     "000000": Opcode.ADD, 
#     "0000010": Opcode.ADD,
#     "001010": Opcode.SUB,
#     "001110": Opcode.CMP,
#     "001110": Opcode.CMP,
# }
OPCODE_TABLE = {
    "101": Opcode.SUB, 
    "000": Opcode.ADD,
    "000000": Opcode.ADD, 
    "0000010": Opcode.ADD,
    "001010": Opcode.SUB,
    "001110": Opcode.CMP,
    "001110": Opcode.CMP,
}

@dataclass
class Instruction:
    opcode: Opcode
    args: list[str]
    literal_bytes: bytes
    formatted_bytes: str = ''
    
    def __str__(self):
       return f"{self.opcode.name.lower()} {', '.join(self.args)}"
    
    def debug_repr(self):
        binary_content = ' '.join(format(byte, '08b') for byte in self.literal_bytes)
        binary_content_len = len(binary_content)
        if self.formatted_bytes:
            binary_content = self.formatted_bytes
        content_len = len(self.__str__()) + binary_content_len
        padding = 85 - content_len
        return f"{self.__str__()} {' ' * padding}{binary_content}"

class Decoder:
    def __init__(self, bin:bytes):
        self._bin = bin
        self.asm_instructions: list[Instruction] = []
        self._current = 0
        self._at_end: bool = False

    def get_current_byte(self) -> bytes:
        return self._bin[self._current]

    def _advance(self) -> str:
        val = self.get_current_byte()
        self._current += 1
        return format(val, '08b')

    def _is_at_end(self):
       return self._current >= len(self._bin)
    
    @property
    def this_byte(self):
        return format(self._bin[self._current], '08b')
    
    def byte_formatter(self, raw_bytes, style: list[tuple[str, int]]):
        bytes_as_string = ', '.join(format(byte, '08b') for byte in raw_bytes)
        offset = 0
        for style_step in style:
            index = style_step[1]+offset
            color = style_step[0]
            bytes_as_string = string_insert(bytes_as_string, style_step[0], index)
            offset += len(color)
        return bytes_as_string + RESET

    def add_instruction(self, opcode: Opcode, args, style:list[tuple[str, int]] = None):
        args = [str(arg) for arg in args]
        literal_bytes = self._bin[self._start:self._current] # AKA lexeme

        formatted_bytes = ''
        if style:
            formatted_bytes = self.byte_formatter(literal_bytes, style)
        self.asm_instructions.append(Instruction(opcode, args, literal_bytes, formatted_bytes))

    def bytes_to_int(self, *bytes_as_str) -> int:
        bytes_as_str = reversed(bytes_as_str)
        long_str = ''.join(bytes_as_str)
        bit_width = len(long_str)
        unsigned_value = int(long_str, 2)
        if unsigned_value & (1 << (bit_width - 1)):
            # two's complement value for signed number
            signed_value = unsigned_value - (1 << bit_width)
        else:
            signed_value = unsigned_value
        
        return signed_value
    
    def mod_reg_rm(self):
        direction = bool(int(self.this_byte[6]))
        wide = bool(int(self.this_byte[7]))
        second_byte = self._advance() # first 2 bytes are required
        mode = second_byte[:2]
        reg_code = second_byte[2:5]
        rm_code = second_byte[5:]
        displacement = 0
        rm = MEMORY_MODE[rm_code][:]
        if mode == '00':
            if rm_code == '110': # I think this is a solution
                rm = tuple()
                displacement = self.bytes_to_int(self._advance(), self._advance())
        if mode == '01': # Memory Mode: 8-bit displacement
            displacement = self.bytes_to_int(self._advance())
        elif mode == '10': # Memory Mode: 16-bit displacement
            displacement = self.bytes_to_int(self._advance(), self._advance())
        
        if isinstance(rm, tuple):
            if displacement:
                rm = rm + (displacement,)
            rm = '[' + ' + '.join(str(operand) for operand in rm) + ']'
        else:
            if displacement:
                rm = f"{rm} + {displacement}"
            rm = '[' + rm + ']'
        if mode == '11': # Register Mode: No displacement
            if wide:
                rm = REGISTER_MODE_WORD[rm_code]
            else:
                rm = REGISTER_MODE_BYTE[rm_code]

        if wide:
            reg = REGISTER_MODE_WORD[reg_code]
        else:
            reg = REGISTER_MODE_BYTE[reg_code]
        
        rm = rm.replace('+ -', '- ')
        args = [reg, rm]
        if not direction:
            args = reversed(args)
        return args, reg_code

    def immediate_parse(self):
        wide = bool(int(self.this_byte[4]))
        if wide:
            dest = REGISTER_MODE_WORD[self.this_byte[5:]]
            value = self.bytes_to_int(self._advance(), self._advance())
        else:
            dest = REGISTER_MODE_BYTE[self.this_byte[5:]]
            value = self.bytes_to_int(self._advance())
        return [dest, value]
    
    def immediate_to_accumulator(self):
        wide = bool(int(self.this_byte[7]))
        if wide:
            address = str(self.bytes_to_int(self._advance(), self._advance()))
            address = '[' + address + ']'
        else:
            address = str(self.bytes_to_int(self._advance()))
            address = '[' + address + ']'
        return address

            
    def scan_instruction(self):
        first_byte = self._advance()
        if first_byte[:6] in ["100010", "000000", "000110", "001110"]:
            args, reg = self.mod_reg_rm()

            self.add_instruction(OPCODE_TABLE.get(reg, Opcode.UNKNOWN), args, FIRST_MOV)

        elif first_byte[:4] in ["1011"]:
            args = self.immediate_parse()
            self.add_instruction(OPCODE_TABLE.get(first_byte[:4], Opcode.UNKNOWN), args, IMMEDIATE)
        
        elif first_byte[:7] in ["0000010"]:
            args = self.immediate_to_accumulator()
            self.add_instruction(OPCODE_TABLE.get(first_byte[:7], Opcode.UNKNOWN), args, IMMEDIATE)

        elif first_byte[:7] == "1100011": # MOV Immediate to register / Memory
            wide = bool(int(first_byte[7]))
            second_byte = self._advance()
            mode_code = second_byte[:2]
            rm_code = second_byte[5:]
            displacement = 0
            rm = MEMORY_MODE[rm_code][:]

            if mode_code == '00':
                if rm_code == '110': # I think this is a solution
                    displacement = self.bytes_to_int(self._advance(), self._advance())
            if mode_code == '01': # Memory Mode: 8-bit displacement
                displacement = self.bytes_to_int(self._advance())
            elif mode_code == '10': # Memory Mode: 16-bit displacement
                displacement = self.bytes_to_int(self._advance(), self._advance())

            if isinstance(rm, tuple):
                if displacement:
                    rm = rm + (displacement,)
                rm = '[' + ' + '.join(str(operand) for operand in rm) + ']'
            else:
                if displacement:
                    rm = f"{rm} + {displacement}"
                rm = '[' + rm + ']'

            if mode_code == '11': # Register Mode: No displacement
                if wide:
                    rm = REGISTER_MODE_WORD[rm_code]
                else:
                    rm = REGISTER_MODE_BYTE[rm_code]

            if wide:
                value = 'word ' + str(self.bytes_to_int(self._advance(), self._advance()))
            else:
                value = 'byte ' + str(self.bytes_to_int(self._advance()))


            self.add_instruction(Opcode.MOV, [rm, value], IMMEDIATE_REG_MEM_MOV)
        
        elif first_byte[:7] in ["1010000", "1010001"]: # MOV Memory to accumulator
            wide = bool(int(first_byte[7]))
            if wide:
                register = 'ax'
                address = str(self.bytes_to_int(self._advance(), self._advance()))
                address = '[' + address + ']'
            else:
                register = 'al'
                address = self.bytes_to_int(self._advance())
                address = '[' + address + ']'
            
            if first_byte[:7] == "1010000":
                args = [register, address]
            elif first_byte[:7] == "1010001":
                args = [address, register]
                
            self.add_instruction(Opcode.MOV, args, ACCUMULATOR_MOV)

        
        elif first_byte[:6] == "0000000": # ADD Reg/Memory w/ register to either
            wide = bool(int(first_byte[7]))
            if wide:
                register = 'ax'
                address = str(self.bytes_to_int(self._advance(), self._advance()))
                address = '[' + address + ']'
            else:
                register = 'al'
                address = self.bytes_to_int(self._advance())
                address = '[' + address + ']'
            
            if first_byte[:7] == "1010000":
                args = [register, address]
            elif first_byte[:7] == "1010001":
                args = [address, register]
                
            self.add_instruction(Opcode.MOV, args, ACCUMULATOR_MOV)

        else:
            self.add_instruction(Opcode.UNKNOWN, ['?', '?'])

    def scan_instructions(self):
        while not self._is_at_end():
            self._start = self._current
            self.scan_instruction()
        return self.asm_instructions

bin_path_as_str = Path("listing_0041_add_sub_cmp_jnz")  # Replace with the path to your file
bin_path_as_str = Path("listing_0040_challenge_movs")  # Replace with the path to your file

try:
    with Path(bin_path_as_str).open('rb') as f:
        bin = f.read()
        decoder = Decoder(bin)
        instructions = decoder.scan_instructions()
        for instruction in instructions:
            print(instruction.debug_repr())
except FileNotFoundError:
        print(f"Error: File not found at {bin_path_as_str}")
# except Exception as e:
#     print(f"An error occurred: {e}")
