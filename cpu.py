"""CPU functionality."""

import sys

# Parse the command line

# print(sys.argv[1])

ldi_ls8 = int('10000010', 2)
print_ls8 = int('01000111', 2)
multiply_ls8 = int('10100010', 2)
compare_ls8 = int('10100111', 2)
jump_ls8 = int('01010100', 2)
jeq_ls8 = int('01010101', 2)
jne_ls8 = int('01010110', 2)
halt_ls8 = int('00000001', 2)

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 9
        self.pc = 0
        self.sp = 0xF4
        self.fl = '00000000'
        self.ban = []
        self.branchtable = {}
        self.branchtable[ldi_ls8] = self.ldi
        self.branchtable[print_ls8] = self.prn
        self.branchtable[multiply_ls8] = self.mul
        self.branchtable[compare_ls8] = self.compare
        self.branchtable[jump_ls8] = self.jmp
        self.branchtable[jeq_ls8] = self.jeq
        self.branchtable[jne_ls8] = self.jne
        self.branchtable[halt_ls8] = self.hlt

    def ram_read(self, mar):
        '''
        Accepts the address to read and return the value stored there
        Memory Address Register (mar) - contains the address that is being read or written to.
        '''
        return self.reg[mar]

    def ram_write(self, mdr, mar):
        '''
        Accepts a value to write, and the address to write it to
        Memory Data Register (mdr) - contains the data that was read or the data to write
        '''
        # print(f'BEFORE WRITING {mdr}: {self.reg[mar]}')
        self.reg[mar] = mdr
        # print(f'AFTER WRITING {mdr}: {self.reg[mar]}')

    def load(self):
        """Load a program into memory."""

        address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        # OPEN FILE
        if len(sys.argv) == 2:
            program_filename = sys.argv[1]
            with open(program_filename) as f:
                # LOOP THROUGH EACH LINE IN THE FILE
                for line in f:
                    # SPLIT AT ANY POINT THERE IS A #
                    line = line.split('#')
                    # REMOVE THE FIRST PART OF THE SPLIT (EVERYTHING BEFORE THE #)
                    line = line[0].strip()

                    # IF THE LINE IS EMPTY, CONTINUE
                    if line == '':
                        continue

                    # CONVERT LINE TO INTEGER AND ADD LINE TO ADDRESS
                    self.ram[address] = (int(line, 2))
                    address += 1
        else:
            print('File undefined: Please input `cpu.py [file_name].py` to define the file you want to run.')
            exit()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
        
    def update_pc(self, value, instruction):
        '''
        Meanings of the bits in the first byte of each instruction: `AABCDDDD`

        * `AA` Number of operands for this opcode, 0-2
        * `B` 1 if this is an ALU operation
        * `C` 1 if this instruction sets the PC
        * `DDDD` Instruction identifier
        '''
        convert_to_binary = format(int(value), '#010b')
        # print(f'CONVERTING TO BINARY: {int(value)} --> {convert_to_binary} --> {convert_to_binary[:4]} --> {int(convert_to_binary[:4], 2)}')
        # print('GETTING 4TH BYTE', convert_to_binary[5:6])
        increment = int(convert_to_binary[:4], 2) + 1
        if convert_to_binary[5:6] == '1' and instruction is not None:
            # print('CURRENT POSITION', self.pc)
            # print('INSTRUCTION RESULT', instruction)
            self.ban.append(self.pc)
            self.pc = instruction
        else:    
            self.pc += increment
        # print('UPDATE PC - AFTER', self.pc)

    def ldi(self, operand_a, operand_b):
        '''
        Set the value of a register to an integer.
        '''
        # print('LDI')
        self.ram_write(operand_b, operand_a)

    def prn(self, operand_a, operand_b):
        '''
        Print numeric value stored in the given register.

        Print to the console the decimal integer value that is stored in the given register.
        '''
        # print('PRN')
        print(self.ram_read(operand_a))

    def mul(self, operand_a, operand_b):
        '''
        Multiply the values in two registers together and store the result in registerA
        '''
        # print('MUL')
        self.alu('MUL', operand_a, operand_b)

    def compare(self, operand_a, operand_b):
        '''
        Compare the values in two registers.

        * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.

        * If registerA is less than registerB, set the Less-than `L` flag to 1,
          otherwise set it to 0.

        * If registerA is greater than registerB, set the Greater-than `G` flag
          to 1, otherwise set it to 0.
        '''
        if self.ram_read(operand_a) == self.ram_read(operand_b):
          # print(f'{self.ram_read(operand_a)} == {self.ram_read(operand_b)}')
          self.fl = '00000001'
        elif self.ram_read(operand_a) < self.ram_read(operand_b):
          # print(f'{self.ram_read(operand_a)} < {self.ram_read(operand_b)}')
          self.fl = '00000100'
        elif self.ram_read(operand_a) > self.ram_read(operand_b):
          # print(f'{self.ram_read(operand_a)} > {self.ram_read(operand_b)}')
          self.fl = '00000010'
        else:
          # print(f'{self.ram_read(operand_a)} != {self.ram_read(operand_b)}')
          self.fl = '00000000'

        # print(self.fl)

    def jmp(self, operand_a, operand_b):
        '''
        Jump to the address stored in the given register.

        Set the `PC` to the address stored in the given register.
        '''
        return self.ram_read(operand_a)

    def jeq(self, operand_a, operand_b):
        '''
        If `equal` flag is set (true), jump to the address stored in the given register.
        '''
        if self.fl[7] == '1':
          return self.ram_read(operand_a)

    def jne(self, operand_a, operand_b):
        '''
        If `E` flag is clear (false, 0), jump to the address stored in the given register.
        '''
        if self.fl[7] == '0':
          return self.ram_read(operand_a)
        
    def hlt(self, operand_a, operand_b):
        '''
        Halt the CPU (and exit the emulator).
        '''
        return False

    def run(self):
        '''
        Run the CPU.
        '''

        while True:
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]
            
            instruction = self.branchtable[self.ram[self.pc]](operand_a, operand_b)

            if instruction is not False and self.pc not in self.ban:
                # print(self.pc in self.ban)
                instruction
                self.update_pc(self.ram[self.pc], instruction)
            else:
                return False

    # def push(self, operand_a = None, operand_b = None):
    #     '''
    #     Push the value in the given register on the stack.

    #     1. Decrement the `SP`.
    #     2. Copy the value in the given register to the address pointed to by `SP`.
    #     '''
    #     print('PUSH')
    #     self.sp -= 1

    #     if operand_a is not None and operand_b is not None:
    #         self.ram[self.sp] = self.ram_read(operand_a)
    #     else:
    #         return self.ram[self.sp]

    # def pop(self, operand_a = None, operand_b = None):
    #     '''
    #     Pop the value at the top of the stack into the given register.

    #     1. Copy the value from the address pointed to by `SP` to the given register.
    #     2. Increment `SP`.
    #     '''
    #     print('POP')
    #     if operand_a is not None and operand_b is not None:
    #         self.ram_write(self.ram[self.sp], operand_a)
    #     else:
    #         return_address = self.ram[self.sp]
    #         self.sp += 1
    #         return return_address
    #     self.sp += 1

    # def call(self, operand_a, operand_b):
    #     '''
    #     Calls a subroutine (function) at the address stored in the register.

    #     1. The address of the ***instruction*** _directly after_ `CALL` is
    #     pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
    #     2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
    #     '''
    #     print('CALL')
    #     return_address = self.pc + 2

    #     # PUSH ON THE STACK
    #     # DECREMENT THE STACK POINTER
    #     return_address = self.push()

    #     # SET THE PC TO THE VALUE IN THE GIVEN REGISTER
    #     reg_number = self.ram[self.pc + 1]
    #     destination_address = self.ram_read(reg_number)

    #     return destination_address

    # def ret(self, operand_a, operand_b):
    #     '''
    #     Return from subroutine.

    #     Pop the value from the top of the stack and store it in the `PC`.
    #     '''
    #     print('RET')
    #     # POP RETURN ADDRESS FROM TOP OF STACK
    #     print('REACHED RET', self.pop())
    #     return self.pop()