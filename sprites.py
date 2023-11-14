import pygame
from configuraciones import *


class Tile:
    def __init__(self, x, y, letter="", colour=None):
        self.x, self.y = x, y
        self.letter = letter
        self.colour = colour
        self.width, self.height = TILESIZE, TILESIZE
        self.font_size = int(60 * (TILESIZE / 100))
        self.create_font()

    def create_font(self):
        font = pygame.font.SysFont("Consolas", self.font_size)
        self.render_letter = font.render(self.letter, True, WHITE)
        self.font_width, self.font_height = font.size(self.letter)

    def draw(self, screen):
        if self.colour is None:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        else:
            pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height))

        if self.letter != "":
            self.font_x = self.x + (self.width / 2) - (self.font_width / 2)
            self.font_y = self.y + (self.height / 2) - (self.font_height / 2)
            letter = pygame.transform.scale(self.render_letter, (self.font_width, self.font_height))
            screen.blit(letter, (self.font_x, self.font_y))
