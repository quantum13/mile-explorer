from core.common import require_env

SERVER_PORT = 8080
SERVER_WORKERS_COUNT = 1

DB_USER = require_env('DB_USER')
DB_PASSWORD = require_env('DB_PASSWORD')
DB_HOST = require_env('DB_HOST')
DB_NAME = require_env('DB_NAME')
DB_POOL_MIN_SIZE = 50
DB_POOL_MAX_SIZE = 100

TASKS_LIMIT = 50

WEB_WALLET_URL = 'https://wallet.testnet.mile.global'

