from IA_Tetris.params import *
from IA_Tetris.utils import PrintColor
from tensorflow import keras
from google.cloud import storage
import pickle
import time
import glob

def save_model(model, name, use_timestamp=False):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_name = f'{name}-{timestamp}.keras' if use_timestamp else f'{name}.keras'
    path = os.path.join(MODEL_PATH, f'{file_name}')
    print(PrintColor.cstr_with_arg(f'[Local] Saved model at path: {path}', \
        'pure green', True))
    model.save(path)

    if MODEL_TARGET == 'gcs':
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f'models/{file_name}')
        blob.upload_from_filename(file_name)
        print(PrintColor.cstr_with_arg(f'[GCS] Saved model on bucket {BUCKET_NAME} at path: models/{file_name}', \
            'pure green', True))

def load_model():
    if MODEL_TARGET == 'local':
        paths = glob.glob(f'{MODEL_PATH}/*')

        if not paths:
            print(PrintColor.cstr_with_arg('No model to load', 'pure red', True))
            return None

        most_recent_model_path = sorted(paths)[-1]

        print(PrintColor.cstr_with_arg(f'[Local] Loaded model from path: {most_recent_model_path}', \
            'pure green', True))
        return keras.models.load_model(most_recent_model_path)

    elif MODEL_TARGET == 'gcs':
        client = storage.Client()
        blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix='model'))

        try:
            latest_blob = max(blobs, key=lambda x: x.updated)
            latest_model_path_to_save = os.path.join(MODEL_PATH, latest_blob.name)
            latest_blob.download_to_filename(latest_model_path_to_save)

            print(PrintColor.cstr_with_arg(f'[GCS] Loaded model from bucket: {BUCKET_NAME}', \
                'pure green', True))
            return keras.models.load_model(latest_model_path_to_save)
        except:
            print(PrintColor.cstr_with_arg('No model to load', 'pure red', True))
            return None

    return None

def save_checkpoint(model, memory, epsilon, episode, name):
    check_file_name = f'{name}.h5'
    path = os.path.join(CHECKPOINT_PATH, f'{check_file_name}')
    model.save_weights(path)

    memo_file_name = 'memory.pkl'
    with open(os.path.join(CHECKPOINT_PATH, memo_file_name), 'wb') as f:
        pickle.dump(memory, f)
    agent_state = {'epsilon': epsilon, 'episode':episode}
    as_file_name = 'agent_state.pkl'
    with open(os.path.join(CHECKPOINT_PATH, as_file_name), 'wb') as f:
        pickle.dump(agent_state, f)
    print(PrintColor.cstr_with_arg(f'[Local] Saved checkpoint for episode {episode} (memory size: {len(memory)}, epsilon: {epsilon}) at path: {path}', \
        'pure green', True))

    if MODEL_TARGET == 'gcs':
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f'checkpoint/{check_file_name}')
        blob.upload_from_filename(check_file_name)
        blob = bucket.blob(f'checkpoint/{memo_file_name}')
        blob.upload_from_filename(memo_file_name)
        blob = bucket.blob(f'checkpoint/{as_file_name}')
        blob.upload_from_filename(as_file_name)
        print(PrintColor.cstr_with_arg(f'[GCS] Saved checkpoint on bucket {BUCKET_NAME} for episode {episode}  (memory size: {len(memory)}, epsilon: {epsilon}) at path: checkpoint/{check_file_name} + {memo_file_name} + {as_file_name}', \
            'pure green', True))

def load_checkpoint(model):
    check_file_name = 'model.weights.h5'
    memo_file_name = 'memory.pkl'
    as_file_name = 'agent_state.pkl'

    if MODEL_TARGET == 'local':
        path = os.path.join(CHECKPOINT_PATH, check_file_name)
        model.load_weights(path)

        with open(os.path.join(CHECKPOINT_PATH, memo_file_name), 'rb') as f:
            memory = pickle.load(f)
        with open(os.path.join(CHECKPOINT_PATH, as_file_name), 'rb') as f:
            agent_state = pickle.load(f)

        print(PrintColor.cstr_with_arg(f"[Local] Loaded checkpoint at episode {agent_state['episode']} (memory size: {len(memory)}, epsilon: {agent_state['epsilon']}) from path: {path}", \
            'pure green', True))
        return memory, agent_state['epsilon'], agent_state['episode']
    elif MODEL_TARGET == 'gcs':
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        check_path = os.path.join(CHECKPOINT_PATH, check_file_name)
        memo_path = os.path.join(CHECKPOINT_PATH, memo_file_name)
        as_path = os.path.join(CHECKPOINT_PATH, as_file_name)

        try:
            blob_check = bucket.blob(f'checkpoint/{check_file_name}')
            blob_check.download_to_filename(check_path)
            model.load_weights(check_path)

            blob_memo = bucket.blob(f'checkpoint/{memo_file_name}')
            blob_memo.download_to_filename(memo_path)
            with open(os.path.join(CHECKPOINT_PATH, memo_file_name), 'rb') as f:
                memory = pickle.load(f)

            blob_as = bucket.blob(f'checkpoint/{as_file_name}')
            blob_as.download_to_filename(as_path)
            with open(os.path.join(CHECKPOINT_PATH, as_file_name), 'rb') as f:
                agent_state = pickle.load(f)

            print(PrintColor.cstr_with_arg(f"[GCS] Loaded checkpoint from bucket: {BUCKET_NAME} for episode {agent_state['episode']} (memory size: {len(memory)}, epsilon: {agent_state['epsilon']})", \
                'pure green', True))
            return memory, agent_state['epsilon'], agent_state['episode']
        except:
            print(PrintColor.cstr_with_arg('No checkpoint to load', 'pure red', True))
            return None, None, None

    return None, None, None
