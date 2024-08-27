import random
import random
from IA_Tetris.params import *
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv
from IA_Tetris.utils import TetrisInfos
from IA_Tetris.registry import *

def main():
    env = TetrisEnv()
    # state_size = env.game_area().shape[0] * env.game_area_only().shape[1]  # Adjust based on your state representation
    agent = TetrisAgent(mem_size=10000, epsilon=1.0, epsilon_min=0.01,
                        epsilon_decay=0.001, discount=0.95)
    # agent.state_size = state_size  # Set the state size in the agent

    start_episode = 0
    if USE_CHECKPOINT:
        agent.memory, agent.epsilon, start_episode = load_checkpoint(agent.model)

    if PLAY_MODE == 'Agent':

        env.tetris.start_game(timer_div=env.seed)

        for episode in range(start_episode, NB_EPISODES):
            # Reset environment and get the initial state
            env.reset()
            current_state = env.state()
            #current_state = np.reshape(current_state, [1, state_size])

            done = False
            best_action = None
            current_piece_id = TetrisInfos.get_tetromino_id(env.tetris.current_tetromino())

            while not done:
                env.tetris.tick()
                # Get the best action to take based on the current state
                best_state = current_state
                rotation_done=True
                if env.tetris.is_new_tetromino():
                    env.stack_actions = []
                    next_states = env.get_next_states()
                    if len(next_states) != 0:
                        best_state = agent.best_state(next_states.values())
                        rotation_done=False
                        for action, state in next_states.items():
                            if best_state == state:
                                best_action = action
                                break
                    else:
                        env.get_results()
                        break

                current_piece_positions = TetrisInfos.TETROMINOS[current_piece_id][best_action[1]]
                curr_piece_position = sorted(current_piece_positions, key=lambda pos: (pos[0], -pos[1]))[0]
                # Take the action and observe the new state and reward
                curr_piece_position = env.actions(best_action, curr_piece_position, rotation_done)

                lines, total_bumpiness, holes, sum_height = next_states[best_action]
                reward = env.score_rewards() + (1+lines) ** 2 - (total_bumpiness+holes+sum_height)
                # Add the experience to the agent's memory
                agent.add_to_memory(current_state, next_states[best_action], reward, done)
                # Update the current state
                current_state = next_states[best_action]
                lines, total_bumpiness, holes, sum_height = next_states[best_action]
                reward = env.score_rewards() + (1+lines) ** 2 - (total_bumpiness+holes+sum_height)
                # Add the experience to the agent's memory
                agent.add_to_memory(current_state, next_states[best_action], reward, done)
                # Update the current state
                current_state = next_states[best_action]

                done = env.game_over()
                if done:
                    env.get_results()
                    break

            # Train the agent after every episode
            agent.train(batch_size=BATCH_SIZE, epochs=EPOCHS)

            if episode % CHECKPOINT_FREQUENCY == 0:
                save_checkpoint(agent.model, agent.memory, agent.epsilon, episode, 'model.weights')

        save_model(agent.model, agent.memory, agent.epsilon, 'model', True)
        # Close the environment after training
        env.close()

    else:
        env.run_game(NB_EPISODES)

if __name__ == '__main__':
    main()
