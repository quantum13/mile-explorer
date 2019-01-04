from core.common import require_env

SERVER_PORT = 8080
SERVER_WORKERS_COUNT = 1

DB_USER = require_env('DB_USER')
DB_PASSWORD = require_env('DB_PASSWORD')
DB_HOST = require_env('DB_HOST')
DB_NAME = require_env('DB_NAME')
