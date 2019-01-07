from apps.explorer.models import Wallet
from core.config import SERVER_PORT, SERVER_WORKERS_COUNT, DEBUG
from core.di import app
from apps.explorer.controllers import *


def start():
    app.run(workers=SERVER_WORKERS_COUNT, port=SERVER_PORT, debug=DEBUG)





