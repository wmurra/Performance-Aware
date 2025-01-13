ok basically I need to write a decoder for the instruction encoding for MOV in x86 ASM
im gonna do it in python

MOV is the mnemonic for an operator of an x86 binary instruction

it goes MOV dest, src
             ^^^^^^^these are its operands
NOTE: destination precedes source, which is a little weird, but apparently thats an intel convention

the full instruction is 2 bytes

take 2 byes, the top 6 bits are like the 'op code'
then we have 

OPCODE,D,W MOD,REG,R/M
OPCODE will always be 100010
w means wide that will vary
d is always 0
MOD will always be 11
REG and R/M will be the 

so i just need 2 tables, wide and non wide, and look up src and dst based on that

ok so that was actually very easy... did I do ut wrong? why did casey make it sound tricky? maybe my implementation overfit the problem. idk