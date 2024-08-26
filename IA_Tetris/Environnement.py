
from pyboy import pyboy
from pyboy import PyBoy
import sys
import numpy as np
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.utils import PrintColor
from IA_Tetris.utils import TetrisInfos
from IA_Tetris.utils import Datas

class TetrisEnv() :

    df = None

    def __init__(self):
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
                        cgb_color_palette = pyboy.defaults["cgb_color_palette"]) # déterminer le type d'affichage

        self.pyboy_env.set_emulation_speed(GAME_SPEED) # déterminer la vitesse
        self.tetris = Tetris(self.pyboy_env, self)
        self.tetris.game_area_mapping()
        self.frame_count = 0
        self.down_button_used = False
        self.last_down_button_reward = 0
        self.total_down_button_rewards = 0
        self.last_nb_tetromino_rewards = 0
        self.total_nb_tetrominos_rewards = 0
        self.last_score_rewards = 0
        self.total_score_rewards = 0
        self.last_lines_rewards = 0
        self.total_lines_rewards = 0
        self.total_holes = 0
        self.total_height = 0
        self.total_bumpiness = 0
        self.seed = np.random.randint(0, sys.maxsize) if SEED == None else SEED # Si SEED == None, on génère une seed random qu'on peut stocker pour la sauvegarder dans le csv
        self.inputs = []

        # /!\ ##########################################
        # METTRE À FALSE QUAND ON COMMENCERA À AVOIR DE VRAIES DONNÉES
        # Si c'est à True, ça va écraser le csv actuel
        TetrisEnv.df = Datas.get_dataframe()
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

    def frame_increment(self):
        self.frame_count += 1

    def ticks_loop(self):
        '''Boucle pour passer d'une frame à la suivante'''
        while self.tetris.tick():
            self.frame_increment()

            if self.tetris.is_new_tetromino():
                positif = self.get_rewards() > 0
                print(PrintColor.cstr_with_arg(f"Rewards: {'+' if positif else ''}{self.get_rewards()}", 'pure green' if positif else 'pure red', True))

            if PLAY_MODE == 'Random':
                # Si on veut tester avec des inputs randoms
                rand_input = INPUTS[np.random.randint(0, len(INPUTS))]
                if rand_input != 'none':
                    self.pyboy_env.button(rand_input)
                self.inputs.append(TetrisInfos.get_input_id(rand_input))

            if self.game_over():
                self.get_results()
                self.reset()

                if NB_EPISODES > 0:
                    break # Coupe la boucle while pour passer à l'épisode suivant

    def get_results(self):
        TetrisEnv.df = TetrisInfos.game_over(data=TetrisEnv.df,
                                                play_time=self.tetris.play_time,
                                                reward=self.get_total_rewards(),
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
        return [self.bumpiness_rewards(), self.lines_rewards(), self.heigh_rewards(), self.score_rewards(), self.hole_rewards() + self.down_button_reward() + self.nb_tetrominos_reward()]

    def get_next_states(self):
        states = {}
    #     piece_id = TetrisInfos.get_tetromino_id(self.tetris.current_tetromino())
    #     rotations = []

    #     if piece_id == 3:
    #         rotations = [0]
    #     elif piece_id == 2 or piece_id == 6 or piece_id == 7:
    #         rotations = [0, 90]
    #     else:
    #         rotations = [0, 90, 180, 270]

    #     for rotation in rotations:
    #         piece =
    #         min_x =
    #         max_x =
    #         for x in range(-min_x, self.game_area().shape[0] - max_x):
    #             states[x, rotation] = self.state()

        return states

    def game_over(self):
        return self.tetris.game_over()

    def actions(self, action):
        if TetrisInfos.get_input(action) == 'down':
            self.down_button_used = True
        self.inputs.append(action)
        self.pyboy_env.button(TetrisInfos.get_input(action))

    def bumpiness_rewards(self):
        state = self.tetris.game_area_only()
        column_heights = []

        # Calcul de la hauteur de chaque colonne
        for i in range(state.shape[1]):
            column = state[:, i]
            bloc_column = [x for x in column if x != 0]  # Filtre les cellules non vides
            column_heights.append(len(bloc_column))

        rewards = 0

        # Calcul de la différence absolue entre les hauteurs des colonnes adjacentes
        for i in range(len(column_heights) - 1):  # On s'arrête avant la dernière colonne
            subtraction_result = abs(column_heights[i + 1] - column_heights[i])
            rewards += subtraction_result

        return rewards * (-1)

    def heigh_rewards(self):
        game_area = self.game_area_only()
        rows, cols = game_area.shape
        max_height = 0

        for y in range(cols):
            height = 0
            for x in range(rows):
                if height == 0 and game_area[x, y] != 0:
                    height = rows - x
                    break
            if height > max_height:
                max_height = height

        rewards = max_height * (-40) if max_height >= 10 else max_height * (-10)
        return rewards

    def hole_rewards(self):
        game_area = self.tetris.game_area_only()
        rows, cols = game_area.shape
        hole = 0

        for y in range(cols):
            found_tetromino = False
            for x in range(rows):
                if found_tetromino and game_area[x, y] == 0:
                    hole += 1
                if not found_tetromino and game_area[x, y] != 0:
                    found_tetromino = True

        rewards = hole * (-50)
        return rewards

    def frame_rewards(self):
        reward = self.frame_count * -1
        return reward

    def update_increment_rewards(self):
        self.last_lines_rewards = self.total_lines_rewards
        total = self.tetris.lines * 200
        self.total_lines_rewards += total - self.last_lines_rewards

        self.last_score_rewards = self.total_score_rewards
        total = self.tetris.score * 1
        self.total_score_rewards += total - self.last_score_rewards

        self.last_down_button_reward = self.total_down_button_rewards
        if self.down_button_used:
            self.total_down_button_rewards += 50
        self.down_button_used = False

        nb_tetro = 0
        self.last_nb_tetromino_rewards = self.total_nb_tetrominos_rewards
        last_nb_tetro_used = self.last_nb_tetromino_rewards / 10
        if self.tetris.total_tetromino_used > last_nb_tetro_used:
            nb_tetro = self.tetris.total_tetromino_used - last_nb_tetro_used
            self.total_nb_tetrominos_rewards += nb_tetro * 10

        self.total_holes += self.hole_rewards()
        self.total_height += self.heigh_rewards()
        self.total_bumpiness += self.bumpiness_rewards()

    def lines_rewards(self):
        return self.total_lines_rewards - self.last_lines_rewards

    def score_rewards(self):
        return self.total_score_rewards - self.last_score_rewards

    def down_button_reward(self):
        return self.total_down_button_rewards - self.last_down_button_reward

    def nb_tetrominos_reward(self):
        return self.total_nb_tetrominos_rewards - self.last_nb_tetromino_rewards

    def get_rewards(self):
        # Rewards obtenues à la frame actuelle
        return self.score_rewards() + self.lines_rewards() + self.hole_rewards() + self.heigh_rewards() + self.bumpiness_rewards() + self.down_button_reward() + self.nb_tetrominos_reward()
                # + self.frame_rewards()

    def get_total_rewards(self):
        # Total de rewards obtenues depuis le début de la partie
        return self.total_score_rewards + self.total_lines_rewards + self.total_holes + self.total_height + self.total_bumpiness + self.total_down_button_rewards + self.total_nb_tetrominos_rewards

    def reset(self):
        self.down_button_used = False
        self.last_down_button_reward = 0
        self.total_down_button_rewards = 0
        self.last_nb_tetromino_rewards = 0
        self.total_nb_tetrominos_rewards = 0
        self.last_score_rewards = 0
        self.total_score_rewards = 0
        self.last_lines_rewards = 0
        self.total_lines_rewards = 0
        self.total_holes = 0
        self.total_height = 0
        self.total_bumpiness = 0

        self.tetris.reset_game(self.seed)

    def close(self):
        self.pyboy_env.stop()


if __name__ == '__main__':
    env = TetrisEnv()
    while env.tetris.tick():
        pass
