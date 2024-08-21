from pyboy.plugins import game_wrapper_tetris
from pyboy import PyBoy
import numpy as np
import time

class Tetris(game_wrapper_tetris.GameWrapperTetris):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = time.time()
        self.spawner_area = np.zeros((2, 4), dtype='int8') # Ths spawner area is an area of shape (2, 4) on top of the game area
        self.current_tetromino = self.next_tetromino()
        self.game_area_only = self.game_area()
        self.fps = 0

    def set_current_tetromino(self, tetromino):
        self.current_tetromino = tetromino

    def current_tetromino(self):
        return self.current_tetromino

    def set_game_area_only(self):
        self.game_area_only = self.game_area()

    def game_area_only(self):
        return self.game_area_only

    def reset_game(self, timer_div=None):
        super().reset_game(timer_div)
        pass

    def tick(self, count=1, render=True):
        PyBoy.tick(count, render)
