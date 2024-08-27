from collections import deque
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from IA_Tetris.registry import load_model
from IA_Tetris.params import *
import numpy as np

class TetrisAgent:

    def __init__(self, mem_size=10000, epsilon=1.0, epsilon_min=0.01,
                 epsilon_decay=0.001, discount=0.95, replay_start_size=None):
        self.action_size = 4 # down, left, right, orientation
        self.memory = deque(maxlen=mem_size)
        if not replay_start_size:
            replay_start_size = mem_size / 2
        self.replay_start_size = replay_start_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.discount = discount
        self.state_size = 4

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
        return self.model.predict(state, verbose=0)[0]


    def best_state(self, states):
        '''Returns the best state for a given collection of states'''
        max_value = None
        best_state = None

        if random.random() <= self.epsilon:
            return random.choice(list(states))

        else:
            for state in states:
                value = self.predict_value(np.reshape(state, [1, self.state_size]))

                if not max_value or value > max_value:
                    max_value = value
                    best_state = state

        return best_state


    def train(self, batch_size=32, epochs=3):
        '''Trains the agent'''
        n = len(self.memory)
        print("taille de la mémoire", n)

        # If the memory is less than the maximal size of ex replay, and it's bigger than our batch size
        if n >= self.replay_start_size and n >= batch_size:
            print("train")

            batch = random.sample(self.memory, batch_size)

            # Get the expected score for the next states, in batch (better performance)

            next_states = np.array([x[1] for x in batch])
            next_qs = [x[0] for x in self.model.predict(next_states)]

            x = []
            y = []

            # Build xy structure to fit the model in batch (better performance)
            for i, (state, _, reward, done) in enumerate(batch):
                if not done:
                    # Partial Q formula
                    new_q = reward + self.discount * next_qs[i]
                else:
                    new_q = reward

                x.append(state)
                y.append(new_q)

            # Fit the model to the given values
            self.model.fit(np.array(x), np.array(y), batch_size=batch_size, epochs=epochs, verbose=0)

            # Update the exploration variable
            if self.epsilon > self.epsilon_min:
                self.epsilon -= self.epsilon_decay
