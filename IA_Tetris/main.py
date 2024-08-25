from IA_Tetris.params import *
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv

def main():
    env = TetrisEnv()
    # state_size = env.game_area().shape[0] * env.game_area_only().shape[1]  # Adjust based on your state representation
    agent = TetrisAgent(mem_size=250000, epsilon=1.0, epsilon_min=0.01,
                 epsilon_decay=0.995, discount=0.99, replay_start_size=None, learning_rate=0.001)
    # agent.state_size = state_size  # Set the state size in the agent

    if PLAY_MODE == 'Agent':

        env.tetris.start_game(timer_div=env.seed)

        for episode in range(NB_EPISODES):
            # Reset environment and get the initial state
            env.reset()
            current_state = env.state()
            #current_state = np.reshape(current_state, [1, state_size])

            done = False
            while not done:
                env.tetris.tick()
                print(f'----Rewards----- \n Bumpiness: {env.bumpiness_penalty()}\n Holes: {env.hole_rewards()}\n Height: {env.height_penalty()}\n Game_over: {env.game_over_rewards()}\n Score: {env.score_rewards()}\n Lines: {env.lines_rewards()}\n Compactness : {env.compactness_reward()}\n Cavity : {env.cavity_penalty()}\n Edge alignement : {env.edge_alignment_reward()}')
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
                    print(f"Episode: {episode + 1}/{NB_EPISODES}, Score: {env.get_rewards()}")
                    # TODO: Sauvegarder le modèle
                    # TODO: Faire des checkpoints
                    break

            # Train the agent after every episode
            agent.train(batch_size=BATCH_SIZE, epochs=EPOCHS)

            # Decrease epsilon after each episode
            if agent.epsilon > agent.epsilon_min:
                agent.epsilon *= agent.epsilon_decay

        # Close the environment after training
        env.close()

    else:
        env.run_game(NB_EPISODES)

if __name__ == '__main__':
    main()
