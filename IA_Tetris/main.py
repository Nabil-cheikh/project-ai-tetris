from IA_Tetris.params import *
from IA_Tetris.Agent import TetrisAgent
from IA_Tetris.Environnement import TetrisEnv

def main():
    env = TetrisEnv()
    agent = TetrisAgent(mem_size=250000, epsilon=1.0, epsilon_min=0.01,
                 epsilon_decay=0.995, discount=0.95, replay_start_size=None)

    if PLAY_MODE == 'Agent':
        env.tetris.start_game(timer_div=env.seed)

        total_reward_list_episode = []  # Liste pour stocker les récompenses de chaque épisode

        for episode in range(NB_EPISODES):
            # Réinitialiser l'environnement et obtenir l'état initial
            env.reset()
            current_state = env.state()
            done = False
            total_reward = 0  # Initialiser la récompense totale pour cet épisode

            while not done:
                env.tetris.tick()
                print(f'Rewards: \n  Bumpiness: {env.bumpiness_rewards()}\n  Holes: {env.hole_rewards()}\n  Height: {env.heigh_rewards()}\n  game_over: {env.game_over_rewards()}\n  Score: {env.score_rewards()}\n  Lines: {env.lines_rewards()}')
                print(f"Current State: {current_state}")

                # Choisir la meilleure action en fonction de l'état actuel
                best_action = agent.best_state(current_state)
                env.actions(best_action)

                next_state = env.state()
                reward = env.get_rewards()
                done = env.game_over()
                total_reward += reward  # Ajouter la récompense à la récompense totale de l'épisode

                # Ajouter l'expérience dans la mémoire de l'agent
                agent.add_to_memory(current_state, next_state, best_action, reward)

                # Mettre à jour l'état courant
                current_state = next_state

                # Si l'épisode est terminé, afficher les résultats
                if done:
                    total_reward_list_episode.append(total_reward)
                    print(f"Episode: {episode+1}/{NB_EPISODES}, Score: {env.get_results()}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.2f}")
                    break

            # Entraîner l'agent après chaque épisode
            agent.train(batch_size=BATCH_SIZE, epochs=EPOCHS)

            # Réduire epsilon après chaque épisode pour favoriser l'exploitation
            if agent.epsilon > agent.epsilon_min:
                agent.epsilon *= agent.epsilon_decay

        # Fermer l'environnement après l'entraînement
        print(f"Total Rewards for all episodes: {total_reward_list_episode}")
        env.close()

    else:
        env.run_game(NB_EPISODES)


if __name__ == '__main__':
    main()
