from collections import deque
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import numpy as np
from IA_Tetris.Environnement import TetrisEnv

class TetrisAgent:

    def __init__(self, mem_size=250000, epsilon=1.0, epsilon_min=0.01,
                 epsilon_decay=0.995, discount=0.99, replay_start_size=None, learning_rate=0.001):
        self.action_size = 4  # down, left, right, rotate
        self.memory = deque(maxlen=mem_size)
        if not replay_start_size:
            replay_start_size = mem_size // 2
        self.replay_start_size = replay_start_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.discount = discount
        self.state_size = 12 # Correspond au nombre de récompenses dans l'état

        self.model = self._build_model(learning_rate)

    def _build_model(self, learning_rate):
        '''Construire un modèle de réseau neuronal Keras'''
        model = Sequential()
        model.add(Dense(units=128, input_dim=self.state_size, activation="relu"))
        model.add(Dense(units=64, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(learning_rate=learning_rate))
        return model

    def add_to_memory(self, current_state, next_state, action, reward, done):
        '''Ajouter un état à la mémoire de l'expérience replay'''
        self.memory.append((current_state, next_state, action, reward, done))

    def predict_value(self, state):
        '''Prédire le score pour un certain état'''
        state = np.reshape(state, [1, self.state_size])
        return self.model.predict(state, verbose=0)[0]

    def generate_action_sequences(self, max_length=1):
        '''Génère toutes les séquences d'actions possibles jusqu'à une longueur donnée'''
        actions = [0, 1, 2, 3]  # Correspond à down, left, right, rotate
        sequences = [[]]

        for _ in range(max_length):
            sequences = [seq + [action] for seq in sequences for action in actions]

        return sequences


    def apply_action_sequence(self, game_area, action_sequence, tetromino_id):
        '''Applique une séquence d'actions à la grille de jeu actuelle'''
        new_state = np.copy(game_area)
        for action in action_sequence:
            new_state = self.apply_action(new_state, action, tetromino_id)
        return new_state

    def apply_action(self, game_area, action, tetromino_id):
        new_game_area = np.copy(game_area)
        current_position, current_shape = self.get_tetromino_position_and_shape(new_game_area, tetromino_id)
        if current_position is None or current_shape is None:
            return game_area

        if action == 0:
            new_position = (current_position[0] + 1, current_position[1])
        elif action == 1:
            new_position = (current_position[0], current_position[1] - 1)
        elif action == 2:
            new_position = (current_position[0], current_position[1] + 1)
        elif action == 3:
            current_shape = self.rotate_tetromino(current_shape)
            new_position = current_position

        if self.is_valid_move(new_game_area, new_position, current_shape):
            for pos in current_position:
                new_game_area[pos[0], pos[1]] = 0

            for block in current_shape:
                new_row = new_position[0] + block[0]
                new_col = new_position[1] + block[1]
                new_game_area[new_row, new_col] = tetromino_id
        else:
            return game_area

        return new_game_area

    def get_tetromino_position_and_shape(self, game_area, tetromino_id):
        positions = []
        shape = []

        for i in range(game_area.shape[0]):
            for j in range(game_area.shape[1]):
                if game_area[i, j] == tetromino_id:
                    positions.append((i, j))

        if not positions:
            # On peut lever une exception, retourner None, ou gérer cela autrement selon votre besoin
            return None, None

        # Déduire la forme en utilisant la position la plus haute et la plus à gauche comme origine
        origin = min(positions)
        shape = [(pos[0] - origin[0], pos[1] - origin[1]) for pos in positions]

        return origin, shape

    def best_action_sequence(self, env):
        '''Retourne la meilleure séquence d'actions pour l'état actuel'''
        best_sequence = None
        best_score = -float('inf')

        game_area = env.game_area()
        tetromino_id = env.get_current_tetromino_id()  # Utiliser la bonne méthode pour obtenir le tetromino actuel

        action_sequences = self.generate_action_sequences()

        for sequence in action_sequences:
            simulated_state = self.apply_action_sequence(game_area, sequence, tetromino_id)
            reward = self.evaluate_state(env, simulated_state)

            if reward > best_score:
                best_score = reward
                best_sequence = sequence

        # Choisir une séquence aléatoire si aucune séquence optimale n'est trouvée
        if best_sequence is None or random.random() <= self.epsilon:
            best_sequence = random.choice(action_sequences)

        return best_sequence

    def evaluate_state(self, env, game_area):
        '''Évalue l'état après avoir appliqué une séquence d'actions'''
        return env.get_rewards()

    def train(self, batch_size=64, epochs=1):
        n = len(self.memory)
        if n >= self.replay_start_size and n >= batch_size:
            batch = random.sample(self.memory, batch_size)

            x = []
            y = []

            for state, next_state, action, reward, done in batch:
                target = reward
                if not done:
                    next_q_values = self.predict_value(next_state)
                    target = reward + self.discount * np.max(next_q_values)

                q_values = self.predict_value(state)
                q_values[action] = target

                x.append(state)
                y.append(q_values)

            self.model.fit(np.array(x), np.array(y), batch_size=batch_size, epochs=epochs, verbose=0)

            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                self.epsilon = max(self.epsilon_min, self.epsilon)
