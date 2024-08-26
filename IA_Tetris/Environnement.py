
import sys
import numpy as np
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.utils import TetrisInfos
from IA_Tetris.utils import Datas
from pyboy import PyBoy
from pyboy import pyboy

class TetrisEnv:
    df = None

    def __init__(self):
        # Remplacement de toutes les références à pyboy.defaults par des valeurs fixes appropriées
        self.pyboy_env = PyBoy(gamerom = ROM_PATH,
                        window = 'SDL2' if SHOW_GAME_WINDOW else 'null',
                        scale = pyboy.defaults["scale"],
                        symbols = None,
                        bootrom = None,
                        sound = False,
                        sound_emulated = False,
                        cgb = None,
                        log_level = pyboy.defaults["log_level"],
                        color_palette = pyboy.defaults["color_palette"],
                        cgb_color_palette = pyboy.defaults["cgb_color_palette"])

        self.pyboy_env.set_emulation_speed(GAME_SPEED)
        self.tetris = Tetris(self.pyboy_env, self)
        self.tetris.game_area_mapping()
        self.frame_count = 0
        self.seed = np.random.randint(0, sys.maxsize) if SEED is None else SEED
        self.inputs = []

        TetrisEnv.df = Datas.get_dataframe()



    def run_game(self, n_episodes=None):
        self.tetris.start_game(timer_div=self.seed)
        self.tetris.tick()

        if n_episodes == 0:
            self.ticks_loop()
        else:
            self.run_n_episodes(n_episodes)

    def run_n_episodes(self, n_episodes):
        for episode in range(n_episodes):
            self.ticks_loop()

    def frame_increment(self):
        self.frame_count += 1

    def ticks_loop(self):
        while self.tetris.tick():
            self.frame_increment()

            if PLAY_MODE == 'Random':
                rand_input = INPUTS[np.random.randint(0, len(INPUTS))]
                if rand_input != 'none':
                    self.pyboy_env.button(rand_input)
                self.inputs.append(TetrisInfos.get_input_id(rand_input))

            if self.game_over():
                self.get_results()
                self.reset()

                if NB_EPISODES > 0:
                    break  # Passe à l'épisode suivant

    def get_results(self):
        TetrisEnv.df = TetrisInfos.game_over(data=TetrisEnv.df,
                                             play_time=self.tetris.play_time,
                                             reward=self.get_rewards(),
                                             score=self.tetris.score,
                                             lines=self.tetris.lines,
                                             nb_tetrominos_used=self.tetris.total_tetromino_used,
                                             seed=self.seed,
                                             inputs=self.inputs)

    def game_area_only(self):
        return self.tetris.game_area_only()

    def game_area(self):
        return self.tetris.game_area()

    def state(self):
        return (self.bumpiness_penalty(),
                self.lines_rewards(),
                self.height_penalty(),
                self.score_rewards(),
                self.hole_rewards(),
                self.game_over_rewards(),
                self.compactness_reward(),
                self.edge_alignment_reward(),
                self.survival_reward(),
                self.cavity_penalty(),
                self.game_area(),
                self.get_rewards())

    def game_over(self):
        return self.tetris.game_over()

    def get_current_tetromino_id(self):
        """Renvoie l'identifiant du tétrimino actuel."""
        return self.tetris.current_tetromino()

    def actions(self, action):
            self.inputs.append(action)
            self.pyboy_env.button(TetrisInfos.get_input(action))

    def lines_rewards(self):
        return (self.tetris.lines*30)**2

    def game_over_rewards(self):
        if self.tetris.game_over():
            return -1000
        return 0  # Retourne 0 si le jeu n'est pas terminé

    def bumpiness_penalty(self):
        state = self.tetris.game_area_only()
        heights = [np.max(np.where(state[:, i] != 0)[0]) if np.any(state[:, i]) else 0 for i in range(state.shape[1])]
        bumpiness = sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))
        return bumpiness * (-1)  # pénalité par différence de hauteur entre colonnes

    def compactness_reward(self):
        state = self.tetris.game_area()
        filled_cells = np.count_nonzero(state)
        total_cells = np.prod(state.shape)
        compactness_ratio = filled_cells / total_cells
        return compactness_ratio * 100



    def height_penalty(self):
        state = self.tetris.game_area()
        max_height = np.max(np.argmax(state != 0, axis=0))
        return max_height * (-10)  # pénalité de 10 points par ligne de hauteur


    def edge_alignment_reward(self):
        state = self.tetris.game_area()
        left_edge_filled = np.sum(state[:, 0] != 0)
        right_edge_filled = np.sum(state[:, -1] != 0)
        return (left_edge_filled + right_edge_filled) * 10  # récompense pour les bords remplis

    def survival_reward(self):
        return self.frame_count // 100  # 1 point pour chaque 100 frames survécues

    def cavity_penalty(self):
        state = self.tetris.game_area()
        penalty = 0
        for i in range(1, state.shape[0]):
            for j in range(state.shape[1]):
                if state[i, j] == 0 and np.any(state[:i, j] != 0):  # s'il y a un espace vide sous un bloc
                    penalty += 1
        return penalty * (-50)  # pénalité par cavité




    def score_rewards(self):
        return self.tetris.score * 20

    def hole_rewards(self):
        state = self.tetris.game_area()
        rows, cols = state.shape
        hole = 0

        for i in range(1, rows):
            for j in range(cols):
                if state[i, j] == 0 and state[i - 1, j] != 0:
                    hole += 1

        return hole * (-100)



    def get_rewards(self):
        return (self.bumpiness_penalty() +
                self.lines_rewards() +
                self.height_penalty() +
                self.score_rewards() +
                self.hole_rewards() +
                self.game_over_rewards() +
                self.compactness_reward() +
                self.edge_alignment_reward() +
                self.survival_reward() +
                self.cavity_penalty())

    def reset(self):
        self.tetris.reset_game(self.seed)
        self.pyboy_env.set_emulation_speed(GAME_SPEED)

    def close(self):
        self.pyboy_env.stop()


if __name__ == '__main__':
    env = TetrisEnv()
    while env.tetris.tick():
        pass
