import random
from IA_Tetris.params import *
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv
from IA_Tetris.utils import TetrisInfos
from IA_Tetris.registry import *

def main():
    env = TetrisEnv()
    # state_size = env.game_area().shape[0] * env.game_area_only().shape[1]  # Adjust based on your state representation
    agent = TetrisAgent(mem_size=20000, discount=0.95)
    # agent.state_size = state_size  # Set the state size in the agent

    start_episode = 0
    if USE_CHECKPOINT:
        check_memory, check_epsilon, check_start_episode = load_checkpoint(agent.model)
        if check_memory != None and check_epsilon != None:
            agent.memory = check_memory
            agent.epsilon = check_epsilon
            start_episode = check_start_episode

    if PLAY_MODE == 'Agent':

        env.tetris.start_game(timer_div=env.seed)

        for episode in range(start_episode, NB_EPISODES):
            # Reset environment and get the initial state
            env.reset()
            current_state = env.state()
            #current_state = np.reshape(current_state, [1, state_size])

            done = False
            best_action = None
            is_action_finished = True
            total_reward = 0
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


                        current_piece_positions = TetrisInfos.TETROMINOS[current_piece_id][best_action[1]]
                        curr_piece_position = sorted(current_piece_positions, key=lambda pos: (pos[0], -pos[1]))[0]
                        # Take the action and observe the new state and reward
                        curr_piece_position, is_action_finished = env.actions(best_action, curr_piece_position, rotation_done)

                        lines, total_bumpiness, holes, sum_height = next_states[best_action]
                        reward = env.score_rewards() + (1+lines) ** 2 - (total_bumpiness+holes+sum_height)
                        # Add the experience to the agent's memory
                        agent.add_to_memory(current_state, next_states[best_action], reward, done)
                        # Update the current state
                        current_state = next_states[best_action]

                        done = env.game_over()
                        print(done)
                        if done:
                            # print(f"Episode: {episode + 1}/{NB_EPISODES}, Score: {env.get_rewards}")
                            # print(f'Rewards: \n  Bumpiness: {env.bumpiness_rewards()}\n  Holes: {env.hole_rewards()}\n  Height: {env.heigh_rewards()}\n  Score: {env.score_rewards()}\n  Lines: {env.lines_rewards()}')
                            # print(f'Epsilon: {agent.epsilon}')
                            print("je passe dans le if done")
                            env.get_results()
                            break
                    if len(next_states) == 0:
                        env.get_results()
                        break

                    current_piece_positions = TetrisInfos.TETROMINOS[current_piece_id][best_action[1]]
                    curr_piece_position = sorted(current_piece_positions, key=lambda pos: (pos[0], -pos[1]))[0]
                    # Take the action and observe the new state and reward
                    curr_piece_position, is_action_finished = env.actions(best_action, curr_piece_position, rotation_done)

                    lines, total_bumpiness, holes, max_height, total_tetrominos = next_states[best_action]
                    reward = env.score_rewards() + (1+lines) ** 2 + total_tetrominos
                    penalty = (total_bumpiness + holes + max_height)*2
                    total_reward = reward - penalty

                    # Add the experience to the agent's memory
                    agent.add_to_memory(current_state, next_states[best_action], total_reward, done)
                    # Update the current state
                    current_state = next_states[best_action]

                if env.tetris.frames_until_tetro_spawn % 2 == 1: # pyboy.button calls 2 states : do input in current frame, and release input in next frame
                    env.execute_actions()

                done = env.game_over()
                # If done, print the score
                if done:
                    print(f"Episode: {episode + 1}/{NB_EPISODES}") #, Score: {env.get_rewards}")
                    # print(f'Rewards: \n  Bumpiness: {env.bumpiness_rewards()}\n  Holes: {env.hole_rewards()}\n  Height: {env.heigh_rewards()}\n  Score: {env.score_rewards()}\n  Lines: {env.lines_rewards()}')
                    # print(f'Epsilon: {agent.epsilon}')
                    print("if done", total_reward)
                    env.get_results(total_reward)
                    # TODO: Sauvegarder le modèle
                    # TODO: Faire des checkpoints
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
