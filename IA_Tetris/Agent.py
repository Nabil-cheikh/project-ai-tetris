from collections import deque
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import numpy as np

class TetrisAgent:

    def __init__(self, mem_size=250000, epsilon=1.0, epsilon_min=0.01,
                 epsilon_decay=0.995, discount=0.99, replay_start_size=None, learning_rate=0.001):
        self.action_size = 4  # down, left, right, rotate
        self.memory = deque(maxlen=mem_size)
        if not replay_start_size:
            replay_start_size = mem_size / 2
        self.replay_start_size = replay_start_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.discount = discount
        self.state_size = 10  # Adjust this to match your state size

        self.model = self._build_model(learning_rate)

    def _build_model(self, learning_rate):
        '''Builds a Keras deep neural network model'''
        model = Sequential()
        model.add(Dense(units=128, input_dim=self.state_size, activation="relu"))
        model.add(Dense(units=64, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(learning_rate=learning_rate))

        return model

    def add_to_memory(self, current_state, next_state, action, reward):
        '''Adds a play to the experience replay memory buffer'''
        self.memory.append((current_state, next_state, action, reward))

    def predict_value(self, state):
        '''Predicts the score for a certain state'''
        state = np.reshape(state, [1, self.state_size])
        return self.model.predict(state, verbose=0)[0]

    def best_state(self, state):
        '''Returns the best action for a given state'''
        if random.random() <= self.epsilon:
            return random.choice([0, 1, 2, 3])
        q_values = self.predict_value(state)
        return np.argmax(q_values)

    def train(self, batch_size=64, epochs=1):
        '''Trains the agent'''
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
