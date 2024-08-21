from pyboy.plugins import game_wrapper_tetris
from pyboy import PyBoy
import time

class Tetris(game_wrapper_tetris.GameWrapperTetris):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = time.time()
        self.current_tetromino = self.next_tetromino()

    def current_tetromino(self):
        pass

    def game_area_clean(self):
        pass

    def reset_game(self, timer_div=None):
        super().reset_game(timer_div)
        pass

    def tick(self, count=1, render=True):
        PyBoy.tick(count, render)
