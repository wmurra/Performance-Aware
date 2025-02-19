I really liked the lesson on the stack I want to take some notes of things to remember from it

IP in the asm context is Instruction Pointer
You cannot MOV it or PUSH it or POP it, 
you have to use CALL (basically JMP + PUSH IP)
and RET (POP IP off the stack and JUMP there)
but! ret isnt real! come back to that later
also when exactly do we push and pop? we could 
do push and pop on the IP at multiple places, this fact 
nessecitates a "Calling Convention" or "ABI"
also SP is one of the registers you CAN mess with and that
stands for Stack Pointer

ADD SP, 2 #This would move the actual pointer into the stack

MOV BX, SP
ADD AX, [BX] #This would add the 16bit value starting @ SP to AX 