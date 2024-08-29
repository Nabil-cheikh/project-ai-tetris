from IA_Tetris.params import *
from IA_Tetris.utils import TetrisInfos
import numpy as np
import time

class Tetris():# Au final on va pas faire d'héritage, c'est trop compliqué

    def __init__(self, pyboy, env):
        self.pyboy = pyboy
        self.tetris = self.pyboy.game_wrapper
        self.env = env
        self.play_time = 0
        self.delta_time = 0
        self.time_scale = 1
        self._is_new_tetromino = True
        self.spawner_area = self.game_area()[1:3,3:7] # The spawner area is the area of shape (2, 4) on top of the game area where new tetropino spawn
        self._last_spawner_area = np.zeros((2, 4), dtype='int8')
        self._current_tetromino = self.next_tetromino()
        self._game_area_only = self.game_area()
        self._last_game_area = np.zeros(self.game_area().shape, dtype='int8')
        self.current_tetromino_area = np.zeros(self.game_area().shape, dtype='uint8')
        self.last_current_tetromino_area = np.zeros(self.game_area().shape, dtype='uint8')
        self.total_tetromino_used = 0
        self.fps = 0
        self._last_time_fps = time.time()
        self.score = 0
        self.lines = 0
        self.level = 0
        self.frames_until_tetro_spawn = 0

    def game_area_mapping(self):
        self.tetris.game_area_mapping(self.tetris.mapping_compressed, 0)

    def start_game(self, timer_div=None):
        self.tetris.start_game(timer_div)

    def set_current_tetromino(self, tetromino):
        self._current_tetromino = tetromino

    def current_tetromino(self) -> str:
        '''Form of the current tetromino: O, Z, S, L, J, T, I'''
        return self._current_tetromino

    def next_tetromino(self):
        return self.tetris.next_tetromino()

    def game_area(self):
        return self.tetris.game_area()

    def set_game_area_only(self):
        self._game_area_only = self._last_game_area

    def game_area_only(self):
        '''Game grid without the current tetromino'''
        return self._game_area_only

    def game_over(self):
        # Un poil plus rapide que le tetris.game_over() de base, qui attend que tout l'écran soit recouvert de "8"
        return 8 in self.game_area()
        # return self.tetris.game_over()

    def reset_game(self, timer_div=None):
        self.tetris.reset_game(timer_div)
        self.play_time = 0
        self.delta_time = 0
        self.time_scale = 1
        self._is_new_tetromino = True
        self.spawner_area = self.game_area()[1:3,3:7] # The spawner area is the area of shape (2, 4) on top of the game area where new tetropino spawn
        self._last_spawner_area = np.zeros((2, 4), dtype='int8')
        self._current_tetromino = self.next_tetromino()
        self._game_area_only = self.game_area()
        self._last_game_area = np.zeros(self.game_area().shape, dtype='int8')
        self.current_tetromino_area = np.zeros(self.game_area().shape, dtype='uint8')
        self.last_current_tetromino_area = np.zeros(self.game_area().shape, dtype='uint8')
        self.total_tetromino_used = 0
        self.fps = 0
        self._last_time_fps = time.time()
        self.score = 0
        self.lines = 0
        self.level = 0
        self.frames_until_tetro_spawn = 0

    def set_new_tetromino(self, is_new):
        if is_new:
            self.total_tetromino_used += 1
        self._is_new_tetromino = is_new

    def is_new_tetromino(self) -> bool:
        '''Return True if a new tetromino spawn during this frame'''
        return self._is_new_tetromino


    def tick(self, count=1, render=True) -> bool:
        tick = self.pyboy.tick(count, render)

        # Get values
        self.score = self.tetris.score
        self.lines = self.tetris.lines
        self.level = self.tetris.level
        self.env.frame_increment()
        self.frames_until_tetro_spawn += 1

        # Time and FPS
        self.delta_time = time.time() - self._last_time_fps
        self.fps = round(1 / self.delta_time, 0)
        self.time_scale = self.fps / GB_NORMAL_FPS
        self.play_time += self.delta_time * self.time_scale

        self.set_new_tetromino(False)

        # Check new tetromino
        is_new_tetromino, current_tetromino = self.new_tetromino_spawned(self.game_area(), self._last_game_area)

        if is_new_tetromino:
            self.set_game_area_only()
            self.set_new_tetromino(True)
            self.set_current_tetromino(current_tetromino)
            self.frames_until_tetro_spawn = 0

            if PRINT_GAME_AREAS:
                print(f'Current Tetromino:\n{TetrisInfos.print_tetromino(self._current_tetromino)}')
                print(f'Next Tetromino:\n{TetrisInfos.print_tetromino(self.next_tetromino())}')
                print(TetrisInfos.better_game_area(self.game_area()))

            if PLAY_MODE == 'Random' or PLAY_MODE == 'Agent':
                # Fix to allow spamming down button when a new tetromino spawn
                self.pyboy.button_release('down')

        # Update values
        if not self.game_over():
            self._last_spawner_area = self.spawner_area
            self.last_current_tetromino_area = self.current_tetromino_area
            self._last_game_area = self.game_area()

        self._last_time_fps = time.time()

        return tick

    def new_tetromino_spawned(self, game_area, last_game_area):
        # Dictionnaire contenant le compte de valeurs uniques dans la zone de jeu de la frame précédente
        # ex: {0: 55, 7: 4} où la key 0 correspond à une case vide, et 7 à un tetromino 'I'
        unique_last = np.unique(last_game_area, return_counts=True)
        count_unique_last = {value:count for value, count in zip(unique_last[0], unique_last[1])}

        # Dictionnaire contenant le compte de valeurs uniques dans la zone de jeu actuelle
        unique = np.unique(game_area, return_counts=True)
        count_unique = {value:count for value, count in zip(unique[0], unique[1])}

        # Calcule de la différence entre la zone de jeu actuelle et la zone de jeu de la frame précédente
        # On est censé avoir une zone de jeu vide contenant uniquement les éléments en plus par rapport à la frame précédente
        self.current_tetromino_area = game_area - last_game_area
        # Vérification des valeurs issues de la soustraction:
        # pendant la phase de déplacements du current_tetromino, on peut avoir des valeurs négatives
        # (ou égales à 4 millions et quelques car game_area() est au format "uint32"), donc on les transforme en 0
        allowed_values = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        invalid_mask = ~np.isin(self.current_tetromino_area, allowed_values)
        self.current_tetromino_area[invalid_mask] = 0
        # Encore une fois on calcule le nombre de valeurs uniques, mais dans cette "différence" de zones de jeu
        unique_val, unique_count = np.unique(self.current_tetromino_area, return_counts=True)

        # Check si :
        #   -On a moins de case vide (de valeur "0") actuellement, par rapport à la frame précédente
        #   -La différence entre la zone de jeu actuelle et celle de la frame précédente renvoie une zone contenant uniquement des 0 (cases vide), et 4 cases d'une autre valeur (l'ID du nouveau tetromino)
        # Si c'est le cas, on renvoie le nouveau tetromino
        return (count_unique.get(0, 0) < count_unique_last.get(0, 0) and len(unique_val) == 2 and 4 in unique_count), self.get_current_tetromino(unique_val)

    def get_current_tetromino(self, unique_val):
        # Si dans la "différence" entre la zone de jeu actuelle et cette de la frame précédente, il n'y a pas que des 0 (cases vides) et uniquement 1 autre valeur (celle du nouveau tetromino),
        # c'est qu'on est dans un cas où une ligne a été détruite, et que cette ligne clignotte, donc on ne renvoie pas de nouveau tetromino
        if len(unique_val) != 2:
            return None

        list_unique_val = list(unique_val)
        # On retire la valeur 0 de la liste ("0" étant une case vide)
        list_unique_val.remove(0)
        # Il ne reste qu'un élément dans la liste, qui devrait correspondre à l'ID du nouveau tetromino
        current_tetromino = list_unique_val[0]
        # On convertit l'ID en "nom" de tetromino
        return TetrisInfos.get_tetromino_form(current_tetromino)
