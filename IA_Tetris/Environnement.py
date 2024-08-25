
from pyboy import pyboy
from pyboy import PyBoy
import sys
import numpy as np
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
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
        return [self.bumpiness_rewards(), self.lines_rewards(), self.heigh_rewards(), self.score_rewards(), self.hole_rewards()]

    def _check_collision(self, piece, next_pos):
        '''Check if there is a collision between the current piece and the board'''
        for x, y in piece:
            x += next_pos[0]
            y += next_pos[1]
            if x < -3 or x >= 6 \
                    or y < 0 or y >= BOARD_HEIGHT \
                    or self.game_area_only()[x][y] != 0:
                return True
        return False


    def _add_piece_to_board(self, piece, piece_id, pos):
        '''Place a piece in the board, returning the resulting board'''
        board = [x[:] for x in self.game_area_only()]
        for x, y in piece:
            board[y + pos[1]][x + pos[0]] = piece_id
        return board

    def get_next_states(self):
        states = {}
        piece_id = TetrisInfos.get_tetromino_id(self.tetris.current_tetromino())
        rotations = []

        if piece_id == 3:
            rotations = [0]
        elif piece_id == 2 or piece_id == 6 or piece_id == 7:
            rotations = [0, 90]
        else:
            rotations = [0, 90, 180, 270]
        if piece_id == 3:
            rotations = [0]
        elif piece_id == 2 or piece_id == 6 or piece_id == 7:
            rotations = [0, 90]
        else:
            rotations = [0, 90, 180, 270]

        for rotation in rotations:
            piece = TetrisInfos.TETROMINOS[piece_id][rotation]
            min_x = min(p[0] for p in piece)
            max_x = max(p[0] for p in piece)
            width_tetro = max_x - min_x

            # obtain initial position :
            initial_pos = [min_x, 0]
            # for all positions in the width
            for x in range(0, BOARD_WIDTH- width_tetro):
                next_pos = [x, 0]

                # Drop piece
                while not self._check_collision(piece, next_pos):
                    next_pos[1] +=1
                next_pos[1] -= 1

                # Valid move
                if next_pos[1] >= 0:
                    new_board = self._add_piece_to_board(piece, piece_id, next_pos)
                    states[(next_pos, rotation)] = self.state(new_board)

        return states

    def game_over(self):
        return self.tetris.game_over()

    def actions(self, action):
        self.inputs.append(action)
        self.pyboy_env.button(TetrisInfos.get_input(action))

    def lines_rewards(self):
        rewards = self.tetris.lines*200
        return rewards

    def bumpiness_rewards(self, board = None):
        if board == None:
            board = self.tetris.game_area_only()
        state_board = board
        column_heights = []

        # Calcul de la hauteur de chaque colonne
        for i in range(state_board.shape[1]):
            column = state_board[:, i]
            bloc_column = [x for x in column if x != 0]  # Filtre les cellules non vides
            column_heights.append(len(bloc_column))

        rewards = 0

        # Calcul de la différence absolue entre les hauteurs des colonnes adjacentes
        for i in range(len(column_heights) - 1):  # On s'arrête avant la dernière colonne
            subtraction_result = abs(column_heights[i + 1] - column_heights[i])
            rewards += subtraction_result

        return rewards * (-1)

    def heigh_rewards(self):
        rewards = 0

        # Parcours de chaque cellule dans la zone de jeu
        for row in self.tetris.game_area():
            for cell in row:
                if cell == 0:  # Si la cellule est un trou
                    rewards += 1
                else:  # Si la cellule n'est pas un trou
                    rewards -= 10
        return rewards

    def score_rewards(self):
        rewards = self.tetris.score*1
        return rewards

    def hole_rewards(self):
        rows, cols = self.tetris.game_area().shape
        hole = 0

        for i in range(rows):
            for j in range(cols):
                if self.tetris.game_area()[i, j] == 0:
                    if i < rows - 1 and self.tetris.game_area()[i + 1, j] != 0:
                        hole += 1

        rewards = hole * (-1000)
        return rewards

    # def frame_rewards(self):
    #     reward = self.frame_count * -1
    #     return reward
    # def frame_rewards(self):
    #     reward = self.frame_count * -1
    #     return reward

    def get_rewards(self):
        return self.score_rewards() + self.lines_rewards() + self.hole_rewards() + self.heigh_rewards() + self.bumpiness_rewards()
        return self.score_rewards() + self.lines_rewards() + self.hole_rewards() + self.heigh_rewards() + self.bumpiness_rewards()

    def reset(self):
        self.tetris.reset_game(self.seed)

    def close(self):
        self.pyboy_env.stop()


if __name__ == '__main__':
    env = TetrisEnv()
    while env.tetris.tick():
        pass
