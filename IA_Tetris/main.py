from pyboy import pyboy
from pyboy.core.mb import Motherboard
from pyboy import PyBoy
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv
from IA_Tetris.utils import TetrisInfos
import pandas as pd

df = None

def main():
    agent = None
    # agent = TetrisAgent()
    env = TetrisEnv(ROM_PATH)

    env.run_game(NB_EPISODES) # déterminer le nombre d'épisodes

if __name__ == '__main__':
    main()
