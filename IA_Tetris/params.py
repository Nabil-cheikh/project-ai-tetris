import os

############ VARIABLES ############
ROM_PATH = os.environ.get('ROM_PATH')
CSV_PATH = os.environ.get('CSV_PATH')
MODEL_TARGET = os.environ.get('MODEL_TARGET')

# GCP Project
GCP_PROJECT = os.environ.get('GCP_PROJECT')
GCP_REGION = os.environ.get('GCP_REGION')

# Cloud Storage
BUCKET_NAME = os.environ.get('BUCKET_NAME')

# BigQuery
BQ_REGION = os.environ.get('BQ_REGION')
BQ_DATASET = os.environ.get('BQ_DATASET')

# Game
SHOW_GAME_WINDOW = False
GAME_SPEED = 0 # 0 > max speed
SEED = 1
NB_EPISODES = 3500
GB_NORMAL_FPS = 59.73
PLAY_MODE = 'Agent' # 'Random'/'Human'/'Agent'/'Replay' (> replay the best party done by the agent)

# Prints debug infos
PRINT_GAME_AREAS = False
PRINT_GAME_OVER_INFOS = True
PRINT_GAME_OVER_AREA = False

# Agent
BATCH_SIZE = 512
EPOCHS = 10
MEMORY_MAX_SIZE = 10000
DISCOUNT = 0.95
EPSILON_MIN = 0.03
STATE_SIZE = 4

# Datas
DATAS_STEP = 'Prod' # 'Test' > replace csv / 'Prod' > add new datas to last csv

# Save models and checkpoints
MODEL_PATH = os.path.join('data', 'models')
CHECKPOINT_PATH = os.path.join('data', 'checkpoints')
USE_CHECKPOINT = True
CHECKPOINT_FREQUENCY = 10

############ CONSTANTS ############
COLUMN_NAMES = ['Time', 'Score', 'Lines', 'Rewards', 'NbBlocUsed', 'Seed', 'Inputs']

BOARD_WIDTH = 10
BOARD_HEIGHT = 18

DTYPES = {
    'Time': 'timestamp',
    'Score': 'int',
    'Lines': 'int',
    'Rewards': 'int',
    'NbBlocUsed': 'int',
    'Seed': 'int',
    'Inputs': 'list'
}

INPUTS = [
    'left',
    'right',
    'down',
    'a'
]
