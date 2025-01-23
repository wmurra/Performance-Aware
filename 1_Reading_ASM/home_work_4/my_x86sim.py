from pathlib import Path
from dataclasses import dataclass, field

import sim86

class VirtualMachine:
    def __init__(self):
        self.registers = [0 for x in range(12)] 
        verbose: bool = True

    def print_registers(self):
        print(' ---- Final Registers ---- ')
        for i, register in enumerate(self.registers):
            if i == 8:
                break
            print(f"{sim86.registers_dict[i+1]}: {hex(register)} ({register})")

    def exec_instruction(
            self, 
            decoded_inst: sim86.Instruction, 
            formatted_bytes: str
            ) -> None:

        print(str(decoded_inst))
        if decoded_inst.op.name == 'mov':
            self.mov(decoded_inst)

    def mov(self, decoded_inst: sim86.Instruction):
        
        index = decoded_inst.operands[0].index
        offset = decoded_inst.operands[0].offset
        count = decoded_inst.operands[0].count

        destination  = decoded_inst.operands[0]
        source  = decoded_inst.operands[1]

        # destination is always a reg, source may not always be a reg

        dest_index = destination.index - 1

        if isinstance(source, sim86.RegisterAccess):
            source_value = self.registers[source.index -1]

        elif isinstance(source, sim86.EffectiveAddressExpression):
            source_value = self.registers[source.explicit_segment + source.displacement]

        elif isinstance(source, sim86.Immediate):
            source_value = source.value

        self.registers[dest_index] = source_value

        # self.registers['ah'] = decoded_inst.operands[1].value
        # print(self.registers.registers)


if __name__ == "__main__":
    # bin_path_as_str = Path("listing_0045_challenge_register_movs") 
    bin_path_as_str = Path("listing_0044_register_movs") 
    # bin_path_as_str = Path("listing_0043_immediate_movs") 

    # bin_path_as_str = Path("listing_0040_challenge_movs")
    vm = VirtualMachine()
    try:
        with Path(bin_path_as_str).open('rb') as f:
            bin = f.read()
            offset = 0

            while offset < len(bin):
                decoded = sim86.decode_8086_instruction(bin, offset)
                if decoded.op != sim86.OperationType.none:
                    last_offset = offset
                    offset += decoded.size
                    
                    literal_bytes = bin[last_offset:offset]
                    literal_bytes_as_binary_str = ' '.join(format(byte, '08b') for byte in literal_bytes)
                    formatted_bytes = (literal_bytes_as_binary_str)

                    op = sim86.mnemonic_from_operation_type(decoded.op)
                    dst, src  = decoded.operands
                    vm.exec_instruction(decoded, formatted_bytes)

                else:
                    print("unrecognized instruction")
                    break
            vm.print_registers()

    except FileNotFoundError:
            print(f"Error: File not found at {bin_path_as_str}")