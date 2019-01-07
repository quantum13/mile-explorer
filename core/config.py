from core.common import require_env

DEBUG = require_env('ENVIRONMENT') == 'dev'

SERVER_PORT = 8080
SERVER_WORKERS_COUNT = 1

DB_USER = require_env('DB_USER')
DB_PASSWORD = require_env('DB_PASSWORD')
DB_HOST = require_env('DB_HOST')
DB_NAME = require_env('DB_NAME')

SERVER_DB_POOL_MIN_SIZE = 10
SERVER_DB_POOL_MAX_SIZE = 45

INDEXER_DB_POOL_MIN_SIZE = 30
INDEXER_DB_POOL_MAX_SIZE = 45
INDEXER_TASKS_LIMIT = 40
# todo posgres limit ->200

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