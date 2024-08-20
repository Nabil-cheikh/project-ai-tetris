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
        tetris = self.pyboy.game_wrapper
        tetris.game_area_mapping(tetris.mapping_compressed, 0)
        tetris.start_game()
        self.pyboy.tick()

    def state():
        pass

    def actions(self):
        pass

    def rewards():
        pass

    def reset(self):
        pass


    def interact():
        pass

    def plot_result():
        pass



env = TetrisEnv(rom_path)
while env.pyboy.tick():
    pass
