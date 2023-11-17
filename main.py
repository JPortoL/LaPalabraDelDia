import pygame
import random
from sprites import *
from configuraciones import *
from palabras import palabras4, palabras5, palabras6, palabras7, palabras8
from collections import deque


class Game:
    def __init__(self, columnas: int):
        pygame.init()
        # Se crea la configuración de pygame
        self.pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(titulo)
        self.clock = pygame.time.Clock()

        self.columnas = columnas
        self.cargar_palabras_del_diccionario()


    def cargar_palabras_del_diccionario(self):
        """
        Función que carga las palabras del diccionario dependiendo\
        de las columnas seleccionadas.
        """
        options = {
            4: palabras4,
            5: palabras5,
            6: palabras6,
            7: palabras7,
            8: palabras8,
        }

        # Se convierte el set a una lista O(N)
        self.words_list = list(options[self.columnas])
        self.words_set = options[self.columnas]

    def crear_tablero(self):
        """
        Función que genera el tablero del wordle y sus variables asociadas.
        """

        # Eficiencia O(1)
        self.palabra = random.choice(self.words_list).upper()
        print(self.palabra)
        self.dic_palabra = self.crear_diccionario_palabra()
        self.palabra_usuario = ""
        self.fila_actual = 0

        # Se crean las celdas del tablero
        self.celdas = []
        self.crear_celdas()
        self.flip = True

    def crear_diccionario_palabra(self):
        dictio = {}
        for i, letra in enumerate(self.palabra):
            try:
                dictio[letra]['indexes'].add(i)
            except:
                dictio[letra] = {'indexes': {i}, 'oranges': deque(), 'total': 0}
        return dictio

    def crear_celdas(self):
        """
        Función que pinta las casillas del tablero.
        """

        # Eficiencia O(N)
        for row in range(6):
            self.celdas.append([])
            # Por cada columna ingresada del usuario pinta 6 casillas
            for col in range(self.columnas):
                self.celdas[row].append(
                    Tile((col * (TILESIZE + GAPSIZE)) + self.calcular_margen_x(),
                         (row * (TILESIZE + GAPSIZE)) + MARGIN_Y))

    def calcular_margen_x(self) -> int:
        """
         Función que calcula la margen en x del tablero para centrarlo.
        """
        return int((WIDTH - (self.columnas * (TILESIZE + GAPSIZE))) / 2)

    def ejecutar_juego(self):
        """
        Función que ejecuta el juego.
        """
        self.jugando = True
        while self.jugando:
            self.clock.tick(FPS)
            self.validar_eventos()
            self.update()
            self.draw()

    def validar_eventos(self):
        """
        Función que válida los eventos del juego.
        """

        for event in pygame.event.get():
            # Se cierra el juego.
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            # Se escribe en el juego.
            if event.type == pygame.KEYDOWN:

                # Se presiona la tecla Enter
                if event.key == pygame.K_RETURN:
                    if len(self.palabra_usuario) == self.columnas:
                        # Se válida si la palabra exista en el diccionario
                        # Eficiencia O(1)'
                        if str.lower(self.palabra_usuario) in self.words_set:

                            # Se válidan los colores de las letras
                            self.validar_letras()
                            if self.palabra_usuario == self.palabra or self.fila_actual + 1 == 6:
                                if self.palabra_usuario != self.palabra:
                                    # Se suma un fallo si la palabra es incorrecta
                                    global fallos
                                    fallos += 1
                                    gano = False
                                else:
                                    # Se suma un acierto si la palabra es incorrecta
                                    global aciertos
                                    aciertos += 1
                                    gano = True

                                # restart the game
                                print(f'FALLOS: {fallos} ACIERTOS: {aciertos}')
                                self.jugando = False
                                self.finalizar_pantalla(gano)
                                break

                            # En caso contrario de que no adivine la palabra o no\
                            # sea la última fila debe continuar a la siguiente palabra.
                            self.fila_actual += 1
                            self.palabra_usuario = ""
                        else:
                            self.row_animation()
                    else:
                        self.row_animation()

                # Se presiona la tecla borrar
                elif event.key == pygame.K_BACKSPACE:
                    # Se elimina la última letra ingresada
                    # Eficiencia O(1)
                    self.palabra_usuario = self.palabra_usuario[:-1]

                # Se presiona cualquier otra tecla.
                else:
                    if len(self.palabra_usuario) < self.columnas and event.unicode.isalpha():
                        self.palabra_usuario += event.unicode.upper()
                        self.box_animation()

    def validar_letras(self):
        """
        La función válida cada letra de la palabra ingresada por el usuario\
        la eficiencia general es O(N)
        """
        # Eficiencia de la función O(N)
        for i, user_letter in enumerate(self.palabra_usuario):
            colour = LIGHTGREY

            # Caso en que la letra esté en la palabra random
            if user_letter in self.dic_palabra:
                # Caso en que la letra esté en la posición correcta
                if i in self.dic_palabra[user_letter]['indexes']:
                    colour = GREEN
                    if self.dic_palabra[user_letter]['total'] + 1 > len(self.dic_palabra[user_letter]['indexes']):
                        self.reveal_animation(
                            self.celdas[self.fila_actual][self.dic_palabra[user_letter]['oranges'].popleft()],
                            LIGHTGREY)
                # Caso en que la letra no esté en la posición correcta
                else:
                    if self.dic_palabra[user_letter]['total'] + 1 <= len(self.dic_palabra[user_letter]['indexes']):
                        colour = YELLOW
                        self.dic_palabra[user_letter]['oranges'].appendleft(i)
                self.dic_palabra[user_letter]['total'] += 1

            self.reveal_animation(self.celdas[self.fila_actual][i], colour)
        self.dic_palabra = self.crear_diccionario_palabra()

    ### MÉTODOS DE LA INTERFAZ
    # Función que dibuja el texto en la pantalla
    def draw_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.pantalla.blit(text_surface, text_rect)

    def mostrar_puntacion(self):
        global aciertos
        global fallos
        # Agrega la visualización de aciertos y fallos
        self.draw_text(f'Aciertos: {aciertos}', pygame.font.Font(None, 30), WHITE, WIDTH // 15, 40)
        self.draw_text(f'Fallos: {fallos}', pygame.font.Font(None, 30), WHITE, WIDTH // 15, 80)

    def draw_tiles(self):
        for row in self.celdas:
            for tile in row:
                tile.draw(self.pantalla)

    def draw(self):
        self.pantalla.fill(BGCOLOUR)
        self.draw_tiles()
        self.mostrar_puntacion()

        pygame.display.flip()

    def row_animation(self):
        # row shaking if not enough letters is inputted
        self.not_enough_letters = True
        start_pos = self.celdas[0][0].x
        amount_move = 4
        move = 3
        screen_copy = self.pantalla.copy()
        screen_copy.fill(BGCOLOUR)
        for row in self.celdas:
            for tile in row:
                if row != self.celdas[self.fila_actual]:
                    tile.draw(screen_copy)

        while True:
            while self.celdas[self.fila_actual][0].x < start_pos + amount_move:
                self.pantalla.blit(screen_copy, (0, 0))
                for tile in self.celdas[self.fila_actual]:
                    tile.x += move
                    tile.draw(self.pantalla)
                self.clock.tick(FPS)
                pygame.display.flip()

            while self.celdas[self.fila_actual][0].x > start_pos - amount_move:
                self.pantalla.blit(screen_copy, (0, 0))
                for tile in self.celdas[self.fila_actual]:
                    tile.x -= move
                    tile.draw(self.pantalla)
                self.clock.tick(FPS)
                pygame.display.flip()

            amount_move -= 2
            if amount_move < 0:
                break

    def update(self):
        """
        Esta función se encarga de refrescar las actualizaciones del tablero.
        """
        self.add_letter()

    def add_letter(self):
        for celda in self.celdas[self.fila_actual]:
            celda.letter = ""

        for i, letter in enumerate(self.palabra_usuario):
            self.celdas[self.fila_actual][i].letter = letter
            self.celdas[self.fila_actual][i].create_font()

    def box_animation(self):
        # tile scale animation for every letter inserted
        for tile in self.celdas[self.fila_actual]:
            if tile.letter == "":
                screen_copy = self.pantalla.copy()
                for start, end, step in ((0, 6, 1), (0, -6, -1)):
                    for size in range(start, end, 2 * step):
                        self.pantalla.blit(screen_copy, (0, 0))
                        tile.x -= size
                        tile.y -= size
                        tile.width += size * 2
                        tile.height += size * 2
                        surface = pygame.Surface((tile.width, tile.height))
                        surface.fill(BGCOLOUR)
                        self.pantalla.blit(surface, (tile.x, tile.y))
                        tile.draw(self.pantalla)
                        pygame.display.flip()
                        self.clock.tick(FPS)
                    self.add_letter()
                break

    def reveal_animation(self, tile, colour):
        # reveal colours animation when user input the whole word
        screen_copy = self.pantalla.copy()

        while True:
            surface = pygame.Surface((tile.width + 5, tile.height + 5))
            surface.fill(BGCOLOUR)
            screen_copy.blit(surface, (tile.x, tile.y))
            self.pantalla.blit(screen_copy, (0, 0))
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

            tile.draw(self.pantalla)
            pygame.display.update()
            self.clock.tick(FPS)

            if tile.font_height == tile.font_size:
                self.flip = True
                break

    def finalizar_pantalla(self, gano):
        """
        Se queda esperando hasta que el usuario cierra el juego o\
        preciona enter para continuar jugando.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return

            self.pantalla.fill(BGCOLOUR)
            if gano:
                self.draw_text(f'¡Felicitaciones, Ganaste!', pygame.font.Font(None, 36), WHITE, WIDTH * 0.84, 40)
                self.draw_text(f'¿Enter para jugar otra?', pygame.font.Font(None, 36), WHITE, WIDTH * 0.84, 80)
            else:
                self.draw_text(f'Lee un diccionario, ¡bruto!', pygame.font.Font(None, 30), WHITE, WIDTH * 0.84, 40)
                self.draw_text(f'Enter para seguir dando pena', pygame.font.Font(None, 30), WHITE, WIDTH * 0.84, 80)
                self.draw_text(f'Era {self.palabra}', pygame.font.Font(None, 30), WHITE, WIDTH * 0.84, 120)
            self.mostrar_puntacion()
            self.draw_tiles()
            pygame.display.flip()


class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(titulo)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.selected_difficulty = None

    # Función que dibuja el texto en la pantalla
    def draw_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def mostrar_puntacion(self):
        global aciertos
        global fallos
        # Agrega la visualización de aciertos y fallos
        self.draw_text(f'Aciertos: {aciertos}', pygame.font.Font(None, 30), WHITE, WIDTH // 15, 40)
        self.draw_text(f'Fallos: {fallos}', pygame.font.Font(None, 30), WHITE, WIDTH // 15, 80)

    # Función que ejecuta el menú principal
    def run(self):
        while True:
            for event in pygame.event.get():
                # Si se cierra la ventana, se acaba todo
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)

                # Si se presiona el mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Se obtiene la posición del mouse
                    x, y = pygame.mouse.get_pos()

                    # Se válida si la posición del mouse está dentro de los botones
                    # eficiencia 0=num dificuiltades

                    for i, difficulty in enumerate([4, 5, 6, 7, 8]):
                        button_rect = pygame.Rect(400, 100 + i * 50, 200, 40)
                        if button_rect.collidepoint(x, y):
                            self.selected_difficulty = difficulty
                            # Retorna la dificultad seleccionada
                            return self.selected_difficulty  
            # Se dibuja el menú principal
            self.screen.fill(BGCOLOUR)
            self.draw_text("Seleccione la Dificultad", self.font, WHITE, WIDTH // 2, 50)
            self.mostrar_puntacion()
            # Se dibujan los botones
            for i, difficulty in enumerate([4, 5, 6, 7, 8]):
                pygame.draw.rect(self.screen, WHITE, (400, 100 + i * 50, 200, 40))
                self.draw_text(str(difficulty), self.font, BLACK, WIDTH // 2, 120 + i * 50)

            pygame.display.flip()
            self.clock.tick(30)

while True:
    main_menu = MainMenu()
    columnas_seleccionadas = main_menu.run()

    game = Game(columnas_seleccionadas)
    game.crear_tablero()
    game.ejecutar_juego()
