from pyboy import PyBoy
from pyboy.utils import WindowEvent
import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import pandas as np
import matplotlib.pyplot as plt
from pyboy.plugins.game_wrapper_tetris import GameWrapperTetris
from IA_Tetris.params import *

#path pour démarrer le jeu
rom_path = ROM_PATH

class TetrisEnv() :

    def __init__(self, rom_path):
        self.pyboy = PyBoy(rom_path)
        self.tetris = GameWrapperTetris()
        self.tetris.game_area_mapping(self.tetris.mapping_compressed, 0)
        self.tetris.start_game()
        self.pyboy.tick()
        self.frame_count = 0

    def state(self):
        game_area = self.tetris.game_area()
        return game_area

    def game_over(self):
        self.tetris.game_over()

    def actions(self, action):
        if action == 0:
            self.pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
        elif action == 1:
            self.pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
        elif action == 2:
            self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
        elif action == 3:
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
        elif action == 4:
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_B)
        self.pyboy.tick()
        self.frame_count = 0

    def lines_rewards(self):
        rewards = self.tetris.lines*200
        return rewards

    def heigh_rewards(self):
        rewards += 0
        for i in self.tetris.game_area():
            if i == 47:
                rewards = 1
        for i in self.tetris.game_area():
            if i != 47:
                rewards = -10
        return rewards

    def score_rewards(self):
        rewards = self.tetris.score*1
        return rewards

    def hole_rewards(self):
        rows, cols = self.tetris.game_area()
        hole = 0
        for i in range(0, rows):
            for j in range(0, cols):
                if self.tetris.game_area()[i, j] == 47:
                    hole_middle = [self.tetris.game_area()[i-1, j-1],
                                self.tetris.game_area()[i-1, j],
                                self.tetris.game_area()[i-1, j+1],
                                self.tetris.game_area()[i, j-1],
                                self.tetris.game_area()[i, j+1],
                                self.tetris.game_area()[i+1, j-1],
                                self.tetris.game_area()[i+1, j],
                                self.tetris.game_area()[i+1, j+1]]

                    if all(h != 47 for h in hole_middle):
                        hole += 1

        rewards = hole*1000
        return rewards
    # dans le init  self.frame_count = 0
#dans le action self.frame_count += 47
    def frame_rewards(self):
        self.frame_count = 0
        reward = self.frame_count * -1
        return reward

    def reset(self):
        self.tetris.reset_game()


    def close(self):
        self.pyboy.stop()


# dans le main

env = TetrisEnv(rom_path)
while env.pyboy.tick():
    pass
