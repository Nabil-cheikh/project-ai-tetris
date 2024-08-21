from pyboy import pyboy
from pyboy.core.mb import Motherboard
from pyboy import PyBoy
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris

def init_pyboy():
    pyboy_argv = {
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

    mb = Motherboard(
            ROM_PATH,
            pyboy_argv['bootrom'],
            pyboy_argv["color_palette"],
            pyboy_argv["cgb_color_palette"],
            pyboy_argv['sound'],
            pyboy_argv['sound_emulated'],
            pyboy_argv['cgb'],
            randomize=False,
        )

    pyboy_env = PyBoy(gamerom=ROM_PATH,
                      window=pyboy_argv['window'],
                      scale=pyboy_argv['scale'],
                      symbols=pyboy_argv['symbols'],
                      bootrom=pyboy_argv['bootrom'],
                      sound=pyboy_argv['sound'],
                      sound_emulated=pyboy_argv['sound_emulated'],
                      cgb=pyboy_argv['cgb'],
                      log_level=pyboy_argv['log_level'],
                      color_palette=pyboy_argv['color_palette'],
                      cgb_color_palette=pyboy_argv['cgb_color_palette']) # déterminer le type d'affichage

    pyboy_env.set_emulation_speed(0) # déterminer la vitesse
    #tetris = pyboy_env.game_wrapper

    tetris = Tetris(pyboy_env, mb, pyboy_argv)
    tetris.game_area_mapping(tetris.mapping_compressed, 0)
    tetris.start_game(timer_div=None) # passer une seed random

    pyboy_env.tick()

    run_game(pyboy_env, tetris, 5) # déterminer le nombre d'épisodes

def run_game(pyboy_env, tetris, n_episodes = None):
    if n_episodes == None:
        ticks_loop(pyboy_env, tetris)
    else:
        run_n_episodes(pyboy_env, tetris, n_episodes)

def run_n_episodes(pyboy_env, tetris, n_episodes):
    for episode in range(n_episodes):
        ticks_loop(pyboy_env, tetris, )

def ticks_loop(pyboy_env, tetris):
    while pyboy_env.tick():
        one_tick(pyboy_env, tetris)

def one_tick(pyboy_env, tetris):
    # check Game Over
    # check spawn new tetromino
    # increment timer
    # check play or replay

    pass

if __name__ == '__main__':
    init_pyboy()
