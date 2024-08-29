
from pyboy import pyboy
from pyboy import PyBoy
import sys
import numpy as np
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.utils import TetrisInfos
from IA_Tetris.utils import Datas

class TetrisEnv() :
    #envrionnement

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
        self.stack_actions = []
        self.total_rewards = 0

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

    def state(self, board=None):
        if board == None:
            board = self.game_area_only()
        lines, board = self._clear_lines(board)
        total_bumpiness = self._bumpiness(board)
        holes = self._number_of_holes(board)
        sum_height = self._height(board)

        return [lines, total_bumpiness, holes, sum_height]

    def _check_collision(self, piece, next_pos):
        '''Check if there is a collision between the current piece and the board'''
        for x, y in piece:
            x += next_pos[0]
            y += next_pos[1]
            if x < 0 or x >= BOARD_WIDTH \
                    or y < 0 or y >= BOARD_HEIGHT:
                return True
            if self.game_area_only()[y][x] != 0:
                return True

        return False


    def _add_piece_to_board(self, piece, piece_id, pos):
        '''Place a piece in the board, returning the resulting board'''
        board = [list(x[:]) for x in self.game_area_only()]
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

        for rotation in rotations:
            piece = TetrisInfos.TETROMINOS[piece_id][rotation]
            min_x = min(p[0] for p in piece)
            max_x = max(p[0] for p in piece)

            # print("positions possibles")
            # print(BOARD_WIDTH - (max_x-min_x))
            # for all positions in the width
            for x in range(-min_x, BOARD_WIDTH - max_x):
                next_pos = [x, 0]
                # Drop piece
                while not self._check_collision(piece, next_pos):
                    next_pos[1] +=1
                next_pos[1] -= 1

                # Valid move
                if next_pos[1] >= 0:
                    new_board = self._add_piece_to_board(piece, piece_id, next_pos)
                    states[(tuple(next_pos), rotation)] = self.state(new_board)

            # print("positions possibles après le check collisions")
            # print(len(states))

        return states

    def game_over(self):
        return self.tetris.game_over()

    def actions(self, action, current_piece, rotation_done):
        self.inputs.append(action)
        # print('action: ', action)
        # récupérer les infos importantes :

        rotation = action[1]
        current_x, current_y = current_piece
        final_x, final_y = action[0]
        done = len(self.stack_actions) == 0

        if len(self.stack_actions) == 0:
            if rotation != 0:
                for _ in range(int(rotation / 90)):
                    self.stack_actions.append('a')
            if current_x != final_x:
                diff_x = final_x
                if diff_x > 0:
                    for _ in range(diff_x):
                        self.stack_actions.append('right')
                else:
                    for _ in range(abs(diff_x)):
                        self.stack_actions.append('left')
            if current_y != final_y:
                diff_y = final_y - current_y
                for _ in range(diff_y):
                    self.stack_actions.append('down')

        if len(self.stack_actions) == 0:
            self.execute_actions(True)

        return (current_x, current_y), done

    def execute_actions(self, force_down=False):
        if len(self.stack_actions) > 0:
            # print('stack inputs: ', self.stack_actions)
            if self.stack_actions[0] == 'down':
                self.pyboy_env.button_press(self.stack_actions[0])
                self.stack_actions = []
            else:
                self.pyboy_env.button(self.stack_actions[0])
                self.stack_actions.pop(0)
                if len(self.stack_actions) == 0: # il y a des cas où il n'y a pas de "down" dans la liste d'actions "prédite"
                    self.stack_actions.append('down')
        if force_down:
            self.stack_actions.append('down')

    def all_actions_done(self):
        return len(self.stack_actions) == 0

    def lines_rewards(self):
        rewards = self.tetris.lines*200
        return rewards

    def _clear_lines(self, board):
        lines_to_clear = [index for index, row in enumerate(board) if 0 not in row and 8 not in row]
        if lines_to_clear:
            board = [row for index, row in enumerate(board) if index not in lines_to_clear]
            # Add new lines at the top
            for _ in lines_to_clear:
                board.insert(0, [0 for _ in range(BOARD_WIDTH)])
        return len(lines_to_clear), board


    def _bumpiness(self, board):
        '''Sum of the differences of heights between pair of columns'''
        total_bumpiness = 0
        min_ys = []

        for col in zip(*board):
            i = 0
            while i < BOARD_HEIGHT and col[i] == 0:
                i += 1
            min_ys.append(i)

        for i in range(len(min_ys) - 1):
            total_bumpiness += abs(min_ys[i] - min_ys[i+1])

        return total_bumpiness


    def _number_of_holes(self, board):
        '''Number of holes in the board (empty square with at least one block above it)'''
        holes = 0

        for col in zip(*board):
            i = 0
            while i < BOARD_HEIGHT and col[i] == 0:
                i += 1
            holes += len([x for x in col[i+1:] if x == 0])

        return holes


    def _height(self, board):
        '''Sum and maximum height of the board'''
        sum_height = 0
        max_height = 0

        for col in zip(*board):
            i = 0
            while i < BOARD_HEIGHT and col[i] == 0:
                i += 1
            height = BOARD_HEIGHT - i
            sum_height += height
            if height > max_height:
                max_height = height

        return max_height


    def bumpiness_rewards(self):
        state_board = self.tetris.game_area_only()
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

        return rewards * (-2)

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
        game_area = self.tetris.game_area()
        rows, cols = game_area.shape
        hole = 0

        for y in range(cols):
            found_tetromino = False
            for x in range(rows):
                if found_tetromino and game_area[x, y] == 0:
                    hole += 1
                if not found_tetromino and game_area[x, y] != 0:
                    found_tetromino = True

        rewards = hole * (-2)
        return rewards

    # def frame_rewards(self):
    #     reward = self.frame_count * -1
    #     return reward
    # def frame_rewards(self):
    #     reward = self.frame_count * -1
    #     return reward

    def get_rewards(self):
        return self.total_rewards

    def reset(self):
        self.stack_actions = []
        self.total_rewards = 0
        self.tetris.reset_game(self.seed)

    def close(self):
        self.pyboy_env.stop()


if __name__ == '__main__':
    env = TetrisEnv()
    while env.tetris.tick():
        pass
