from collections import deque
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import numpy as np
from IA_Tetris.registry import *
from IA_Tetris.params import *

class TetrisAgent:

    def __init__(self, mem_size=10000, epsilon=1.0, epsilon_min=0.01,
                 epsilon_decay=0.001, discount=0.95, replay_start_size=None, state_size=5):
        self.action_size = 4 # down, left, right, orientation
        self.memory = deque(maxlen=mem_size)
        if not replay_start_size:
            replay_start_size = mem_size / 2
        self.replay_start_size = replay_start_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.discount = discount
        self.state_size = state_size

        if DATAS_STEP == 'Prod':
            self.model, self.memory, self.epsilon = load_model()
            if self.model == None:
                self.model = self._build_model()
        else:
            self.model = self._build_model()


    def _build_model(self):
        '''Builds a Keras deep neural network model'''
        model = Sequential()
        model.add(Dense(units=64, input_dim=self.state_size, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(units=8, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(learning_rate=0.001))

        return model

    def add_to_memory(self, current_state, next_state, action, reward):
        '''Adds a play to the experience replay memory buffer'''
        self.memory.append((current_state, next_state, action, reward))


    def predict_value(self, state):
        '''Predicts the score for a certain state'''
        state = np.reshape(state, [1, self.state_size])
        return self.model.predict(state, verbose=0)[0]


    def best_state(self, states):
        '''Returns the best state for a given collection of states'''
        max_value = None
        best_state = None

        if random.random() <= self.epsilon:
            return random.choice([0, 1, 2, 3])

        else:
            try:
                for state in states:
                    value = self.predict_value(np.reshape(state, [1, self.state_size]))

                    if not max_value or value > max_value:
                        max_value = value
                        best_state = state
            except:
                print(PrintColor.cstr_with_arg('Failed to predict best state', 'pure red', True))
                return random.choice([0, 1, 2, 3])

        return best_state


    def train(self, batch_size=64, epochs=3):
        n = len(self.memory)

        if n >= self.replay_start_size and n >= batch_size:
            batch = random.sample(self.memory, batch_size)

            # Extract states, next states, actions, and rewards from the batch
            states = np.array([x[0] for x in batch], dtype=np.float32)
            next_states = np.array([x[1] for x in batch], dtype=np.float32)
            actions = np.array([x[2] for x in batch], dtype=np.int32)
            rewards = np.array([x[3] for x in batch], dtype=np.float32)

            # Predict Q-values for current states and next states
            # print(PrintColor.cstr_with_arg(f"Agent is training with next_states (shape {next_states.shape})\n  First element: {next_states[0]}", 'cyan', True))
            q_values = self.model.predict(states, verbose=0)
            next_q_values = self.model.predict(next_states, verbose=0)

            # Initialize target values
            y = q_values.copy()

            for i in range(batch_size):
                action = actions[i]
                if rewards[i] != -1000:
                    y[i][action] = rewards[i] + self.discount * np.max(next_q_values[i])
                else:
                    y[i][action] = rewards[i]

            # Fit the model to the target Q-values
            self.model.fit(states, y, batch_size=batch_size, epochs=epochs, verbose=0)

            # Update the exploration rate
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                self.epsilon = max(self.epsilon_min, self.epsilon)
