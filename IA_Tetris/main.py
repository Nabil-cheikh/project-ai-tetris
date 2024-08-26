from IA_Tetris.params import *
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv
from IA_Tetris.registry import *
import random

def main():
    env = TetrisEnv()
    # state_size = env.game_area().shape[0] * env.game_area_only().shape[1]  # Adjust based on your state representation
    agent = TetrisAgent(mem_size=25000, epsilon=1.0, epsilon_min=0.01,
                        epsilon_decay=0.001, discount=0.95, state_size=len(env.state()))
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
            while not done:
                env.tetris.tick()
                # Get the best action to take based on the current state
                # next_states = env.get_next_states()
                # best_state = agent.best_state(next_states)

                best_action = random.choice([0, 1, 2, 3])

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
                    print(f'Episode: {episode + 1}/{NB_EPISODES}\
                          \n  Rewards:\
                          \n    Bumpiness: {env.bumpiness_rewards()}\
                          \n    Holes: {env.hole_rewards()}\
                          \n    Height: {env.heigh_rewards()}\
                          \n    Frame: {env.total_score_rewards}\
                          \n    Score: {env.total_lines_rewards}\
                          \n    Lines: {env.total_down_button_rewards}\
                          \n    Lines: {env.total_nb_tetrominos_rewards}\
                          \n  Agent:\
                          \n    Memory: {len(agent.memory)}/{agent.memory.maxlen}\
                          \n    Epsilon: {agent.epsilon}/1')
                    env.get_results()
                    break

            # Train the agent after every episode
            agent.train(batch_size=BATCH_SIZE, epochs=EPOCHS)

            # Decrease epsilon after each episode
            if agent.epsilon > agent.epsilon_min:
                agent.epsilon *= agent.epsilon_decay

            if episode % CHECKPOINT_FREQUENCY == 0:
                save_checkpoint(agent.model, agent.memory, agent.epsilon, episode, 'model.weights')

        save_model(agent.model, agent.memory, agent.epsilon, 'model', True)
        # Close the environment after training
        env.close()

    else:
        env.run_game(NB_EPISODES)

if __name__ == '__main__':
    main()
