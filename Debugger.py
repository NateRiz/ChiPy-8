from Interpreter import Interpreter
import pygame
from enum import Enum
from time import sleep


class STATE(Enum):
    PLAY = 0
    STEP = 1
    PAUSE = 2


class Debugger:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.screen = interpreter._screen
        self.x = Interpreter.SCREEN_WIDTH
        self.y = 0
        self.text_y_start = 0
        self.width = Interpreter.DEBUG_WINDOW_SIZE
        self.height = Interpreter.SCREEN_HEIGHT
        self.font_size = 18
        self.font = pygame.font.SysFont("monospace", self.font_size)

        self.state = STATE.PAUSE
        self.pause = None
        self.step = None
        self.play = None
        self.setup_buttons()

    def execute(self):
        while True:
            self.get_input()
            if self.state == STATE.PAUSE:
                sleep(0.05)
            else:
                self.interpreter.tick()
            if self.state == STATE.STEP:
                self.state = STATE.PAUSE
            self.draw()

    def setup_buttons(self):
        buffer = 8
        button_size = 24
        x = self.x + buffer
        y = self.y + buffer
        self.pause = pygame.rect.Rect(x, y, button_size, button_size)

        x += buffer + button_size
        self.step = pygame.rect.Rect(x, y, button_size, button_size)

        x += buffer + button_size
        self.play = pygame.rect.Rect(x, y, button_size, button_size)

        self.text_y_start = y + button_size + buffer

    def get_input(self):
        event = pygame.event.get(eventtype=pygame.MOUSEBUTTONDOWN)
        if event:
            pos = event[0].pos
            if self.pause.collidepoint(pos):
                self.state = STATE.PAUSE
            elif self.step.collidepoint(pos) and self.state == STATE.PAUSE:
                self.state = STATE.STEP
            elif self.play.collidepoint(pos):
                self.state = STATE.PLAY

    def draw(self):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (60, 255, 60)
        RED = (255, 90, 90)
        YELLOW = (255, 255, 60)
        buffer = 8
        formatted = self.get_formatted()

        # fill console black
        rect = pygame.draw.rect(self.screen, BLACK, (self.x, self.y, self.width, self.height))

        # Draw buttons
        colors = (WHITE, YELLOW)
        color = WHITE
        if self.pause.collidepoint(pygame.mouse.get_pos()):
            color = YELLOW
        pygame.draw.rect(self.screen, color, self.pause, 1)
        pygame.draw.rect(self.screen, RED, (self.pause.centerx - 5, self.pause.y + 5, 2, self.pause.height - 10), 3)
        pygame.draw.rect(self.screen, RED, (self.pause.centerx + 3, self.pause.y + 5, 2, self.pause.height - 10), 3)

        color = WHITE
        if self.step.collidepoint(pygame.mouse.get_pos()):
            color = YELLOW
        pygame.draw.rect(self.screen, color, self.step, 1)
        gt = self.font.render(">", True, RED)
        self.screen.blit(gt, (self.step.centerx - gt.get_size()[0] // 2, self.step.centery - gt.get_size()[1] // 2))

        color = WHITE
        if self.play.collidepoint(pygame.mouse.get_pos()):
            color = YELLOW
        pygame.draw.rect(self.screen, color, self.play, 1)
        gt = self.font.render(">", True, GREEN)
        self.screen.blit(gt, (self.play.centerx - gt.get_size()[0] // 2, self.play.centery - gt.get_size()[1] // 2))

        current_y = self.text_y_start

        for i, line in enumerate(formatted.split("\n")):
            img = self.font.render(line, True, WHITE)
            self.screen.blit(img, (self.x + buffer, self.y + current_y))
            current_y += buffer + self.font_size

        line = self.font.render("Stk:______", True, WHITE)
        self.screen.blit(line, (self.x + buffer, self.y + current_y))
        current_y += buffer + self.font_size

        for i, line in enumerate(reversed(self.interpreter.stack)):
            color = WHITE
            if self.interpreter.stack_pointer == 0xF - i:
                color = GREEN
            img = self.font.render(F"{hex(0xF - i)[2:]}. |{hex(line)}|", True, color)
            self.screen.blit(img, (self.x + buffer, self.y + current_y))
            current_y += (buffer + self.font_size)

        line = self.font.render("    ------", True, WHITE)
        self.screen.blit(line, (self.x + buffer, self.y + current_y))
        current_y += buffer + self.font_size

        pygame.display.update(rect)

    def get_formatted(self):
        i = self.interpreter
        reg = [f'0x{hex(j)[2:].rjust(2, "0")}' for j in i.registers]
        op_code = (i.memory[i.program_counter] << 8) | i.memory[i.program_counter + 1]
        op_name = op_map[(op_code & 0xF000) >> 12](op_code)

        result = out.format(
            hex(op_code), op_code_map[op_name[3:]],
            reg[0], reg[8], hex(i.program_counter),
            reg[1], reg[9], hex(i.index_register),
            reg[2], reg[0xA], hex(i.delay_timer),
            reg[3], reg[0xB], hex(i.sound_timer),
            reg[4], reg[0xC], hex(i.stack_pointer),
            reg[5], reg[0xD],
            reg[6], reg[0xE],
            reg[7], reg[0xF]
        )
        return result


out = \
    """OP CODE:{} - {}
-----------------
R0:{} R8:{} | PC:{}
R1:{} R9:{} | IC:{}
R2:{} RA:{} | DT:{}
R3:{} RB:{} | ST:{}
R4:{} RC:{} | SP:{}
R5:{} RD:{} |
R6:{} RE:{} |
R7:{} RF:{} |
"""

op_code_map = {
    "0nnn": "SYS addr",
    "00E0": "CLS",
    "00EE": "RET",
    "1nnn": "JP addr",
    "2nnn": "CALL addr",
    "3xkk": "SE Vx, byte",
    "4xkk": "SNE Vx, byte",
    "5xy0": "SE Vx, Vy",
    "6xkk": "LD Vx, byte",
    "7xkk": "ADD Vx, byte",
    "8xy0": "LD Vx, Vy",
    "8xy1": "OR Vx, Vy",
    "8xy2": "AND Vx, Vy",
    "8xy3": "XOR Vx, Vy",
    "8xy4": "ADD Vx, Vy",
    "8xy5": "SUB Vx, Vy",
    "8xy6": "SHR Vx {, Vy}",
    "8xy7": "SUBN Vx, Vy",
    "8xyE": "SHL Vx {, Vy}",
    "9xy0": "SNE Vx, Vy",
    "Annn": "LD I, addr",
    "Bnnn": "JP V0, addr",
    "Cxkk": "RND Vx, byte",
    "Dxyn": "DRW Vx, Vy, nibble",
    "Ex9E": "SKP Vx",
    "ExA1": "SKNP Vx",
    "Fx07": "LD Vx, DT",
    "Fx0A": "LD Vx, K",
    "Fx15": "LD DT, Vx",
    "Fx18": "LD ST, Vx",
    "Fx1E": "ADD I, Vx",
    "Fx29": "LD F, Vx",
    "Fx33": "LD B, Vx",
    "Fx55": "LD [I], Vx",
    "Fx65": "LD Vx, [I]",
}

_op_map0 = {
    0x0: "OP_00E0",
    0xE: "OP_00EE"
}

_op_map8 = {
    0x0: "OP_8xy0",
    0x1: "OP_8xy1",
    0x2: "OP_8xy2",
    0x3: "OP_8xy3",
    0x4: "OP_8xy4",
    0x5: "OP_8xy5",
    0x6: "OP_8xy6",
    0x7: "OP_8xy7",
    0xE: "OP_8xyE"
}

_op_mapE = {
    0xE: "OP_Ex9E",
    0x1: "OP_ExA1"
}

_op_mapF = {
    0x07: "OP_Fx07",
    0x0A: "OP_Fx0A",
    0x15: "OP_Fx15",
    0x18: "OP_Fx18",
    0x1E: "OP_Fx1E",
    0x29: "OP_Fx29",
    0x33: "OP_Fx33",
    0x55: "OP_Fx55",
    0x65: "OP_Fx65"
}


def __op_map0(n): return _op_map0[n & 0x000F]


def __op_map8(n): return _op_map8[n & 0x000F]


def __op_mapE(n): return _op_mapE[n & 0x000F]


def __op_mapF(n): return _op_mapF[n & 0x00FF]


op_map = {
    0x0: lambda n: __op_map0(n),
    0x1: lambda _: "OP_1nnn",
    0x2: lambda _: "OP_2nnn",
    0x3: lambda _: "OP_3xkk",
    0x4: lambda _: "OP_4xkk",
    0x5: lambda _: "OP_5xy0",
    0x6: lambda _: "OP_6xkk",
    0x7: lambda _: "OP_7xkk",
    0x8: lambda n: __op_map8(n),
    0x9: lambda _: "OP_9xy0",
    0xA: lambda _: "OP_Annn",
    0xB: lambda _: "OP_Bnnn",
    0xC: lambda _: "OP_Cxkk",
    0xD: lambda _: "OP_Dxyn",
    0xE: lambda n: __op_mapE(n),
    0xF: lambda n: __op_mapF(n),
}
