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

        self.state = STATE.PLAY
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

        x+=buffer+button_size
        self.step = pygame.rect.Rect(x, y, button_size, button_size)

        x+=buffer+button_size
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
        buffer = 8
        formatted = self.get_formatted()

        #fill console black
        rect = pygame.draw.rect(self.screen, BLACK, (self.x, self.y, self.width, self.height))

        #Draw buttons
        pygame.draw.rect(self.screen, WHITE, self.pause, 1)
        pygame.draw.rect(self.screen, RED, (self.pause.centerx - 5, self.pause.y + 5, 2, self.pause.height-10), 3)
        pygame.draw.rect(self.screen, RED, (self.pause.centerx + 3, self.pause.y + 5, 2, self.pause.height-10), 3)

        pygame.draw.rect(self.screen, WHITE, self.step, 1)
        gt = self.font.render(">", True, RED)
        self.screen.blit(gt, (self.step.centerx-gt.get_size()[0]//2, self.step.centery-gt.get_size()[1]//2))

        pygame.draw.rect(self.screen, WHITE, self.play, 1)
        gt = self.font.render(">", True, GREEN)
        self.screen.blit(gt, (self.play.centerx-gt.get_size()[0]//2, self.play.centery-gt.get_size()[1]//2))

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
