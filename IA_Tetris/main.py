from IA_Tetris.params import *
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv
from IA_Tetris.utils import TetrisInfos
from IA_Tetris.registry import *

def main():
    env = TetrisEnv()

    if PLAY_MODE == 'Agent':
        agent = TetrisAgent(mem_size=MEMORY_MAX_SIZE, epsilon_min= EPSILON_MIN, discount=DISCOUNT)

        start_episode = 0
        if USE_CHECKPOINT:
            check_memory, check_epsilon, check_start_episode = load_checkpoint(agent.model)
            if check_memory != None and check_epsilon != None:
                agent.memory = check_memory
                agent.epsilon = check_epsilon
                start_episode = check_start_episode

        env.tetris.start_game(timer_div=env.seed)

        for episode in range(start_episode, NB_EPISODES):
            # Reset environment and get the initial state
            env.reset()
            current_state = env.state()
            #current_state = np.reshape(current_state, [1, state_size])

            done = False
            best_action = None
            total_reward = 0
            is_action_finished = True
            current_piece_id = TetrisInfos.get_tetromino_id(env.tetris.current_tetromino())


            while not done:
                env.tetris.tick()
                # Get the best action to take based on the current state
                best_state = current_state
                rotation_done=True
                if env.tetris.is_new_tetromino():
                    env.stack_actions = []
                    next_states = env.get_next_states()
                    best_state = agent.best_state(next_states.values())
                    rotation_done=False
                    for action, state in next_states.items():
                        if best_state == state:
                            best_action = action
                            break
                    if len(next_states) == 0:
                        env.get_results()
                        break

                    current_piece_positions = TetrisInfos.TETROMINOS[current_piece_id][best_action[1]]
                    curr_piece_position = sorted(current_piece_positions, key=lambda pos: (pos[0], -pos[1]))[0]
                    # Take the action and observe the new state and reward
                    curr_piece_position, is_action_finished = env.actions(best_action, curr_piece_position, rotation_done)

                    lines, total_bumpiness, holes, sum_height = next_states[best_action]
                    reward = env.score_rewards() + (1+lines*100) ** 2 + env.tetris.total_tetromino_used * 1.5
                    penalty = (total_bumpiness+holes+sum_height)*2
                    compensated_reward = reward - penalty
                    env.total_rewards += compensated_reward
                    # Add the experience to the agent's memory
                    agent.add_to_memory(current_state, next_states[best_action], compensated_reward, done)
                    # Update the current state
                    current_state = next_states[best_action]

                if env.tetris.frames_until_tetro_spawn % 2 == 1: # pyboy.button calls 2 states : do input in current frame, and release input in next frame
                    env.execute_actions()

                done = env.game_over()
                # If done, print the score
                if done:
                    print('-----------------------')
                    print(f"Episode: {episode + 1}/{NB_EPISODES}")
                    env.get_results()
                    print(f'Agent:\n  -Memory: {len(agent.memory)}/{agent.memory.maxlen}\n  -Epsilon: {round(agent.epsilon, 2)}/1')

                    if PRINT_GAME_OVER_AREA:
                        print(TetrisInfos.better_game_area(env.tetris._last_game_area))
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
