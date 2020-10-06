import os
import unittest
from unittest import skip
from unittest.mock import patch
from Interpreter import Interpreter
from tests_utils import *


class Test(unittest.TestCase):

    def setUp(self):
        patch('pygame.display.set_mode', lambda _ : None).start()
        patch('pygame.display.flip', lambda : None).start()

    def test_loads_rom_correctly(self):
        path = os.path.join(os.getcwd(), "test_roms", "rand_512_bytes.ch8")
        num_bytes = 512
        create_random_hex_file(num_bytes, path)
        hex_dump = None
        with open(path, "rb") as file:
            contents = file.read()
            hex_dump = [int('{:02X}'.format(b), 16) for b in contents]

        interpreter = Interpreter(path)
        for idx, i in enumerate(interpreter.memory[Interpreter.MEMORY_START_ADDRESS: Interpreter.MEMORY_START_ADDRESS+num_bytes]):

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

    @skip('Not implemented')
    def test_OP_6xkk(self):  # LD Vx, byte: Set Vx = kk
        pass

    @skip('Not implemented')
    def test_OP_7xkk(self):  # ADD Vx, byte: Set Vx = Vx + kk
        pass

    @skip('Not implemented')
    def test_OP_8xy0(self):  # LD Vx, Vy: Set Vx = Vy
        pass

    @skip('Not implemented')
    def test_OP_8xy1(self):  # OR Vx, Vy: Set Vx = Vx OR Vy
        pass

    @skip('Not implemented')
    def test_OP_8xy2(self):  # AND Vx, Vy: Set Vx = Vx AND Vy
        pass

    @skip('Not implemented')
    def test_OP_8xy3(self):  # XOR Vx, Vy: Set Vx = Vx XOR Vy
        pass

    @skip('Not implemented')
    def test_OP_8xy4(self):  # ADD Vx, Vy: Set Vx = Vx + Vy, set VF = carry
        pass

    @skip('Not implemented')
    def test_OP_8xy5(self):  # SUB Vx, Vy: Set Vx = Vx - Vy, set VF = NOT borrow
        pass

    @skip('Not implemented')
    def test_OP_8xy6(self):  # SHR Vx {, Vy}: Set Vx = Vx SHR 1
        pass

    @skip('Not implemented')
    def test_OP_8xy7(self):  # SUBN Vx, Vy: Set Vx = Vy - Vx, set VF = NOT borrow
        pass

    @skip('Not implemented')
    def test_OP_8xyE(self):  # SHL Vx {, Vy}: Set Vx = Vx SHL 1
        pass

    @skip('Not implemented')
    def test_OP_9xy0(self):  # SNE Vx, Vy: Skip next instruction if Vx != Vy
        pass

    @skip('Not implemented')
    def test_OP_Annn(self):  # LD I, addr: Set I = nnn
        pass

    @skip('Not implemented')
    def test_OP_Bnnn(self):  # P V0, addr: Jump to location nnn + V0
        pass

    @skip('Not implemented')
    def test_OP_Cxkk(self):  # RND Vx, byte: Set Vx = random byte AND kk
        pass

    @skip('Not implemented')
    def test_OP_Dxyn(self):  # DRW Vx, Vy, nibble: Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision
        pass

    @skip('Not implemented')
    def test_OP_Ex9E(self):  # SKP Vx: Skip next instruction if key with the value of Vx is pressed
        pass

    @skip('Not implemented')
    def test_OP_ExA1(self):  # SKNP Vx: Skip next instruction if key with the value of Vx is not pressed
        pass

    @skip('Not implemented')
    def test_OP_Fx07(self):  # LD Vx, DT: Set Vx = delay timer value
        pass

    @skip('Not implemented')
    def test_OP_Fx0A(self):  # LD Vx, K: Wait for a key press, store the value of the key in Vx
        pass

    @skip('Not implemented')
    def test_OP_Fx15(self):  # LD DT, Vx: Set delay timer = Vx
        pass

    @skip('Not implemented')
    def test_OP_Fx18(self):  # LD ST, Vx: Set sound timer = Vx
        pass

    @skip('Not implemented')
    def test_OP_Fx1E(self):  # ADD I, V: Set I = I + Vx
        pass

    @skip('Not implemented')
    def test_OP_Fx29(self):  # LD F, Vx: Set I = location of sprite for digit Vx
        pass

    @skip('Not implemented')
    def test_OP_Fx33(self):  # LD B, Vx: Store BCD representation of Vx in memory locations I, I+1, and I+2
        pass

    @skip('Not implemented')
    def test_OP_Fx55(self):  # LD [I], Vx: Store registers V0 through Vx in memory starting at location I
        pass

    @skip('Not implemented')
    def test_OP_Fx65(self):  # LD Vx, [I]: Read registers V0 through Vx from memory starting at location I
        pass


if __name__ == '__main__':
    unittest.main()