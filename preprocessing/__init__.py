import os

if not os.getenv('ENV_STATUS') == '1':
    import utils  # This loads vars, do not remove
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from preprocessing.main import run_cleaner
