from pyboy import pyboy
from pyboy.core.mb import Motherboard
from pyboy import PyBoy
from IA_Tetris.params import *
from IA_Tetris.Better_Tetris_Wrapper import Tetris
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv
from IA_Tetris.utils import TetrisInfos
import pandas as pd
import numpy as np

EPISODES = 1000
BATCH_SIZE = 32
EPOCHS = 3

def main():
    env = TetrisEnv(ROM_PATH)
    # state_size = env.game_area().shape[0] * env.game_area_only().shape[1]  # Adjust based on your state representation
    agent = TetrisAgent(mem_size=10000, epsilon=1.0, epsilon_min=0.01,
                        epsilon_decay=0.001, discount=0.95)
    # agent.state_size = state_size  # Set the state size in the agent

    env.tetris.start_game(timer_div=env.seed)
    env.tetris.tick()

    for episode in range(NB_EPISODES):
        # Reset environment and get the initial state
        env.reset()
        current_state = env.state()
        #current_state = np.reshape(current_state, [1, state_size])

        done = False
        while not done:
            env.tetris.tick()
            # Get the best action to take based on the current state
            best_action = agent.best_state([current_state])

            # Take the action and observe the new state and reward
            env.actions(best_action)
            next_state = env.state()
            #next_state = np.reshape(next_state, [1, state_size])
            reward = env.get_rewards()
            done = env.game_over()

            # Add the experience to the agent's memory
            agent.add_to_memory(current_state, next_state, best_action, reward)

            # Update the current state
            current_state = next_state

            # If done, print the score
            if done:
                print(f"Episode: {episode + 1}/{EPISODES}, Score: {env.get_rewards}")
                print(f'Rewards: \n  Bumpiness: {env.bumpiness_rewards()}\n  Holes: {env.hole_rewards()}\n  Height: {env.heigh_rewards()}\n  Frame: {env.frame_rewards()}\n  Score: {env.score_rewards()}\n  Lines: {env.lines_rewards()}')
                print(f'Epsilon: {agent.epsilon}')
                env.get_results()
                break

        # Train the agent after every episode
        agent.train(batch_size=BATCH_SIZE, epochs=EPOCHS)

        # Decrease epsilon after each episode
        if agent.epsilon > agent.epsilon_min:
            agent.epsilon *= agent.epsilon_decay

    # Close the environment after training
    env.close()

if __name__ == '__main__':
    main()
