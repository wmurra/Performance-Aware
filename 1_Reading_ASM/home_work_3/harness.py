from pathlib import Path
from new_decoder import Decoder

bin_path_as_str = Path("listing_0041_add_sub_cmp_jnz")  # Replace with the path to your file
# bin_path_as_str = Path("listing_0040_challenge_movs")  # Replace with the path to your file

try:
    with Path(bin_path_as_str).open('rb') as f:
        bin = f.read()
        decoder = Decoder(bin)
        instructions = decoder.scan_instructions()
        for instruction in instructions:
            print(instruction.debug_repr())
except FileNotFoundError:
        print(f"Error: File not found at {bin_path_as_str}")