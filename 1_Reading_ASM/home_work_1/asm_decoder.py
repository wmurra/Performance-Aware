RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
PINK = "\033[35m"

RESET = "\033[0m"

wide_table = {
    '000':'ax',
    '001':'cx',
    '010':'dx',
    '011':'bx',
    '100':'sp',
    '101':'bp',
    '110':'si',
    '111':'di',
}
non_wide_table = {
    '000':'al',
    '001':'cl',
    '010':'dl',
    '011':'bl',
    '100':'ah',
    '101':'ch',
    '110':'dh',
    '111':'bh',
}
def string_insert(original:str, substring:str, index:int):
    return original[:index] + substring + original[index:]

def decode_instruction(two_bytes: bytes) -> str:
    wide = bool(int(format(two_bytes[0], '08b')[7]))
    if wide:
        src = wide_table[format(two_bytes[1], '08b')[2:5]]
        dest = wide_table[format(two_bytes[1], '08b')[5:]]

    else:
        src = non_wide_table[format(two_bytes[1], '08b')[2:5]]
        dest = non_wide_table[format(two_bytes[1], '08b')[5:]]

    return f"mov {dest}, {src}"

def read_file_as_binary(file_path):
    asm_lines = []
    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Read the file content as bytes
            file_content = file.read()

        print(f"OPCODE {RED}D {BLUE}W {GREEN}MOD {YELLOW}REG {PINK}R/M{RESET}")
        print("")
        # Convert each byte to its binary representation
        binary_content = ' '.join(format(byte, '08b') for byte in file_content)
        for i in range(0, len(file_content), 2):
            two_bytes = file_content[i:i+2]
            instruction = decode_instruction(two_bytes)
            the_string = f"{format(two_bytes[0], '08b')}, {format(two_bytes[1], '08b')}{RESET}"
            the_string = string_insert(the_string, RED, 6)
            the_string = string_insert(the_string, BLUE, 12)
            the_string = string_insert(the_string, RESET, 18)
            the_string = string_insert(the_string, GREEN, 24)
            the_string = string_insert(the_string, YELLOW, 31)
            the_string = string_insert(the_string, PINK, 39)
            the_string += f" {instruction}"

                        # the_string = string_insert(the_string, RED, 7)

            print(the_string)
        # Print the binary content
        # print(binary_content)
    
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
file_path = "listing_0037_single_register_mov"  # Replace with the path to your file
file_path = "listing_0038_many_register_mov"  # Replace with the path to your file

read_file_as_binary(file_path)
