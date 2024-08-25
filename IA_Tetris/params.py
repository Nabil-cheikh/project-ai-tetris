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
SHOW_GAME_WINDOW = True
GAME_SPEED = 0 # 0 > max speed
SEED = 1
NB_EPISODES = 500
GB_NORMAL_FPS = 59.73
PLAY_MODE = 'Agent' # 'Random'/'Human'/'Agent'

# Prints debug infos
PRINT_GAME_AREAS = True
PRINT_GAME_OVER_INFOS = True

# Agent
BATCH_SIZE = 64
EPOCHS = 20

# Datas
DATAS_STEP = 'Test' # 'Test' > replace csv / 'Prod' > add new datas to last csv

############ CONSTANTS ############
COLUMN_NAMES = ['Time', 'Score', 'Lines', 'Rewards', 'NbBlocUsed', 'Seed', 'Inputs']

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
