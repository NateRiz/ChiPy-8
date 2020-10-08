from Interpreter import Interpreter
import pygame


class Debugger:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.screen = interpreter._screen
        self.x = Interpreter.SCREEN_WIDTH
        self.y = 0
        self.width = Interpreter.DEBUG_WINDOW_SIZE
        self.height = Interpreter.SCREEN_HEIGHT
        self.font_size = 18
        self.font = pygame.font.SysFont("monospace", self.font_size)

    def execute(self):
        while True:
            self.interpreter.tick()
            self.draw()


    def draw(self):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (30, 255, 30)
        buffer = 8
        formatted = self.get_formatted()

        rect = pygame.draw.rect(self.screen, BLACK, (self.x, self.y, self.width, self.height))

        current_y = self.y

        for i, line in enumerate(formatted.split("\n")):
            img = self.font.render(line, True, WHITE)
            self.screen.blit(img, (self.x + buffer, self.y + current_y))
            current_y += buffer + self.font_size

        line = self.font.render("Stk:______", True, WHITE)
        self.screen.blit(line, (self.x + buffer, self.y + current_y))
        current_y += buffer + self.font_size

        for i, line in enumerate(reversed(self.interpreter.stack)):
            color = WHITE
            if self.interpreter.stack_pointer == 0xF-i:
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
        return out.format(
            hex(i.program_counter), hex(i.index_register),
            hex(i.delay_timer), hex(i.sound_timer),
            *[f'0x{hex(j)[2:].ljust(2, "0")}' for j in i.registers],
            hex(i.stack_pointer), hex(i.op_code)
        )


out = \
    """PC:{} IC:{}
DT:{} ST:{}
R0:{} R8:{}
R1:{} R9:{}
R2:{} RA:{}
R3:{} RB:{}
R4:{} RC:{}
R5:{} RD:{}
R6:{} RE:{}
R7:{} RF:{}
SP:{} OP:{}
"""
