import binascii
from random import getrandbits
import pygame

pygame.init()


class Interpreter:
    MEMORY_START_ADDRESS = 0x200
    FONT_SET_START_ADDRESS = 0x50
    CHIP8_WIDTH = 64
    CHIP8_HEIGHT = 32
    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 480

    def __init__(self, rom_path):
        self.registers = [0] * 16
        self.memory = [0x00] * 4096
        self.load_rom(rom_path)
        self.load_fonts()
        self.index_register = 0
        self.stack = [Interpreter.MEMORY_START_ADDRESS] * 16  # 16 level stack for Program Counter
        self.stack_pointer = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.input = [0] * 16
        self.input_map = {
            "1": 0x1,
            "2": 0x2,
            "3": 0x3,
            "4": 0xC,
            "q": 0x4,
            "w": 0x5,
            "e": 0x6,
            "r": 0xD,
            "a": 0x7,
            "s": 0x8,
            "d": 0x9,
            "f": 0xE,
            "z": 0xA,
            "x": 0x0,
            "c": 0xB,
            "v": 0xF,
        }
        self.display = [0] * (Interpreter.CHIP8_WIDTH * Interpreter.CHIP8_HEIGHT)
        self._screen = pygame.display.set_mode((Interpreter.SCREEN_WIDTH, Interpreter.SCREEN_HEIGHT))
        pygame.display.set_caption("ChiPy-8 Interpreter")
        self.op_code = 0

        self._op_map0 = {
            0x0: self.OP_00E0,
            0xE: self.OP_00EE
        }

        self._op_map8 = {
            0x0: self.OP_8xy0,
            0x1: self.OP_8xy1,
            0x2: self.OP_8xy2,
            0x3: self.OP_8xy3,
            0x4: self.OP_8xy4,
            0x5: self.OP_8xy5,
            0x6: self.OP_8xy6,
            0x7: self.OP_8xy7,
            0xE: self.OP_8xyE
        }

        self._op_mapE = {
            0xE: self.OP_Ex9E,
            0x1: self.OP_ExA1
        }

        self._op_mapF = {
            0x07: self.OP_Fx07,
            0x0A: self.OP_Fx0A,
            0x15: self.OP_Fx15,
            0x18: self.OP_Fx18,
            0x1E: self.OP_Fx1E,
            0x29: self.OP_Fx29,
            0x33: self.OP_Fx33,
            0x55: self.OP_Fx55,
            0x65: self.OP_Fx65
        }

        self.op_map = {
            0x0: self.__op_map0,
            0x1: self.OP_1nnn,
            0x2: self.OP_2nnn,
            0x3: self.OP_3xkk,
            0x4: self.OP_4xkk,
            0x5: self.OP_5xy0,
            0x6: self.OP_6xkk,
            0x7: self.OP_7xkk,
            0x8: self.__op_map8,
            0xA: self.OP_Annn,
            0xB: self.OP_Bnnn,
            0xC: self.OP_Cxkk,
            0xD: self.OP_Dxyn,
            0xE: self.__op_mapE,
            0xF: self.__op_mapF,
        }

    @property
    def program_counter(self):
        return self.stack[self.stack_pointer]

    @program_counter.setter
    def program_counter(self, val):
        self.stack[self.stack_pointer] = val

    def __op_map0(self):
        self._op_map0[self.op_code & 0x000F]()

    def __op_map8(self):
        self._op_map8[self.op_code & 0x000F]()

    def __op_mapE(self):
        self._op_mapE[self.op_code & 0x000F]()

    def __op_mapF(self):
        self._op_mapF[self.op_code & 0x00FF]()

    def load_rom(self, rom_path):
        with open(rom_path, "rb") as f:
            content = f.read()
        ops = binascii.hexlify(content)
        self.memory[Interpreter.MEMORY_START_ADDRESS:Interpreter.MEMORY_START_ADDRESS + len(ops)] = ops

    def load_fonts(self):
        font_set = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        self.memory[Interpreter.FONT_SET_START_ADDRESS: Interpreter.FONT_SET_START_ADDRESS + len(font_set)] = font_set

    def tick(self):
        self.get_input()

        self.op_code = (self.memory[self.program_counter] << 8) | self.memory[self.program_counter + 1]
        self.op_map[self.op_code]()

        self.increment_program_counter()

        self._screen.flip()

    def get_input(self):
        self.input = [0] * 16
        for i in pygame.event.get(eventtype=pygame.KEYDOWN):
            if chr(i.key) in self.input_map:
                self.input[self.input_map[chr(i.key)]] = 1
        pygame.event.clear()

    def increment_program_counter(self):
        self.program_counter += 2

    def OP_00E0(self):  # CLS: Clear the Display
        self.display = [0] * (64 * 32)

    def OP_00EE(self):  # RET: Return from a subroutine
        self.stack_pointer -= 1

    def OP_1nnn(self):  # JP addr: Jump to location nnn
        self.program_counter = self.op_code & 0x0FFF

    def OP_2nnn(self):  # CALL addr: Call subroutine at nnn
        self.stack_pointer += 1
        self.program_counter = self.op_code & 0x0FFF

    def OP_3xkk(self):  # SE Vx, byte: Skip next instruction if Vx = kk
        if self.registers[self.op_code & 0x0F00] == self.op_code & 0x00FF:
            self.increment_program_counter()

    def OP_4xkk(self):  # SNE Vx, byte: Skip next instruction if Vx != kk
        if self.registers[self.op_code & 0x0F00] != self.op_code & 0x00FF:
            self.increment_program_counter()

    def OP_5xy0(self):  # SE Vx, Vy: Skip next instruction if Vx = Vy
        if self.registers[self.op_code & 0x0F00] == self.registers[self.op_code & 0x00F0]:
            self.increment_program_counter()

    def OP_6xkk(self):  # LD Vx, byte: Set Vx = kk
        self.registers[self.op_code & 0x0F00] = self.op_code & 0x00FF

    def OP_7xkk(self):  # ADD Vx, byte: Set Vx = Vx + kk
        self.registers[self.op_code & 0x0F00] += self.op_code & 0x00FF

    def OP_8xy0(self):  # LD Vx, Vy: Set Vx = Vy
        self.registers[self.op_code & 0x0F00] = self.registers[self.op_code & 0x00F0]

    def OP_8xy1(self):  # OR Vx, Vy: Set Vx = Vx OR Vy
        self.registers[self.op_code & 0x0F00] = self.registers[self.op_code & 0x0F00] | self.registers[
            self.op_code & 0x00F0]

    def OP_8xy2(self):  # AND Vx, Vy: Set Vx = Vx AND Vy
        self.registers[self.op_code & 0x0F00] = self.registers[self.op_code & 0x0F00] & self.registers[
            self.op_code & 0x00F0]

    def OP_8xy3(self):  # XOR Vx, Vy: Set Vx = Vx XOR Vy
        self.registers[self.op_code & 0x0F00] = self.registers[self.op_code & 0x0F00] ^ self.registers[
            self.op_code & 0x00F0]

    def OP_8xy4(self):  # ADD Vx, Vy: Set Vx = Vx + Vy, set VF = carry
        res = self.registers[self.op_code & 0x0F00] + self.registers[self.op_code & 0x00F0]
        self.registers[0xF] = (0x100 & res) >> 8
        self.registers[self.op_code & 0x0F00] = res & 0xFF

    def OP_8xy5(self):  # SUB Vx, Vy: Set Vx = Vx - Vy, set VF = NOT borrow
        self.registers[0xF] = int(self.registers[self.op_code & 0x0F00] > self.registers[self.op_code & 0x00F0])
        self.registers[self.op_code & 0x0F00] -= self.registers[self.op_code & 0x00F0]
        if self.registers[self.op_code & 0xF00] < 0:
            self.registers[self.op_code & 0xF00] += 0xFF

    def OP_8xy6(self):  # SHR Vx {, Vy}: Set Vx = Vx SHR 1
        self.registers[0xF] = self.registers[(self.op_code & 0x0F00) & 1]
        self.registers[self.op_code & 0x0F00] >>= 1

    def OP_8xy7(self):  # SUBN Vx, Vy: Set Vx = Vy - Vx, set VF = NOT borrow
        self.registers[0xF] = int(self.registers[self.op_code & 0x00F0] > self.registers[self.op_code & 0x0F00])
        self.registers[self.op_code & 0x0F00] = self.registers[self.op_code & 0x00F0] - self.registers[
            self.op_code & 0x0F00]
        if self.registers[self.op_code & 0xF00] < 0:
            self.registers[self.op_code & 0xF00] += 0xFF

    def OP_8xyE(self):  # SHL Vx {, Vy}: Set Vx = Vx SHL 1
        self.registers[0xF] = self.registers[(self.op_code & 0x0F00) & 0x80]
        self.registers[(self.op_code & 0x0F00)] <<= 1
        if self.registers[0xF]:
            self.registers[(self.op_code & 0x0F00)] -= 0xFF

    def OP_9xy0(self):  # SNE Vx, Vy: Skip next instruction if Vx != Vy
        if self.registers[self.op_code & 0x0F00] != self.registers[self.op_code & 0x00F0]:
            self.increment_program_counter()

    def OP_Annn(self):  # LD I, addr: Set I = nnn
        self.index_register = self.op_code & 0x0FFF

    def OP_Bnnn(self):  # P V0, addr: Jump to location nnn + V0
        self.program_counter = self.op_code | 0x0FFF + self.registers[0]

    def OP_Cxkk(self):  # RND Vx, byte: Set Vx = random byte AND kk
        self.registers[self.op_code & 0x0F00] = getrandbits(8) & (self.op_code & 0x00FF)

    def OP_Dxyn(self):  # DRW Vx, Vy, nibble: Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision
        sprite = self.memory[self.index_register:self.registers[self.op_code & 0x000F]]
        x = self.memory[self.op_code & 0x0F00]
        y = self.memory[self.op_code & 0x00F0]

        idx = x + x * y
        for i in range(len(sprite)):
            self.display[idx] ^= sprite[i]
            if not self.display[idx]:
                self.registers[0xF] = 1

        tile_width = Interpreter.SCREEN_WIDTH // Interpreter.CHIP8_WIDTH
        tile_height = Interpreter.SCREEN_HEIGHT // Interpreter.CHIP8_HEIGHT
        colors = ((0, 0, 0), (255, 255, 255))
        for i in range(idx, idx + len(sprite)):
            pygame.draw.rect(self._screen, colors[self.display[i]],
                             (tile_width * (i % Interpreter.CHIP8_WIDTH), tile_height * (i // Interpreter.CHIP8_HEIGHT),
                              tile_width, tile_height))

    def OP_Ex9E(self):  # SKP Vx: Skip next instruction if key with the value of Vx is pressed
        if self.input[self.registers[self.op_code & 0x0F00]]:
            self.increment_program_counter()

    def OP_ExA1(self):  # SKNP Vx: Skip next instruction if key with the value of Vx is not pressed
        if not self.input[self.registers[self.op_code & 0x0F00]]:
            self.increment_program_counter()

    def OP_Fx07(self):  # LD Vx, DT: Set Vx = delay timer value
        self.registers[self.op_code & 0x0F00] = self.delay_timer

    def OP_Fx0A(self):  # LD Vx, K: Wait for a key press, store the value of the key in Vx
        for idx, n in self.input:
            if n:
                self.registers[self.op_code & 0x0F00] = idx
                return

    def OP_Fx15(self):  # LD DT, Vx: Set delay timer = Vx
        self.delay_timer = self.op_code & 0x0F00

    def OP_Fx18(self):  # LD ST, Vx: Set sound timer = Vx
        self.sound_timer = self.op_code & 0x0F00

    def OP_Fx1E(self):  # ADD I, V: Set I = I + Vx
        self.index_register += self.op_code & 0x0F00

    def OP_Fx29(self):  # LD F, Vx: Set I = location of sprite for digit Vx
        BYTES_PER_SPRITE = 5
        self.index_register = self.memory[Interpreter.FONT_SET_START_ADDRESS + BYTES_PER_SPRITE * (self.op_code & 0x0F00)]

    def OP_Fx33(self):  # LD B, Vx: Store BCD representation of Vx in memory locations I, I+1, and I+2
        val = self.op_code & 0xF00
        self.memory[self.index_register] = val % 10
        val //= 10
        self.memory[self.index_register+1] = val % 10
        val //= 10
        self.memory[self.index_register+2] = val % 10

    def OP_Fx55(self):  # LD [I], Vx: Store registers V0 through Vx in memory starting at location I
        for i in range(self.op_code & 0x0F00):
            self.memory[self.index_register + i] = self.registers[i]

    def OP_Fx65(self):  # LD Vx, [I]: Read registers V0 through Vx from memory starting at location I
        for i in range(self.op_code & 0x0F00):
            self.registers[i] = self.memory[self.index_register + i]