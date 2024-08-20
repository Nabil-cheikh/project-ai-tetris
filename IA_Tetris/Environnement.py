from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import pandas as np
import matplotlib.pyplot as plt

#path pour démarrer le jeu
rom_path = '/Users/julienbellande/Desktop/tetris.gb'

class TetrisEnv() :

    def __init__(self, rom_path):
        self.pyboy = PyBoy(rom_path)
        self.pyboy.set_emulation_speed(0)
        self.tetris = self.pyboy.game_wrapper
        self.tetris.game_area_mapping(self.tetris.mapping_compressed, 0)
        self.tetris.start_game()
        self.pyboy.tick()

    def state(self):
        game_area = self.tetris.game_area()
        return game_area

    def rewards():
        rewards = X * scoring
        penalities = X * no_scoring_timer

        pass

    def reset(self):
        self.tetris.start_game()
        self.pyboy.tick()

    def interact():
        pass

    def close(self):
        self.pyboy.stop()



env = TetrisEnv(rom_path)
while env.pyboy.tick():
    pass
