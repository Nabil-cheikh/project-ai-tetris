
from pyboy import pyboy
from pyboy.core.mb import Motherboard
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.utils import TetrisInfos

#path pour démarrer le jeu
rom_path = ROM_PATH

class TetrisEnv() :

    def __init__(self, rom_path):
        self.pyboy_argv = {
            'window':pyboy.defaults["window"],
            'scale':pyboy.defaults["scale"],
            'symbols':None,
            'bootrom':None,
            'sound':False,
            'sound_emulated':False,
            'cgb':None,
            'log_level':pyboy.defaults["log_level"],
            'color_palette':pyboy.defaults["color_palette"],
            'cgb_color_palette':pyboy.defaults["cgb_color_palette"]
        }

        self.mb = Motherboard(
                ROM_PATH,
                self.pyboy_argv['bootrom'],
                self.pyboy_argv["color_palette"],
                self.pyboy_argv["cgb_color_palette"],
                self.pyboy_argv['sound'],
                self.pyboy_argv['sound_emulated'],
                self.pyboy_argv['cgb'],
                randomize=False,
            )

        self.pyboy_env = PyBoy(gamerom=ROM_PATH,
                        window=self.pyboy_argv['window'],
                        scale=self.pyboy_argv['scale'],
                        symbols=self.pyboy_argv['symbols'],
                        bootrom=self.pyboy_argv['bootrom'],
                        sound=self.pyboy_argv['sound'],
                        sound_emulated=self.pyboy_argv['sound_emulated'],
                        cgb=self.pyboy_argv['cgb'],
                        log_level=self.pyboy_argv['log_level'],
                        color_palette=self.pyboy_argv['color_palette'],
                        cgb_color_palette=self.pyboy_argv['cgb_color_palette']) # déterminer le type d'affichage

        self.pyboy_env.set_emulation_speed(0) # déterminer la vitesse

        self.tetris = Tetris(self.pyboy_env, self.mb, self.pyboy_argv)
        self.tetris.game_area_mapping(self.tetris.mapping_compressed, 0)


    def run_game(self, n_episodes = None):
        self.tetris.start_game(timer_div=None)
        self.pyboy_env.tick()
        self.frame_count = 0

        if n_episodes == None:
            self.ticks_loop()
        else:
            self.run_n_episodes(n_episodes)

    def run_n_episodes(self, n_episodes):
        for episode in range(n_episodes):
            self.ticks_loop()

    def ticks_loop(self):
        while self.pyboy_env.tick():
            self.one_tick()

    def one_tick(self):
        # check Game Over
        if self.game_over():
            TetrisInfos.update_datas()
        # check spawn new tetromino
        # increment timer
        # check play or replay

        pass

    def state(self):
        return self.tetris.game_area_clean()

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
        self.frame_count += 1

    def lines_rewards(self):
        rewards = self.tetris.lines*200
        return rewards

    def bumpiness_rewards(self):
        state = self.tetris.game_area_clean()
        column_heigh = []
        for i in range(state.shape[1]):
            column = state[:, i]
            bloc_column = [x for x in column if x != 47]
            column_heigh.append(len(bloc_column))

        rewards = 0
        for i in range(column_heigh) :
            subtraction_result = column_heigh[i + 1] - column_heigh[i]
            rewards += subtraction_result
        return rewards*(-1)

    def heigh_rewards(self):
        rewards = 0
        for i in self.tetris.game_area():
            if i == 47:
                rewards += 1
        for i in self.tetris.game_area():
            if i != 47:
                rewards += -10
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
                    hole_middle = [self.tetris.game_area()[i, j+1]]

                    if all(h != 47 for h in hole_middle):
                        hole += 1

        rewards = hole*(-1000)
        return rewards

    def frame_rewards(self):
        self.frame_count = 0
        reward = self.frame_count * -1
        return reward

    def get_rewards(self):
        rewards = self.frame_rewards + self.hole_rewards
        + self.score_rewards + self.heigh_rewards + self.bumpiness_rewards
        + self.lines_rewards
        return rewards

    def reset(self):
        self.tetris.reset_game()

    def close(self):
        self.pyboy_env.stop()


if __name__ == '__main__':
    env = TetrisEnv(rom_path)
    while env.tetris.tick():
        pass
