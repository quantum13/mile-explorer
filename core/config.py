from core.common import require_env

DEBUG = require_env('ENVIRONMENT') == 'dev'

SERVER_PORT = 8080
SERVER_WORKERS_COUNT = 1

DB_USER = require_env('DB_USER')
DB_PASSWORD = require_env('DB_PASSWORD')
DB_HOST = require_env('DB_HOST')
DB_NAME = require_env('DB_NAME')
DB_POOL_MIN_SIZE = 50
DB_POOL_MAX_SIZE = 100

TASKS_LIMIT = 50

if require_env('NETWORK') == 'testnet':
    WEB_WALLET_URL = 'https://wallet.testnet.mile.global'
    GENESIS_BLOCK = './data/genesis_block_testnet.txt'
elif require_env('NETWORK') == 'mainnet':
    WEB_WALLET_URL = 'https://wallet.mile.global'
    GENESIS_BLOCK = './data/genesis_block.txt'
else:
    assert False


