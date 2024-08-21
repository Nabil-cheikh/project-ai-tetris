from pyboy import pyboy
from pyboy.core.mb import Motherboard
from pyboy import PyBoy
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv
from IA_Tetris.utils import TetrisInfos

def main():
    agent = None
    # agent = TetrisAgent()
    env = TetrisEnv(ROM_PATH)

    env.run_game(NB_EPISODES) # déterminer le nombre d'épisodes

def game_over(episode, print_infos, df, play_time, reward, score, lines, nb_tetrominos_used, seed, inputs):
    # Values we have to saved on a DataFrame
    print('GAME OVER')
    minutes = int(play_time // 60)
    seconds = int(play_time - minutes * 60)
    milliseconds = int((play_time - minutes * 60 - seconds)*1000)
    time = '{:02d}:{:02d}.{:03d}'.format(minutes, seconds, milliseconds)
    if print_infos:
        print(f"[Episode {episode}] Game Infos:\
                    \n-Total Rewards:{reward}\
                    \n-Game Score:{score}\
                    \n-Lines:{lines}\
                    \n-Time:{time}\
                    \n-Tetrominos used:{nb_tetrominos_used}")
    df = TetrisInfos.update_datas(df, time, score, lines, reward, nb_tetrominos_used, seed, inputs)
    return df

if __name__ == '__main__':
    main()
