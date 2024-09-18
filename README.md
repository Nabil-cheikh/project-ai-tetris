# AI Model Beating Tetris

This project demonstrates an AI model that successfully plays and beats the classic game Tetris. The game is run using a ROM file through the PyBoy framework, and the AI model is trained using the Reinforcement Learning method called Deep Q-Learning.

## Table of Contents
- Introduction
- Installation
- Algorithm Choice
- Contributing
- Sources

## Introduction
This project showcases an AI model that can play Tetris, a popular tile-matching puzzle game. The game is emulated using the PyBoy framework, and the AI is trained using Deep Q-Learning, a reinforcement learning technique.

## Installation
To get started, clone the repository and follow these steps :

- Create a `.env` file containing these lines :
```
ROM_PATH='./data/rom/Tetris.gb'
CSV_PATH='./data/csv/games.csv'
MODEL_TARGET='local'
```
- Get the gameboy color ROM Tetris from an Emulator website, for this project, emulatorgames.net was used. Put the gb file inside the folder `./data/rom`
- Restart (or open) your terminal inside the project repository, and execute these lines :
```
pip install -r requirements.txt

make clear_directories

make run
```

If you want to interrupt the training process, and then restart it at the point it has been interrupted, just do `control + C` to stop it, and then `make run`to restart at the point.

If you want to reinitialize the training process, `control + C` then `make clean` and then `make run`. The model should restart from zero.

## Algorithm choice
For this project, we had different approaches, Q-Learning, Policy Gradient Method, Actor-Critics etc.. The Q-Learning algorithm was then chosen.

Q-Learning is a reinforcement learning algorithm that helps an agent learn to maximize rewards by taking the best actions based on its current state.
Deep Q-Learning enhance Q-Learning by using a deep neural-network to approximate the Q-values, allowing the agent to handle more complex environments.

## Contributing
The difficulty of this project is that we had 2 weeks to implement a model that works.
By overestimating the complexity of Tetris environments, we've chosen the Deep Q-Learning approach, but in the future, the project will be enriched with the Q-Learning approach (without the deep) to see if the model perform aswell. Feel free to customize this project, contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Sources
https://huggingface.co/learn/deep-rl-course/en/unit3/deep-q-algorithm

