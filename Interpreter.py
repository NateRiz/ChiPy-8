from random import getrandbits
import pygame
from sys import exit

pygame.init()


class Interpreter:
    MEMORY_START_ADDRESS = 0x200
    FONT_SET_START_ADDRESS = 0x50
    CHIP8_WIDTH = 64
    CHIP8_HEIGHT = 32
    SCALE = 25
    DEBUG_WINDOW_SIZE = 400
    SCREEN_WIDTH = 64 * SCALE
    SCREEN_HEIGHT = 32 * SCALE
    BACKGROUND_COLOR = (97, 134, 169)
    FOREGROUND_COLOR = (33, 41, 70)

    def __init__(self, rom_path, debug_mode):
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
        self.ascii_pygame_key_map = {
            "1": pygame.K_1,
            "2": pygame.K_2,
            "3": pygame.K_3,
            "4": pygame.K_4,
            "q": pygame.K_q,
            "w": pygame.K_w,
            "e": pygame.K_e,
            "r": pygame.K_r,
            "a": pygame.K_a,
            "s": pygame.K_s,
            "d": pygame.K_d,
            "f": pygame.K_f,
            "z": pygame.K_z,
            "x": pygame.K_x,
            "c": pygame.K_c,
            "v": pygame.K_v,
        }
        self.display = [0] * (Interpreter.CHIP8_WIDTH * Interpreter.CHIP8_HEIGHT)
        self._screen = pygame.display.set_mode((Interpreter.SCREEN_WIDTH + Interpreter.DEBUG_WINDOW_SIZE * debug_mode,
                                                Interpreter.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
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
            0x9: self.OP_9xy0,
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
            ops = [int('{:02X}'.format(b), 16) for b in content]
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
        self.clock.tick(600)

        self.get_input()

        self.op_code = (self.memory[self.program_counter] << 8) | self.memory[self.program_counter + 1]

        self.increment_program_counter()

        self.op_map[(self.op_code & 0xF000) >> 12]()

        if self.delay_timer > 0:
            self.delay_timer = 0
        if self.sound_timer > 0:
            self.sound_timer = 0

    def draw(self):
        tile_width = Interpreter.SCREEN_WIDTH // Interpreter.CHIP8_WIDTH
        tile_height = Interpreter.SCREEN_HEIGHT // Interpreter.CHIP8_HEIGHT

        colors = (Interpreter.BACKGROUND_COLOR, Interpreter.FOREGROUND_COLOR)

        for idx, toggle in enumerate(self.display):
            x = idx % Interpreter.CHIP8_WIDTH
            y = idx // Interpreter.CHIP8_WIDTH
            pygame.draw.rect(self._screen, colors[self.display[idx]],
                             (tile_width * x, tile_height * y, tile_width, tile_height))

    def get_input(self):
        self.input = [0] * 16
        if pygame.event.get(eventtype=pygame.QUIT):
            pygame.quit()
            exit(0)
        poll = pygame.key.get_pressed()
        for k, v in self.input_map.items():
            if poll[self.ascii_pygame_key_map[k]]:
                self.input[v] = 1
        pygame.event.clear()

    def increment_program_counter(self):
        self.program_counter += 2

    def decrement_program_counter(self):
        self.program_counter -= 2

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
        vx = (self.op_code & 0x0F00) >> 8

        if self.registers[vx] == self.op_code & 0x00FF:
            self.increment_program_counter()

    def OP_4xkk(self):  # SNE Vx, byte: Skip next instruction if Vx != kk
        vx = (self.op_code & 0x0F00) >> 8

        if self.registers[vx] != self.op_code & 0x00FF:
            self.increment_program_counter()

    def OP_5xy0(self):  # SE Vx, Vy: Skip next instruction if Vx = Vy
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        if self.registers[vx] == self.registers[vy]:
            self.increment_program_counter()

    def OP_6xkk(self):  # LD Vx, byte: Set Vx = kk
        vx = (self.op_code & 0x0F00) >> 8

        self.registers[vx] = self.op_code & 0x00FF

    def OP_7xkk(self):  # ADD Vx, byte: Set Vx = Vx + kk
        vx = (self.op_code & 0x0F00) >> 8

        self.registers[vx] = (self.registers[vx] + self.op_code & 0x00FF) % 0xFF

    def OP_8xy0(self):  # LD Vx, Vy: Set Vx = Vy
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        self.registers[vx] = self.registers[vy]

    def OP_8xy1(self):  # OR Vx, Vy: Set Vx = Vx OR Vy
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        self.registers[vx] |= self.registers[vy]

    def OP_8xy2(self):  # AND Vx, Vy: Set Vx = Vx AND Vy
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        self.registers[vx] &= self.registers[vy]

    def OP_8xy3(self):  # XOR Vx, Vy: Set Vx = Vx XOR Vy
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        self.registers[vx] ^= self.registers[vy]

    def OP_8xy4(self):  # ADD Vx, Vy: Set Vx = Vx + Vy, set VF = carry
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        res = self.registers[vx] + self.registers[vy]
        self.registers[0xF] = (0x100 & res) >> 8
        self.registers[vx] = res & 0xFF

    def OP_8xy5(self):  # SUB Vx, Vy: Set Vx = Vx - Vy, set VF = NOT borrow
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        self.registers[0xF] = int(self.registers[vx] > self.registers[vy])
        self.registers[vx] -= self.registers[vy]
        if self.registers[vx] < 0:
            self.registers[vx] += 0xFF + 1

    def OP_8xy6(self):  # SHR Vx {, Vy}: Set Vx = Vx SHR 1
        vx = (self.op_code & 0x0F00) >> 8

        self.registers[0xF] = self.registers[vx] & 1
        self.registers[vx] >>= 1

    def OP_8xy7(self):  # SUBN Vx, Vy: Set Vx = Vy - Vx, set VF = NOT borrow
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        self.registers[0xF] = int(self.registers[vy] > self.registers[vx])
        self.registers[vx] = self.registers[vy] - self.registers[vx]
        if self.registers[vx] < 0:
            self.registers[vx] += 0xFF + 1

    def OP_8xyE(self):  # SHL Vx {, Vy}: Set Vx = Vx SHL 1
        vx = (self.op_code & 0x0F00) >> 8

        self.registers[0xF] = (self.registers[vx] & 0x80) >> 7
        self.registers[vx] <<= 1
        if self.registers[0xF]:
            self.registers[vx] -= (0xFF + 1)

    def OP_9xy0(self):  # SNE Vx, Vy: Skip next instruction if Vx != Vy
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4

        if self.registers[vx] != self.registers[vy]:
            self.increment_program_counter()

    def OP_Annn(self):  # LD I, addr: Set I = nnn
        self.index_register = self.op_code & 0x0FFF

    def OP_Bnnn(self):  # P V0, addr: Jump to location nnn + V0
        self.program_counter = (self.op_code & 0x0FFF) + self.registers[0]

    def OP_Cxkk(self):  # RND Vx, byte: Set Vx = random byte AND kk
        vx = (self.op_code & 0x0F00) >> 8
        self.registers[vx] = getrandbits(8) & (self.op_code & 0x00FF)

    def OP_Dxyn(self):  # DRW Vx, Vy, nibble: Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision
        vx = (self.op_code & 0x0F00) >> 8
        vy = (self.op_code & 0x00F0) >> 4
        height = self.op_code & 0x000F
        width = 8
        self.registers[0xF] = 0

        for y in range(height):
            byte = self.memory[self.index_register + y]
            for x in range(width):
                idx = self.registers[vx] + width - x - 1 + (self.registers[vy] + y) * Interpreter.CHIP8_WIDTH
                byte >>= 1
                if idx >= len(self.display):
                    return # Temp fix since wrapping isnt implemented
                self.display[idx] ^= byte & 1
                if self.display[idx] == 0:
                    self.registers[0xF] = 1

        update_rect = pygame.rect.Rect(0, 0, Interpreter.SCREEN_WIDTH, Interpreter.SCREEN_HEIGHT)
        pygame.draw.rect(self._screen, Interpreter.BACKGROUND_COLOR, update_rect)
        self.draw()
        pygame.display.update(update_rect)



    def OP_Ex9E(self):  # SKP Vx: Skip next instruction if key with the value of Vx is pressed
        vx = (self.op_code & 0x0F00) >> 8
        if self.input[self.registers[vx]]:
            self.increment_program_counter()

    def OP_ExA1(self):  # SKNP Vx: Skip next instruction if key with the value of Vx is not pressed
        vx = (self.op_code & 0x0F00) >> 8
        if not self.input[self.registers[vx]]:
            self.increment_program_counter()

    def OP_Fx07(self):  # LD Vx, DT: Set Vx = delay timer value
        vx = (self.op_code & 0x0F00) >> 8
        self.registers[vx] = self.delay_timer

    def OP_Fx0A(self):  # LD Vx, K: Wait for a key press, store the value of the key in Vx
        vx = (self.op_code & 0x0F00) >> 8
        for idx, n in enumerate(self.input):
            if n:
                self.registers[vx] = idx
                return
        self.decrement_program_counter()

    def OP_Fx15(self):  # LD DT, Vx: Set delay timer = Vx
        vx = (self.op_code & 0x0F00) >> 8
        self.delay_timer = self.registers[vx]

    def OP_Fx18(self):  # LD ST, Vx: Set sound timer = Vx
        vx = (self.op_code & 0x0F00) >> 8
        self.sound_timer = self.registers[vx]

    def OP_Fx1E(self):  # ADD I, V: Set I = I + Vx
        vx = (self.op_code & 0x0F00) >> 8
        self.index_register += self.registers[vx]

    def OP_Fx29(self):  # LD F, Vx: Set I = location of sprite for digit Vx
        BYTES_PER_SPRITE = 5
        vx = (self.op_code & 0x0F00) >> 8
        self.index_register = Interpreter.FONT_SET_START_ADDRESS + BYTES_PER_SPRITE * self.registers[vx]

    def OP_Fx33(self):  # LD B, Vx: Store BCD representation of Vx in memory locations I, I+1, and I+2
        vx = (self.op_code & 0x0F00) >> 8
        val = self.registers[vx]
        self.memory[self.index_register+2] = val % 10
        val //= 10
        self.memory[self.index_register+1] = val % 10
        val //= 10
        self.memory[self.index_register] = val % 10

    def OP_Fx55(self):  # LD [I], Vx: Store registers V0 through Vx in memory starting at location I
        vx = (self.op_code & 0x0F00) >> 8
        for i in range(vx+1):
            self.memory[self.index_register + i] = self.registers[i]

    def OP_Fx65(self):  # LD Vx, [I]: Read registers V0 through Vx from memory starting at location I
        vx = (self.op_code & 0x0F00) >> 8
        for i in range(vx+1):
            self.registers[i] = self.memory[self.index_register + i]
