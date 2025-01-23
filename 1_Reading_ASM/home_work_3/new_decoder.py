from asm_helpers import*

opcode_table = OpCodes()
class Decoder:
    def __init__(self, bin:bytes):
        self._bin = bin
        self.asm_instructions: list[Instruction] = []
        last_byte = ''
        self._current = 0
        self._at_end: bool = False
    
    @property
    def this_byte(self):
        return format(self._bin[self._current], '08b')

    def _advance(self) -> str:
        self.last_byte = self.this_byte
        self._current += 1
        return self.last_byte

    def _is_at_end(self):
       return self._current >= len(self._bin)

    def add_instruction(self, opcode: Opcode, args, style:list[tuple[str, int]] = None):
        args = [str(arg) for arg in args]
        literal_bytes = self._bin[self._start:self._current] # AKA lexeme
        formatted_bytes = ''
        if style:
            formatted_bytes = byte_formatter(literal_bytes, style)
        self.asm_instructions.append(Instruction(opcode, args, literal_bytes, formatted_bytes))
    
    def mod_reg_rm(self, immediate=False, operator=False):
            direction = bool(int(self.last_byte[6]))
            wide = bool(int(self.last_byte[7]))
            second_byte = self._advance()
            mode = second_byte[:2]
            reg_code = second_byte[2:5]
            rm_code = second_byte[5:]
            displacement = 0
            rm = MEMORY_MODE[rm_code][:]

            if mode == '00':
                if rm_code == '110': # I think this is a solution
                    if not immediate:
                        rm = tuple()
                    displacement = bytes_to_int(self._advance(), self._advance())
            if mode == '01': # Memory Mode: 8-bit displacement
                displacement = bytes_to_int(self._advance())
            elif mode == '10': # Memory Mode: 16-bit displacement
                displacement = bytes_to_int(self._advance(), self._advance())

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
    
            if immediate and not operator:
                if wide:
                    value = 'word ' + str(bytes_to_int(self._advance(), self._advance()))
                else:
                    value = 'byte ' + str(bytes_to_int(self._advance()))
                return [rm, value]
    
            elif operator:
                value = str(bytes_to_int(self._advance()))
                return [rm, value], reg_code
            
            else:
                if wide:
                    reg = REGISTER_MODE_WORD[reg_code]
                else:
                    reg = REGISTER_MODE_BYTE[reg_code]
                rm = rm.replace('+ -', '- ')
                args = [reg, rm]
                if not direction:
                    args = reversed(args)
                return args

    def memory_to_accumulator(self):
        # elif this_byte_as_bin[:7] in ["1010000", "1010001"]: # MOV Memory to accumulator
        direction = bool(int(self.last_byte[6]))
        wide = bool(int(self.last_byte[7]))
        if wide:
            register = 'ax'
            address = str(bytes_to_int(self._advance(), self._advance()))
            address = '[' + str(address) + ']'
        else:
            register = 'al'
            address = bytes_to_int(self._advance())
            address = '[' + str(address) + ']'
        args = [register, address]
        if direction:
            args = reversed(args)
        return args

    def scan_instruction(self):
        style = MYSTERY
        opcode = Opcode.UNKNOWN
        args = ['?']

        self._advance()
        if self.last_byte[:7] in ['0111010', '0111110', '0111111', '0111001', '0111011', '0111101', '0111000', '0111100', '1110001', '1110000']:
            style = FIRST_MOV
            opcode = Opcode.JZN
            args = [bytes_to_int(self._advance())]

        elif self.last_byte[:6] in ["100010", "000000", "000110", "001110", "001010"]:
            style = FIRST_MOV
            opcode = opcode_table.get(self.last_byte[:6])
            args = self.mod_reg_rm()
        
        elif self.last_byte[:6] in ["101000"]:
            style = FIRST_MOV
            opcode = opcode_table.get(self.last_byte[:6])
            args = self.memory_to_accumulator()

        elif self.last_byte[:6] in ["100000"]: # this is operator territory 
            style = FIRST_MOV
            args, reg = self.mod_reg_rm(immediate=True, operator=True)
            opcode = reg_opcode_table.get(reg)

        elif self.last_byte[:7] in ["0000010", "0010110", "0011110"]: # immediate to accumulator
            style = ACCUMULATOR_MOV
            opcode = opcode_table.get(self.last_byte[:7])
            args = self.memory_to_accumulator()
            
        elif self.last_byte[:7] in ["1100011"]: 
            style = IMMEDIATE_REG_MEM_MOV
            opcode = opcode_table.get(self.last_byte[:7])
            args = self.mod_reg_rm(immediate=True)

        self.add_instruction(opcode, args, style)

    def scan_instructions(self):
        while not self._is_at_end():
            self._start = self._current
            # try:
            self.scan_instruction()
            # except Exception as e:
            #     print(e)
            #     break
                
        return self.asm_instructions