"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # set up program counter
        self.pc = 0
        # set space for ram
        self.ram = [0] * 256
        # set space for the register
        self.reg = [0] * 8
        # set check for halted state
        self.halted = False
        # declare stack pointer
        self.SP = 7
        # initialize stack at address f4 (empty stack), as described in spec
        self.reg[self.SP] = 0xf4

        # set up branch table to hold operations pointing to handler defs
        self.branchtable = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            MUL: self.mul,
            POP: self.pop,
            PSH: self.psh,
            CALL: self.call,
            RET: self.ret
        }

    # mar = memory address register
    # mdr = memory data register

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self, program):
        """Load a program into memory."""

        address = 0

        with open(program) as file:
            for line in file:
                line = line.split("#")[0]
                line = line.strip()

                if line == '':
                    continue

                val = int(line, 2)

                self.ram[address] = val
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
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
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # while loop to check halted state
        while not self.halted:
            # check ram space
            ir = self.ram[self.pc]
            # add in alu ops
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            fndInst = ((ir >> 6)) + 1

            if ir in self.branchtable:
                self.branchtable[ir](operand_a, operand_b)

            else:
                self.trace()
                print("instruction error")

            self.pc += fndInst

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def hlt(self, operand_a, operand_b):
        self.halted = True

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    def pshVal(self, val):
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], val)

    def psh(self, operand_a, operand_b):
        self.pshVal(self.reg[operand_a])

    def popVal(self):
        val = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1
        return val

    def pop(self, operand_a, operand_b):
        self.reg[operand_a] = self.popVal()

    def call(self, operand_a, operand_b):
        self.pshVal(self.pc + 2)
        self.pc = self.reg[operand_a]

    def ret(self, operand_a, operand_b):
        self.pc = self.popVal()
