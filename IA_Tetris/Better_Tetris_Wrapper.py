from IA_Tetris.params import *
from IA_Tetris.utils import TetrisInfos
from IA_Tetris.utils import PrintColor
import numpy as np
import time

class Tetris():# Au final on va pas faire d'héritage, c'est trop compliqué

    def __init__(self, pyboy, env):
        self.pyboy = pyboy
        self.tetris = self.pyboy.game_wrapper
        self.env = env
        self.play_time = 0
        self.delta_time = 0
        self.time_scale = 1
        self._is_new_tetromino = True
        self.spawner_area = self.game_area()[1:3,3:7] # The spawner area is the area of shape (2, 4) on top of the game area where new tetropino spawn
        self._last_spawner_area = np.zeros((2, 4), dtype='uint8')
        self._current_tetromino = self.next_tetromino()
        self._game_area_only = np.zeros(self.game_area().shape, dtype='uint8')
        self._last_game_area = np.zeros(self.game_area().shape, dtype='uint8')
        self.total_tetromino_used = 0
        self.fps = 0
        self._last_time_fps = time.time()
        self.score = 0
        self.lines = 0
        self.level = 0
        self.cumul_rewards = {'Score':0, 'Lines':0, 'Holes':0, 'Height':0, 'Bumpiness':0, '↓':0, 'Nb Tetro':0} # Used just for debugs

    def game_area_mapping(self):
        self.tetris.game_area_mapping(self.tetris.mapping_compressed, 0)

    def start_game(self, timer_div=None):
        self.tetris.start_game(timer_div)

    def set_current_tetromino(self, tetromino):
        self._current_tetromino = tetromino

    def current_tetromino(self) -> str:
        '''Form of the current tetromino: O, Z, S, L, J, T, I'''
        return self._current_tetromino

    def next_tetromino(self):
        return self.tetris.next_tetromino()

    def game_area(self):
        return self.tetris.game_area()

    def set_game_area_only(self):
        self._game_area_only = self._last_game_area

    def game_area_only(self):
        '''Game grid without the current tetromino'''
        return self._game_area_only

    def game_over(self):
        # Un poil plus rapide que le tetris.game_over() de base, qui attend que tout l'écran soit recouvert de "8"
        return 8 in self.game_area()
        # return self.tetris.game_over()

    def reset_game(self, timer_div=None):
        self.tetris.reset_game(timer_div)
        self.play_time = 0
        self.delta_time = 0
        self.time_scale = 1
        self._is_new_tetromino = True
        self.spawner_area = self.game_area()[1:3,3:7] # The spawner area is the area of shape (2, 4) on top of the game area where new tetropino spawn
        self._last_spawner_area = np.zeros((2, 4), dtype='uint8')
        self._current_tetromino = self.next_tetromino()
        self._game_area_only = np.zeros(self.game_area().shape, dtype='uint8')
        self._last_game_area = np.zeros(self.game_area().shape, dtype='uint8')
        self.total_tetromino_used = 0
        self.fps = 0
        self._last_time_fps = time.time()
        self.score = 0
        self.lines = 0
        self.level = 0
        self.cumul_rewards = {'Score':0, 'Lines':0, 'Holes':0, 'Height':0, 'Bumpiness':0, '↓':0, 'Nb Tetro':0}

    def set_new_tetromino(self, is_new):
        if is_new:
            self.total_tetromino_used += 1
        self._is_new_tetromino = is_new

    def is_new_tetromino(self) -> bool:
        '''Return True if a new tetromino spawn during this frame'''
        return self._is_new_tetromino

    def tick(self, count=1, render=True) -> bool:
        tick = self.pyboy.tick(count, render)

        # Get values
        self.score = self.tetris.score
        self.lines = self.tetris.lines
        self.level = self.tetris.level
        self.env.frame_increment()

        # self.env.update_increment_rewards()

        # Time and FPS
        self.delta_time = time.time() - self._last_time_fps
        self.fps = round(1 / self.delta_time, 0)
        self.time_scale = self.fps / GB_NORMAL_FPS
        self.play_time += self.delta_time * self.time_scale

        self.spawner_area = self.game_area()[1:3,3:7]
        self.set_new_tetromino(False)

        # Update rewards logs
        # self.cumul_rewards['Score'] += self.env.score_rewards()
        # self.cumul_rewards['Lines'] += self.env.lines_rewards()
        # self.cumul_rewards['Holes'] += self.env.hole_rewards()
        # self.cumul_rewards['Height'] += self.env.heigh_rewards()
        # self.cumul_rewards['Bumpiness'] += self.env.bumpiness_rewards()
        # self.cumul_rewards['↓'] += self.env.down_button_reward()
        # self.cumul_rewards['Nb Tetro'] += self.env.nb_tetrominos_reward()

        # Check new tetromino
        is_new_tetromino, current_tetromino = self.new_tetromino_spawned(self.game_area(), self._last_game_area)
        if is_new_tetromino:
            self.set_game_area_only()
            self.set_new_tetromino(True)
            self.set_current_tetromino(current_tetromino)

            # if PRINT_ON_NEW_TETROMINO_INFOS:
            #     cumul_rewards = self.cumul_rewards['Score'] + self.cumul_rewards['Lines'] + self.cumul_rewards['Holes'] + self.cumul_rewards['Height'] + self.cumul_rewards['Bumpiness'] + self.cumul_rewards['↓'] + self.cumul_rewards['Nb Tetro']
            #     print(PrintColor.cstr_with_arg(f"Rewards: {'+' if cumul_rewards > 0 else ''}{int(cumul_rewards)}", 'pure green' if cumul_rewards > 0 else 'pure red', True), " (", \
            #         PrintColor.cstr_with_arg(f"Score: {'+' if self.cumul_rewards['Score'] > 0 else ''}{self.cumul_rewards['Score']}", 'pure green' if self.cumul_rewards['Score'] > 0 else 'pure red', False), ", ", \
            #         PrintColor.cstr_with_arg(f"Lines: {'+' if self.cumul_rewards['Lines'] > 0 else ''}{self.cumul_rewards['Lines']}", 'pure green' if self.cumul_rewards['Lines'] > 0 else 'pure red', False), ", ", \
            #         PrintColor.cstr_with_arg(f"Holes: {'+' if self.cumul_rewards['Holes'] > 0 else ''}{self.cumul_rewards['Holes']}", 'pure green' if self.cumul_rewards['Holes'] > 0 else 'pure red', False), ", ", \
            #         PrintColor.cstr_with_arg(f"Height: {'+' if self.cumul_rewards['Height'] > 0 else ''}{self.cumul_rewards['Height']}", 'pure green' if self.cumul_rewards['Height'] > 0 else 'pure red', False), ", ", \
            #         PrintColor.cstr_with_arg(f"Bump: {'+' if self.cumul_rewards['Bumpiness'] > 0 else ''}{self.cumul_rewards['Bumpiness']}", 'pure green' if self.cumul_rewards['Bumpiness'] > 0 else 'pure red', False), ", ", \
            #         PrintColor.cstr_with_arg(f"↓: {'+' if self.cumul_rewards['↓'] > 0 else ''}{self.cumul_rewards['↓']}", 'pure green' if self.cumul_rewards['↓'] > 0 else 'pure red', False), ", ", \
            #         PrintColor.cstr_with_arg(f"Nb Tetro: {'+' if self.cumul_rewards['Nb Tetro'] > 0 else ''}{int(self.cumul_rewards['Nb Tetro'])}", 'pure green' if self.cumul_rewards['Nb Tetro'] > 0 else 'pure red', False), \
            #         ")", sep='')
            # self.cumul_rewards = {'Score':0, 'Lines':0, 'Holes':0, 'Height':0, 'Bumpiness':0, '↓':0, 'Nb Tetro':0}

            if PRINT_GAME_AREAS:
                print(f'Current Tetromino:\n{TetrisInfos.print_tetromino(self._current_tetromino)}')
                print(f'Next Tetromino:\n{TetrisInfos.print_tetromino(self.next_tetromino())}')

            if PRINT_GAME_AREAS:
                print(TetrisInfos.better_game_area(self.game_area()))

            if PLAY_MODE == 'Random' or PLAY_MODE == 'Agent':
                # Fix to allow spamming down button when a new tetromino spawn
                self.pyboy.button_release('down')

        # Update values
        self._last_spawner_area = self.spawner_area
        self._last_game_area = self.game_area()

        self._last_time_fps = time.time()

        return tick

    def new_tetromino_spawned(self, game_area, last_game_area):
        # Dictionnaire contenant le compte de valeurs uniques dans la zone de jeu de la frame précédente
        # ex: {0: 55, 7: 4} où la key 0 correspond à une case vide, et 7 à un tetromino 'I'
        unique_last = np.unique(last_game_area, return_counts=True)
        count_unique_last = {value:count for value, count in zip(unique_last[0], unique_last[1])}

        # Dictionnaire contenant le compte de valeurs uniques dans la zone de jeu actuelle
        unique = np.unique(game_area, return_counts=True)
        count_unique = {value:count for value, count in zip(unique[0], unique[1])}

        # Calcule de la différence entre la zone de jeu actuelle et la zone de jeu de la frame précédente
        # On est censé avoir une zone de jeu vide contenant uniquement les éléments en plus par rapport à la frame précédente
        current_tetromino_area = game_area - last_game_area
        # Vérification des valeurs issues de la soustraction:
        # pendant la phase de déplacements du current_tetromino, on peut avoir des valeurs négatives
        # (ou égales à 4 millions et quelques car game_area() est au format "uint32"), donc on les transforme en 0
        allowed_values = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        invalid_mask = ~np.isin(current_tetromino_area, allowed_values)
        current_tetromino_area[invalid_mask] = 0
        # TODO: Stocker une variable pour le game_area avec uniquement le current tetromino ?
        # Encore une fois on calcule le nombre de valeurs uniques, mais dans cette "différence" de zones de jeu
        unique_val, unique_count = np.unique(current_tetromino_area, return_counts=True)

        # Check si :
        #   -On a moins de case vide (de valeur "0") actuellement, par rapport à la frame précédente
        #   -La différence entre la zone de jeu actuelle et celle de la frame précédente renvoie une zone contenant uniquement des 0 (cases vide), et 4 cases d'une autre valeur (l'ID du nouveau tetromino)
        # Si c'est le cas, on renvoie le nouveau tetromino
        return (count_unique[0] < count_unique_last[0] and len(unique_val) == 2 and 4 in unique_count), self.get_current_tetromino(unique_val)

    def get_current_tetromino(self, unique_val):
            # Si dans la "différence" entre la zone de jeu actuelle et cette de la frame précédente, il n'y a pas que des 0 (cases vides) et uniquement 1 autre valeur (celle du nouveau tetromino),
            # c'est qu'on est dans un cas où une ligne a été détruite, et que cette ligne clignotte, donc on ne renvoie pas de nouveau tetromino
            if len(unique_val) != 2:
                return None

            list_unique_val = list(unique_val)
            # On retire la valeur 0 de la liste ("0" étant une case vide)
            list_unique_val.remove(0)
            # Il ne reste qu'un élément dans la liste, qui devrait correspondre à l'ID du nouveau tetromino
            current_tetromino = list_unique_val[0]
            # On convertit l'ID en "nom" de tetromino
            return TetrisInfos.get_tetromino_form(current_tetromino)
