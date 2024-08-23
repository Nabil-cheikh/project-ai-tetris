from collections import deque
import random
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

class TetrisAgent:

    def __init__(self, mem_size=250000, epsilon=1.0, epsilon_min=0.01,
                 epsilon_decay=0.995, discount=0.95, replay_start_size=None):
        self.action_size = 4  # down, left, right, orientation
        self.memory = deque(maxlen=mem_size)
        if replay_start_size is None:
            replay_start_size = mem_size // 2
        self.replay_start_size = replay_start_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.discount = discount
        self.state_size = 6  # Assuming your state size is 6; adjust based on your state representation

        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(units=64, input_dim=self.state_size, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(units=8, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(learning_rate=0.001))
        return model

    def add_to_memory(self, current_state, next_state, action, reward):
        """Adds a play to the experience replay memory buffer."""
        self.memory.append((current_state, next_state, action, reward))

    def predict_value(self, state):
        """Predicts the Q-values for a certain state."""
        state = np.array(state, dtype=np.float32).reshape(1, self.state_size)
        return self.model.predict(state, verbose=0)[0]

    def best_state(self, current_state):
        """Returns the best action for a given state."""
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.action_size)
        else:
            q_values = self.predict_value(current_state)
            return np.argmax(q_values)

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
            q_values = self.model.predict(states, verbose=0)
            next_q_values = self.model.predict(next_states, verbose=0)

            # Initialize target values
            y = q_values.copy()

            for i in range(batch_size):
                action = actions[i]
                if rewards[i] != -1000:  # Assuming -1000 is the terminal state reward
                    y[i][action] = rewards[i] + self.discount * np.max(next_q_values[i])
                else:
                    y[i][action] = rewards[i]

            # Fit the model to the target Q-values
            self.model.fit(states, y, batch_size=batch_size, epochs=epochs, verbose=0)

            # Update the exploration rate
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                self.epsilon = max(self.epsilon_min, self.epsilon)  # Ensure epsilon doesn't go below epsilon_min
