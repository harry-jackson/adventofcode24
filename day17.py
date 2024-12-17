from dataclasses import dataclass
from typing import List, Callable


class Computer:
    OpCodes: List[int]
    A: int
    B: int
    C: int
    Pointer: int
    Output: List[int]
    Operations: List[Callable]

    def __init__(self):
        self.OpCodes = []
        self.A = 0
        self.B = 0
        self.C = 0
        self.Pointer = 0
        self.Output = []
        self.Operations = [self.adv, self.bxl, self.bst, self.jnz, self.bxc, self.out, self.bdv, self.cdv]

    def step(self):
        
        if self.Pointer < 0 or self.Pointer >= len(self.OpCodes):
            return True
        
        f_id = self.OpCodes[self.Pointer]
        operand = self.OpCodes[self.Pointer + 1]
        f = self.Operations[f_id]
        
        f(operand)
        self.Pointer += 2
        
        return False
    
    def run(self, max_loops = None):
        halt = False
        loops = 0
        while not halt:

            if max_loops is not None and loops > max_loops:
                return self.Output
            
            halt = self.step()
        return self.Output

    def debug(self):
        print(f'A: {self.A}, B: {self.B}, C: {self.C}, Pointer: {self.Pointer}')

    def combo(self, operand):
        if operand >= 0 and operand <= 3:
            return operand
        elif operand == 4:
            return self.A
        elif operand == 5:
            return self.B
        elif operand == 6:
            return self.C
        elif operand == 7:
            raise ValueError('Operand 7 is reserved and will not appear in valid programs.')
        else:
            raise ValueError('Invalid operand')
        
    def set_register(self, register, value):
        self.__setattr__(register, value)

    def get_register(self, register):
        self.__getattribute__(register)

    def set_instructions(self, instructions):
        self.OpCodes = instructions

    def _dv(self, operand):
        return self.A // (2  ** self.combo(operand))

    def adv(self, operand):
        self.A = self._dv(operand)
    
    def bxl(self, operand):
        self.B = self.B ^ operand
    
    def bst(self, operand):
        self.B = self.combo(operand) % 8

    def jnz(self, operand):
        if self.A != 0:
            self.Pointer = operand - 2

    def bxc(self, operand):
        self.B = self.B ^ self.C

    def out(self, operand):
        self.Output.append(self.combo(operand) % 8)

    def bdv(self, operand):
        self.B = self._dv(operand)

    def cdv(self, operand):
        self.C = self._dv(operand)

def initialize_computer(lines: List[str]):
    computer = Computer()

    for line in lines:
        match line.strip().replace(':', '').split(' '):
            case ['Register', r, n]:
                computer.set_register(r, int(n))
            case ['Program', instructions]:
                program = [int(i) for i in instructions.split(',')]
                computer.set_instructions(program)

    return computer

def main():
    with open('data/day17.txt', 'r') as f:
        lines = f.readlines()

    computer = initialize_computer(lines)
    res = computer.run()
    part_1 = ''.join([str(n) for n in res])

    # Part 2: Notice that the program is one set of operations, 
    # with a loop at the end going back to the beginning. 

    # Each loop outputs the value of B at the end.
    # Each loop, A gets integer divided by 8. 
    # The program halts when A is zero at the end of the instruction set.

    # So first we look for a number A < 8 that causes the operations to 
    # produce the last value in the list. 
    # (< 8 so that A is divided to 0 and the program halts).

    # Then we look for a number over 8 times that value that outputs 
    # the last two values in the list. 
    
    # Carry on until we have a value that outputs the whole thing.
    op_codes = computer.OpCodes

    target_As = [0]
    for i in reversed(range(len(op_codes))):

        last_target_A = target_As[-1]
        
        A = last_target_A * 8
        while True:
            computer = initialize_computer(lines)
            computer.set_register('A', A)

            computer.run(max_loops = 16 - i)
                    
            if computer.Output == op_codes[i:]:
                target_As.append(A)
                break

            A += 1
            
    part_2 = target_As[-1]

    print(f'Part 1: {part_1}')
    print(f'Part 2: {part_2}')

if __name__ == '__main__':
    main()