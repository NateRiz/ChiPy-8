import os
import pygame
import unittest
from unittest.mock import patch
from Interpreter import Interpreter
from tests_utils import *


class Test(unittest.TestCase):

    def setUp(self):
        patch('pygame.display.set_mode', lambda _: None).start()
        patch('pygame.display.flip', lambda: None).start()
        patch('pygame.draw.rect', lambda a, b, c: None).start()
        # Todo Patch Clock.tick()

    def test_loads_rom_correctly(self):
        path = os.path.join(os.getcwd(), "test_roms", "rand_512_bytes.ch8")
        num_bytes = 512
        create_random_hex_file(num_bytes, path)
        hex_dump = None
        with open(path, "rb") as file:
            contents = file.read()
            hex_dump = [int('{:02X}'.format(b), 16) for b in contents]

        interpreter = Interpreter(path)
        for idx, i in enumerate(
                interpreter.memory[Interpreter.MEMORY_START_ADDRESS: Interpreter.MEMORY_START_ADDRESS + num_bytes]):
            self.assertEqual(hex_dump[idx], i, F"Wrong value at idx:{idx}. Got {i}, expected {hex_dump[idx]}")

    def test_OP_00E0(self):  # CLS: Clear the Display
        path = os.path.join(os.getcwd(), "test_roms", "clear_display.ch8")
        interpreter = Interpreter(path)
        interpreter.display = [1] * len(interpreter.display)
        interpreter.tick()
        self.assertTrue(not any(interpreter.display), F"Expected cleared display. Got {interpreter.display}")

    def test_OP_00EE(self):  # RET: Return from a subroutine
        path = os.path.join(os.getcwd(), "test_roms", "return_from_subroutine.ch8")
        interpreter = Interpreter(path)
        interpreter.stack = [0x300] + [0x200] * 15
        interpreter.stack_pointer = 1
        interpreter.tick()
        correct = [0x300, 0x202] + [0x200] * 14
        self.assertEqual(interpreter.stack, correct)
        self.assertEqual(interpreter.stack_pointer, 0)

    def test_OP_1nnn(self):  # JP addr: Jump to location nnn
        path = os.path.join(os.getcwd(), "test_roms", "jump.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x212)

    def test_OP_2nnn(self):  # CALL addr: Call subroutine at nnn
        path = os.path.join(os.getcwd(), "test_roms", "call_subroutine.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        correct = [0x202, 0x204] + [0x200] * 14
        self.assertEqual(interpreter.stack, correct)
        self.assertEqual(interpreter.stack_pointer, 1)

    def test_OP_3xkk(self):  # SE Vx, byte: Skip next instruction if Vx = kk
        path = os.path.join(os.getcwd(), "test_roms", "SE.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[0] = 10
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x204)

    def test_OP_4xkk(self):  # SNE Vx, byte: Skip next instruction if Vx != kk
        path = os.path.join(os.getcwd(), "test_roms", "SNE.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[0] = 11
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x204)

    def test_OP_5xy0(self):  # SE Vx, Vy: Skip next instruction if Vx = Vy
        path = os.path.join(os.getcwd(), "test_roms", "SE_Vx_Vy.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x204)

    def test_OP_6xkk(self):  # LD Vx, byte: Set Vx = kk
        path = os.path.join(os.getcwd(), "test_roms", "LD_Vx_byte.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0xAA)

    def test_OP_7xkk(self):  # ADD Vx, byte: Set Vx = Vx + kk
        path = os.path.join(os.getcwd(), "test_roms", "Add_Vx_byte.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 0x1
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0x1 + 0xAA)

    def test_OP_8xy0(self):  # LD Vx, Vy: Set Vx = Vy
        path = os.path.join(os.getcwd(), "test_roms", "Ld_Vx_Vy.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 0x1
        interpreter.registers[2] = 0xA
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0xA)

    def test_OP_8xy1(self):  # OR Vx, Vy: Set Vx = Vx OR Vy
        path = os.path.join(os.getcwd(), "test_roms", "OR.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 0b10101
        interpreter.registers[2] = 0b11000
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0b11101)

    def test_OP_8xy2(self):  # AND Vx, Vy: Set Vx = Vx AND Vy
        path = os.path.join(os.getcwd(), "test_roms", "AND.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 0b10101
        interpreter.registers[2] = 0b01100
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0b00100)

    def test_OP_8xy3(self):  # XOR Vx, Vy: Set Vx = Vx XOR Vy
        path = os.path.join(os.getcwd(), "test_roms", "XOR.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 0b10101
        interpreter.registers[2] = 0b01100
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0b11001)

    def test_OP_8xy4(self):  # ADD Vx, Vy: Set Vx = Vx + Vy, set VF = carry
        path = os.path.join(os.getcwd(), "test_roms", "ADD_Vx_Vy.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 255
        interpreter.registers[2] = 3
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 2)  # Should wrap
        self.assertEqual(interpreter.registers[0xF], 1)

    def test_OP_8xy5(self):  # SUB Vx, Vy: Set Vx = Vx - Vy, set VF = NOT borrow
        path = os.path.join(os.getcwd(), "test_roms", "SUB_Vx_Vy.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 3
        interpreter.registers[2] = 5
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 254)  # Should wrap
        self.assertEqual(interpreter.registers[0xF], 1)

    def test_OP_8xy6(self):  # SHR Vx {, Vy}: Set Vx = Vx SHR 1
        path = os.path.join(os.getcwd(), "test_roms", "SHR_VX.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 0b101
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0b10)  # Should wrap
        self.assertEqual(interpreter.registers[0xF], 1)

    def test_OP_8xy7(self):  # SUBN Vx, Vy: Set Vx = Vy - Vx, set VF = NOT borrow
        path = os.path.join(os.getcwd(), "test_roms", "SHR_VX.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 0b101
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0b10)  # Should wrap
        self.assertEqual(interpreter.registers[0xF], 1)

    def test_OP_8xyE(self):  # SHL Vx {, Vy}: Set Vx = Vx SHL 1
        path = os.path.join(os.getcwd(), "test_roms", "SHL_VX.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 129
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 2)  # Should wrap
        self.assertEqual(interpreter.registers[0xF], 1)

    def test_OP_9xy0(self):  # SNE Vx, Vy: Skip next instruction if Vx != Vy
        path = os.path.join(os.getcwd(), "test_roms", "SNE_Vx_Vy.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = 1
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x204)

    def test_OP_Annn(self):  # LD I, addr: Set I = nnn
        path = os.path.join(os.getcwd(), "test_roms", "LD_I_addr.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        self.assertEqual(interpreter.index_register, 0xABC)

    def test_OP_Bnnn(self):  # P V0, addr: Jump to location nnn + V0
        path = os.path.join(os.getcwd(), "test_roms", "P_V0_addr.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[0] = 0x4
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0xABC + 0x4)

    def test_OP_Cxkk(self):  # RND Vx, byte: Set Vx = random byte AND kk
        patch('Interpreter.getrandbits', lambda _: 0b10101010).start()
        path = os.path.join(os.getcwd(), "test_roms", "RND_Vx_byte.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 0b10101010 & 0b1100)
        patch.stopall()

    def test_OP_Dxyn(
            self):  # DRW Vx, Vy, nibble: Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision
        path = os.path.join(os.getcwd(), "test_roms", "DRW_Vx_Vy.ch8")
        BYTES_PER_DIGIT = 5
        interpreter = Interpreter(path)
        interpreter.index_register = 0x50
        interpreter.tick()
        guess = []
        for i in range(BYTES_PER_DIGIT):
            guess += interpreter.display[i * Interpreter.CHIP8_WIDTH: i * Interpreter.CHIP8_WIDTH + 8]
        correct = [int(j) for j in "".join([bin(i)[2:] for i in interpreter.memory[0x50: 0x50 + 5]])]
        self.assertEqual(guess, correct)

    def test_OP_Ex9E(self):  # SKP Vx: Skip next instruction if key with the value of Vx is pressed
        path = os.path.join(os.getcwd(), "test_roms", "SKP_Vx.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = interpreter.input_map['a']
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x202)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
        pygame.event.post(event)
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x206)

    def test_OP_ExA1(self):  # SKNP Vx: Skip next instruction if key with the value of Vx is not pressed
        path = os.path.join(os.getcwd(), "test_roms", "SKNP_Vx.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[1] = interpreter.input_map['a']
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
        pygame.event.post(event)
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x202)
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x206)

    def test_OP_Fx07(self):  # LD Vx, DT: Set Vx = delay timer value
        path = os.path.join(os.getcwd(), "test_roms", "Ld_Vx_DT.ch8")
        interpreter = Interpreter(path)
        interpreter.delay_timer = 99
        interpreter.tick()
        self.assertEqual(interpreter.registers[1], 99)

    def test_OP_Fx0A(self):  # LD Vx, K: Wait for a key press, store the value of the key in Vx
        path = os.path.join(os.getcwd(), "test_roms", "LD_Vx_k.ch8")
        interpreter = Interpreter(path)
        for _ in range(10):
            interpreter.tick()
            self.assertEqual(interpreter.program_counter, 0x200)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
        pygame.event.post(event)
        interpreter.tick()
        self.assertEqual(interpreter.program_counter, 0x202)
        self.assertEqual(interpreter.registers[1], interpreter.input_map['a'])

    def test_OP_Fx15(self):  # LD DT, Vx: Set delay timer = Vx
        path = os.path.join(os.getcwd(), "test_roms", "LD_DT.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        self.assertEqual(interpreter.delay_timer, interpreter.registers[1])

    def test_OP_Fx18(self):  # LD ST, Vx: Set sound timer = Vx
        path = os.path.join(os.getcwd(), "test_roms", "LD_ST.ch8")
        interpreter = Interpreter(path)
        interpreter.tick()
        self.assertEqual(interpreter.sound_timer, interpreter.registers[1])

    def test_OP_Fx1E(self):  # ADD I, Vx: Set I = I + Vx
        path = os.path.join(os.getcwd(), "test_roms", "ADD_I_Vx.ch8")
        interpreter = Interpreter(path)
        interpreter.index_register = 2
        interpreter.registers[1] = 3
        interpreter.tick()
        self.assertEqual(interpreter.index_register, 5)

    def test_OP_Fx29(self):  # LD F, Vx: Set I = location of sprite for digit Vx
        path = os.path.join(os.getcwd(), "test_roms", "LD_F_Vx.ch8")
        BYTES_PER_DIGIT = 5
        interpreter = Interpreter(path)
        interpreter.registers[1] = 3
        interpreter.tick()
        self.assertEqual(interpreter.index_register,
                         interpreter.FONT_SET_START_ADDRESS + (interpreter.registers[1] * BYTES_PER_DIGIT))

    def test_OP_Fx33(self):  # LD B, Vx: Store BCD representation of Vx in memory locations I, I+1, and I+2
        path = os.path.join(os.getcwd(), "test_roms", "LD_B_Vx.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[0xA] = 123
        interpreter.index_register = 0x300
        interpreter.tick()
        self.assertEqual(interpreter.memory[0x300:0x303], [1, 2, 3])

    def test_OP_Fx55(self):  # LD [I], Vx: Store registers V0 through Vx in memory starting at location I
        path = os.path.join(os.getcwd(), "test_roms", "LD_I_Vx.ch8")
        interpreter = Interpreter(path)
        interpreter.registers[:0xC] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        interpreter.index_register = interpreter.MEMORY_START_ADDRESS + 0x100
        interpreter.tick()
        start = interpreter.MEMORY_START_ADDRESS + 0x100
        end = start + 0xC
        self.assertEqual(interpreter.registers[:0xC], interpreter.memory[start:end])

    def test_OP_Fx65(self):  # LD Vx, [I]: Read registers V0 through Vx from memory starting at location I
        path = os.path.join(os.getcwd(), "test_roms", "LD_Vx_I.ch8")
        interpreter = Interpreter(path)
        interpreter.index_register = interpreter.MEMORY_START_ADDRESS
        interpreter.tick()
        correct = [0xFC, 0x65, 0x01, 0x23, 0x45, 0x67, 0x89, 0x10, 0x11, 0x12, 0x13, 0x14, 0x0, 0x0, 0x0, 0x0]
        self.assertEqual(interpreter.registers, correct)


if __name__ == '__main__':
    unittest.main()
