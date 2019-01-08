import apps.explorer.controllers  # for registering controllers
from core.config import SERVER_PORT, SERVER_WORKERS_COUNT, DEBUG, SSL_CERT, SSL_KEY
from core.di import app
from core.logging import setup_logging


def start():
    setup_logging('sanic.root', replace=True)
    setup_logging('sanic.error', replace=True)
    app.run(host='0.0.0.0', workers=SERVER_WORKERS_COUNT, port=SERVER_PORT, debug=DEBUG,
            ssl={'cert': SSL_CERT, 'key': SSL_KEY})





