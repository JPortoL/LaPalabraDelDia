import pygame
import random

import palabras as words
from sprites import *
from settings import *
from palabras import *


class Game:
    def __init__(self, columnas):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.columnas = columnas
        self.create_word_list()
        self.fallos = FALLOS
        self.aciertos = ACIERTOS
    

    def draw_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)


    def create_word_list(self):
        options = {
            4: words.palabras4,
            5: words.palabras5,
            6: words.palabras6,
            7: words.palabras7,
            8: words.palabras8,
        }
        self.words_list = list(options[self.columnas])
        self.words_set = options[self.columnas]

    def new(self):
        self.word = random.choice(self.words_list).upper()
        print(self.word)
        self.text = ""
        self.current_row = 0
        self.tiles = []
        self.create_tiles()
        self.flip = True
        self.timer = 0

    def get_margin_x(self) -> int:
        return int((WIDTH - (self.columnas * (TILESIZE + GAPSIZE))) / 2)

    def create_tiles(self):
        for row in range(6):
            self.tiles.append([])
            for col in range(self.columnas):
                self.tiles[row].append(
                    Tile((col * (TILESIZE + GAPSIZE)) + self.get_margin_x(), (row * (TILESIZE + GAPSIZE)) + MARGIN_Y))

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.add_letter()

    def add_letter(self):
        # empty all the letter in the current row
        for tile in self.tiles[self.current_row]:
            tile.letter = ""

        # add the letters typed to the current row
        for i, letter in enumerate(self.text):
            self.tiles[self.current_row][i].letter = letter
            self.tiles[self.current_row][i].create_font()

    def draw_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.draw(self.screen)
    
    def mostrar_puntacion(self):
        # Agrega la visualización de aciertos y fallos
        self.draw_text(f'Aciertos: {self.aciertos}', pygame.font.Font(None, 36), WHITE, WIDTH // 10, 40)
        self.draw_text(f'Fallos: {self.fallos}', pygame.font.Font(None, 36), WHITE, WIDTH // 10, 80)

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.draw_tiles()
        self.mostrar_puntacion()
        pygame.display.flip()

    def row_animation(self):
        # row shaking if not enough letters is inputted
        self.not_enough_letters = True
        start_pos = self.tiles[0][0].x
        amount_move = 4
        move = 3
        screen_copy = self.screen.copy()
        screen_copy.fill(BGCOLOUR)
        for row in self.tiles:
            for tile in row:
                if row != self.tiles[self.current_row]:
                    tile.draw(screen_copy)

        while True:
            while self.tiles[self.current_row][0].x < start_pos + amount_move:
                self.screen.blit(screen_copy, (0, 0))
                for tile in self.tiles[self.current_row]:
                    tile.x += move
                    tile.draw(self.screen)
                self.clock.tick(FPS)
                pygame.display.flip()

            while self.tiles[self.current_row][0].x > start_pos - amount_move:
                self.screen.blit(screen_copy, (0, 0))
                for tile in self.tiles[self.current_row]:
                    tile.x -= move
                    tile.draw(self.screen)
                self.clock.tick(FPS)
                pygame.display.flip()

            amount_move -= 2
            if amount_move < 0:
                break

    def box_animation(self):
        # tile scale animation for every letter inserted
        for tile in self.tiles[self.current_row]:
            if tile.letter == "":
                screen_copy = self.screen.copy()
                for start, end, step in ((0, 6, 1), (0, -6, -1)):
                    for size in range(start, end, 2 * step):
                        self.screen.blit(screen_copy, (0, 0))
                        tile.x -= size
                        tile.y -= size
                        tile.width += size * 2
                        tile.height += size * 2
                        surface = pygame.Surface((tile.width, tile.height))
                        surface.fill(BGCOLOUR)
                        self.screen.blit(surface, (tile.x, tile.y))
                        tile.draw(self.screen)
                        pygame.display.flip()
                        self.clock.tick(FPS)
                    self.add_letter()
                break

    def reveal_animation(self, tile, colour):
        # reveal colours animation when user input the whole word
        screen_copy = self.screen.copy()

        while True:
            surface = pygame.Surface((tile.width + 5, tile.height + 5))
            surface.fill(BGCOLOUR)
            screen_copy.blit(surface, (tile.x, tile.y))
            self.screen.blit(screen_copy, (0, 0))
            if self.flip:
                tile.y += 6
                tile.height -= 12
                tile.font_y += 4
                tile.font_height = max(tile.font_height - 8, 0)
            else:
                tile.colour = colour
                tile.y -= 6
                tile.height += 12
                tile.font_y -= 4
                tile.font_height = min(tile.font_height + 8, tile.font_size)
            if tile.font_height == 0:
                self.flip = False

            tile.draw(self.screen)
            pygame.display.update()
            self.clock.tick(FPS)

            if tile.font_height == tile.font_size:
                self.flip = True
                break

    def check_letters(self):
        copy_word = [x for x in self.word]
        for i, user_letter in enumerate(self.text):
            colour = LIGHTGREY
            for j, letter in enumerate(copy_word):
                if user_letter == letter:
                    colour = YELLOW
                    if i == j:
                        colour = GREEN
                    copy_word[j] = ""
                    break
            self.reveal_animation(self.tiles[self.current_row][i], colour)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(self.text) == self.columnas:
                        if str.lower(self.text) in self.words_set:
                            # check all letters
                            self.check_letters()
                            if self.text == self.word or self.current_row + 1 == 6:
                                # player lose, lose message is sent
                                if self.text != self.word:
                                    self.fallos += 1
                                    global FALLOS
                                    FALLOS += 1
                                    gano = False
                                # player win, send win message
                                else:
                                    self.aciertos += 1
                                    global ACIERTOS
                                    ACIERTOS += 1
                                    gano = True

                                # restart the game
                                print(f'FALLOS: {self.fallos} ACIERTOS: {self.aciertos}')
                                self.playing = False
                                self.end_screen(gano)
                                break

                            self.current_row += 1
                            self.text = ""
                        else:
                            self.row_animation()

                    else:
                        # row animation, not enough letters message
                        self.row_animation()

                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

                else:
                    if len(self.text) < self.columnas and event.unicode.isalpha():
                        self.text += event.unicode.upper()
                        self.box_animation()

    def end_screen(self, gano):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
            self.screen.fill(BGCOLOUR)
            if gano:
                self.draw_text(f'¡Felicitaciones, Ganaste!', pygame.font.Font(None, 36), WHITE, WIDTH * 0.84, 40)
                self.draw_text(f'¿Enter para jugar otra?', pygame.font.Font(None, 36), WHITE, WIDTH * 0.84, 80)
            else:
                self.draw_text(f'Lee un diccionario, ¡bruto!', pygame.font.Font(None, 30), WHITE, WIDTH * 0.84, 40)
                self.draw_text(f'Enter para seguir dando pena', pygame.font.Font(None, 30), WHITE, WIDTH * 0.84, 80)
            self.mostrar_puntacion()
            self.draw_tiles()
            pygame.display.flip()

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.selected_difficulty = None

    def draw_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def mostrar_puntacion(self):
        global ACIERTOS
        global FALLOS
        # Agrega la visualización de aciertos y fallos
        self.draw_text(f'Aciertos: {ACIERTOS}', pygame.font.Font(None, 36), WHITE, WIDTH // 10, 40)
        self.draw_text(f'Fallos: {FALLOS}', pygame.font.Font(None, 36), WHITE, WIDTH // 10, 80)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    for i, difficulty in enumerate([4, 5, 6, 7, 8]):
                        button_rect = pygame.Rect(300, 100 + i * 50, 200, 40)
                        if button_rect.collidepoint(x, y):
                            self.selected_difficulty = difficulty
                            return self.selected_difficulty  # Retorna la dificultad seleccionada
            self.screen.fill(BGCOLOUR)
            self.draw_text("Seleccione la Dificultad", self.font, WHITE, WIDTH // 2, 50)
            self.mostrar_puntacion()

            for i, difficulty in enumerate([4, 5, 6, 7, 8]):
                pygame.draw.rect(self.screen, WHITE, (300, 100 + i * 50, 200, 40))
                self.draw_text(str(difficulty), self.font, BLACK, 400, 120 + i * 50)

            pygame.display.flip()
            self.clock.tick(30)

while True:
    main_menu = MainMenu()
    columnas_seleccionadas = main_menu.run()

    game = Game(columnas_seleccionadas)
    game.new()
    game.run()
