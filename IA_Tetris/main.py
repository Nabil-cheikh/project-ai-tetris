from pyboy import PyBoy
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris

def init_pyboy():
    pyboy = PyBoy(ROM_PATH) # déterminer le type d'affichage

    pyboy.set_emulation_speed(0) # déterminer la vitesse
    tetris = pyboy.game_wrapper
    tetris.game_area_mapping(tetris.mapping_compressed, 0)
    tetris.start_game(timer_div=None) # passer une seed random

    pyboy.tick()

    run_game(pyboy, tetris, 5) # déterminer le nombre d'épisodes

def run_game(pyboy, tetris, n_episodes = None):
    if n_episodes == None:
        ticks_loop(pyboy, tetris)
    else:
        run_n_episodes(pyboy, tetris, n_episodes)

def run_n_episodes(pyboy, tetris, n_episodes):
    for episode in range(n_episodes):
        ticks_loop(pyboy, tetris, )

def ticks_loop(pyboy, tetris):
    while pyboy.tick():
        one_tick(pyboy, tetris)

def one_tick(pyboy, tetris):
    # check Game Over
    # check spawn new tetromino
    # increment timer
    # check play or replay

    pass

if __name__ == '__main__':
    init_pyboy()
