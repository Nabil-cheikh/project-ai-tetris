from IA_Tetris.params import *
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv

def main():
    env = TetrisEnv()
    agent = TetrisAgent(mem_size=250000, epsilon=1.0, epsilon_min=0.01,
                        epsilon_decay=0.995, discount=0.99, replay_start_size=None, learning_rate=0.001)

    if PLAY_MODE == 'Agent':
        env.tetris.start_game(timer_div=env.seed)

        for episode in range(NB_EPISODES):
            env.reset()
            result =[]
            done = False

            while not done:
                env.tetris.tick()
                current_state = env.state()

                # Get the best action sequence to take based on the current game state
                best_action_sequence = agent.best_action_sequence(env)

                # Apply each action in the best sequence
                for action in best_action_sequence:
                    env.actions(action)

                 # Move to the next frame
                print(f'----Rewards----- \n Bumpiness: {env.bumpiness_penalty()}\n Holes: {env.hole_rewards()}\n Height: {env.height_penalty()}\n Game_over: {env.game_over_rewards()}\n Score: {env.score_rewards()}\n Lines: {env.lines_rewards()}\n Compactness: {env.compactness_reward()}\n Cavity: {env.cavity_penalty()}\n Edge alignment: {env.edge_alignment_reward()}\n Survival: {env.survival_reward()}')
                next_state = env.state()
                reward = env.get_rewards()
                done = env.game_over()

                # Add the experience to the agent's memory
                agent.add_to_memory(current_state, next_state, best_action_sequence, reward, done)

                # Update the current state
                current_state = next_state

                # If done, print the score and rewards
                if done:
                    print(f"Episode: {episode + 1}/{NB_EPISODES}")
                    print(f'--------------------TOTAL REWARD : {int(env.get_rewards())}------------------------')
                    result.append(int(env.get_rewards()))
                    break

            # Train the agent after each episode
            agent.train(batch_size=BATCH_SIZE, epochs=EPOCHS)



        # Close the environment after training
        print(result)
        env.close()

    else:
        env.run_game(NB_EPISODES)

if __name__ == '__main__':
    main()
