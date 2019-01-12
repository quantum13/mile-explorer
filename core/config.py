from core.common import require_env

DEBUG = require_env('ENVIRONMENT') == 'dev'

SERVER_PORT = require_env('SERVER_PORT')
SERVER_WORKERS_COUNT = 1

SSL_CERT = require_env('SSL_CERT')
SSL_KEY = require_env('SSL_KEY')

DB_USER = require_env('DB_USER')
DB_PASSWORD = require_env('DB_PASSWORD')
DB_HOST = require_env('DB_HOST')
DB_NAME = require_env('DB_NAME')

SERVER_DB_POOL_MIN_SIZE = 30
SERVER_DB_POOL_MAX_SIZE = 120

INDEXER_DB_POOL_MIN_SIZE = {1: 30, 2: 2}
INDEXER_DB_POOL_MAX_SIZE = {1: 55, 2: 20}
INDEXER_TASKS_LIMIT = {1: 50, 2: 15}
# todo postgres limit ->200

if require_env('NETWORK') == 'testnet':
    WEB_WALLET_URL = 'https://wallet.testnet.mile.global'
    GENESIS_BLOCK = './data/genesis_block_testnet.txt'
elif require_env('NETWORK') == 'mainnet':
    WEB_WALLET_URL = 'https://wallet.mile.global'
    GENESIS_BLOCK = './data/genesis_block.txt'
else:
    assert False


API_VERIFY_SSL = False

PAGE_SIZE = 30


# LOGGING ##############

LOG_TELEGRAM_TOKEN = '740605683:AAFOHfQQQwMVICqrUNPk-OrbS8iJXhayfMM'
LOG_TELEGRAM_CHANNELS = {
    'CRITICAL': '-1001492636146',
    'FATAL': '-1001492636146',
    'ERROR': '-1001492636146',
}
LOG_TELEGRAM_CHANNELS_DEFAULT = '-1001321012251'
LOG_TELEGRAM_APP_NAME = require_env('LOG_TELEGRAM_APP_NAME')
