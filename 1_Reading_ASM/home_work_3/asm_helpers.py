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
MYSTERY = [(RED, 0)]

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

OPCODE_TABLE = {
    
    "100010": Opcode.MOV, 
    "1100011": Opcode.MOV,
    "101000": Opcode.MOV,
    "1011": Opcode.MOV,
    
    "000000": Opcode.ADD, 
    "0000010": Opcode.ADD,
    "100000": Opcode.ADD,

    "001010": Opcode.SUB,
    "100000": Opcode.SUB,
    "0010110": Opcode.SUB,
    
    "001110": Opcode.CMP,
    "001110": Opcode.CMP,
    "0011110": Opcode.CMP,
    
}
reg_opcode_table = {
    "000": Opcode.ADD,
    "101": Opcode.SUB,
    "111": Opcode.CMP,

}
class OpCodes:
    def __init__(self):
        self.table = OPCODE_TABLE
    
    def get(self, opcode_name):
        return self.table.get(opcode_name, Opcode.UNKNOWN)
    
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

def byte_formatter(raw_bytes, style: list[tuple[str, int]]):
    bytes_as_string = ', '.join(format(byte, '08b') for byte in raw_bytes)
    offset = 0
    for style_step in style:
        index = style_step[1]+offset
        color = style_step[0]
        bytes_as_string = string_insert(bytes_as_string, style_step[0], index)
        offset += len(color)
    return bytes_as_string + RESET

def bytes_to_int(*bytes_as_str) -> int:
    if not bytes_as_str:
        return -808080808
    bytes_as_str = reversed((bytes_as_str))
    long_str = ''.join(bytes_as_str)
    bit_width = len(long_str)
    unsigned_value = int(long_str, 2)
    if unsigned_value & (1 << (bit_width - 1)):
        # two's complement value for signed number
        signed_value = unsigned_value - (1 << bit_width)
    else:
        signed_value = unsigned_value
    
    return signed_value

