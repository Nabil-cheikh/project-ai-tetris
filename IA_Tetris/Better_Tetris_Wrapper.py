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
        self.spawner_area = self.game_area()[1:3,3:7] # The spawner area is the area of shape (2, 4) on top of the game area where new tetropino spawn
        self._last_spawner_area = np.zeros((2, 4), dtype='int8')
        self._current_tetromino = self.next_tetromino()
        self._last_next_tetromino = self.next_tetromino()
        self._game_area_only = self.game_area()
        self._last_game_area = np.zeros(self.game_area().shape, dtype='int8')
        self.total_tetromino_used = 0
        self.fps = 0
        self._last_time_fps = time.time()
        self.score = 0
        self.lines = 0
        self.level = 0

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
        self.spawner_area = self.game_area()[1:3,3:7] # The spawner area is the area of shape (2, 4) on top of the game area where new tetropino spawn
        self._last_spawner_area = np.zeros((2, 4), dtype='int8')
        self._current_tetromino = self.next_tetromino()
        self._game_area_only = self.game_area()
        self._last_game_area = np.zeros(self.game_area().shape, dtype='int8')
        self.total_tetromino_used = 0
        self.fps = 0
        self._last_time_fps = time.time()
        self.score = 0
        self.lines = 0
        self.level = 0

    def set_new_tetromino(self, is_new):
        if is_new:
            self.total_tetromino_used += 1
        self._new_tetromino = is_new

    def new_tetromino(self) -> bool:
        '''Return True if a new tetromino spawn during this frame'''
        return self._new_tetromino

    def tick(self, count=1, render=True) -> bool:
        tick = self.pyboy.tick(count, render)

        # Get values
        self.score = self.tetris.score
        self.lines = self.tetris.lines
        self.level = self.tetris.level
        self.env.frame_increment()

        # Time and FPS
        self.delta_time = time.time() - self._last_time_fps
        self.fps = round(1 / self.delta_time, 0)
        self.time_scale = self.fps / GB_NORMAL_FPS
        self.play_time += self.delta_time * self.time_scale

        self.spawner_area = self.game_area()[1:3,3:7]
        self.set_new_tetromino(False)

        # Check new tetromino
        unique_last = np.unique(self._last_game_area, return_counts=True)
        count_unique_last = {value:count for value, count in zip(unique_last[0], unique_last[1])}

        unique = np.unique(self.game_area(), return_counts=True)
        count_unique = {value:count for value, count in zip(unique[0], unique[1])}
        if count_unique[0] < count_unique_last[0]:
            self.set_game_area_only()
            self.set_new_tetromino(True)
            self.set_current_tetromino(self._last_next_tetromino)

            if PRINT_GAME_AREAS:
                print(f'Current Tetromino:\n{TetrisInfos.print_tetromino(self.current_tetromino())}')
                print(f'Next Tetromino:\n{TetrisInfos.print_tetromino(self.next_tetromino())}')
                # print(TetrisInfos.better_game_area(self.game_area_only()))

            if PLAY_MODE == 'Random' or PLAY_MODE == 'Agent':
                # Fix to allow spamming down button when a new tetromino spawn
                self.pyboy.button_release('down')
                    # break

        # Update values
        self._last_spawner_area = self.spawner_area
        self._last_game_area = self.game_area()
        self._last_next_tetromino = self.next_tetromino()
        self._last_time_fps = time.time()

        return tick
