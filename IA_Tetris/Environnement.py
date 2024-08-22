
from pyboy import pyboy
from pyboy.core.mb import Motherboard
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.utils import TetrisInfos

#path pour démarrer le jeu
rom_path = ROM_PATH

class TetrisEnv() :
    #envrionnement

    df = None

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
                rom_path,
                self.pyboy_argv['bootrom'],
                self.pyboy_argv["color_palette"],
                self.pyboy_argv["cgb_color_palette"],
                self.pyboy_argv['sound'],
                self.pyboy_argv['sound_emulated'],
                self.pyboy_argv['cgb'],
                randomize=False,
            )

        self.pyboy_env = PyBoy(gamerom=rom_path,
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
        self.tetris = Tetris(self.pyboy_env)
        self.tetris.game_area_mapping()
        # self.pb_tetris = self.pyboy_env.game_wrapper
        # self.pb_tetris.game_area_mapping(self.pb_tetris.mapping_compressed, 0)
        self.frame_count = 0
        self.seed = np.random.randint(0, sys.maxsize) if SEED == None else SEED # Si SEED == None, on génère une seed random qu'on peut stocker pour la sauvegarder dans le csv
        self.inputs = [] # TODO: stock tous les inputs de la partie

        # /!\ ##########################################
        # METTRE À FALSE QUAND ON COMMENCERA À AVOIR DE VRAIES DONNÉES
        # Si c'est à True, ça va écraser le csv actuel
        TetrisEnv.df = TetrisInfos.get_dataframe(True)
        # /!\ ##########################################

    def run_game(self, n_episodes = None):
        self.tetris.start_game(timer_div=self.seed)
        self.tetris.tick()

        if n_episodes == 0:
            self.ticks_loop()
        else:
            self.run_n_episodes(n_episodes)

    def run_n_episodes(self, n_episodes):
        for episode in range(n_episodes):
            self.ticks_loop()

    def ticks_loop(self):
        """Boucle principale de traitement des ticks"""
        while self.tetris.tick():
            # Incrémenter le compteur de frames
            self.frame_count += 1

            if AUTO_PLAY_RANDOM:
                # Si on veut tester avec des inputs randoms
                rand_input = INPUTS[np.random.randint(0, len(INPUTS))]
                if rand_input != 'none':
                    self.pyboy_env.button(rand_input)
                self.inputs.append(TetrisInfos.get_input_id(rand_input))

            # Vérifier l'état du jeu (Game Over)
            if self.game_over():
                TetrisEnv.df = TetrisInfos.game_over(print_infos=True,
                                                data=TetrisEnv.df,
                                                play_time=self.tetris.play_time,
                                                reward=self.get_rewards(),
                                                score=self.tetris.score,
                                                lines=self.tetris.lines,
                                                nb_tetrominos_used=self.tetris.total_tetromino_used,
                                                seed=self.seed,
                                                inputs=self.inputs)
                self.reset()

                if NB_EPISODES > 0:
                    break # Passer au prochain épisode après réinitialisation

            # Ajoutez ici la logique d'action de l'agent
            #action = self.get_agent_action()  # Fonction fictive pour obtenir l'action de l'agent
            #self.actions(action)

    def state(self):
        return self.tetris.game_area_only()

    def game_over(self):
        return self.tetris.game_over()

    def actions(self, action):
        if action == 0:
            self.pyboy_env.send_input(WindowEvent.PRESS_ARROW_LEFT)
        elif action == 1:
            self.pyboy_env.send_input(WindowEvent.PRESS_ARROW_RIGHT)
        elif action == 2:
            self.pyboy_env.send_input(WindowEvent.PRESS_ARROW_DOWN)
        elif action == 3:
            self.pyboy_env.send_input(WindowEvent.PRESS_BUTTON_A)
        #self.tetris.tick() # pourquoi tick ici ?

    def lines_rewards(self):
        rewards = self.tetris.lines*200
        return rewards

    def bumpiness_rewards(self):
        state = self.tetris.game_area_only()
        column_heigh = []
        for i in range(state.shape[1]):
            column = state[:, i]
            bloc_column = [x for x in column if x != 47]
            column_heigh.append(len(bloc_column))

        rewards = 0
        for i in range(len(column_heigh)) :
            subtraction_result = np.abs(column_heigh[i + 1] - column_heigh[i])
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
        reward = self.frame_count * -1
        return reward

    def get_rewards(self):
        # TODO: Problème sur le hole_rewards()
        #     167 def hole_rewards(self):
        # --> 168     rows, cols = self.tetris.game_area()
        #     169     hole = 0
        #     170     for i in range(0, rows):

        # ValueError: too many values to unpack (expected 2)

        # TODO: Problème avec self.heigh_rewards()
        #     154 rewards = 0
        #     155 for i in self.tetris.game_area():
        # --> 156     if i == 47:
        #     157         rewards += 1
        #     158 for i in self.tetris.game_area():

        # ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()

        # TODO: Problème avec self.bumpiness_rewards()
        #     147 rewards = 0
        #     148 for i in range(len(column_heigh)) :
        # --> 149     subtraction_result = np.abs(column_heigh[i + 1] - column_heigh[i])
        #     150     rewards += subtraction_result
        #     151 return rewards*(-1)

        # IndexError: list index out of range

        return self.frame_rewards() + self.score_rewards() + self.lines_rewards()
        #  + self.hole_rewards()
        #  + self.heigh_rewards()
        #  + self.bumpiness_rewards()

    def reset(self):
        self.tetris.reset_game(self.seed)

    def close(self):
        self.pyboy_env.stop()


if __name__ == '__main__':
    env = TetrisEnv(rom_path)
    while env.tetris.tick():
        pass
