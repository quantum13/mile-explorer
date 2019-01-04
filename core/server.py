from apps.explorer.models import Wallet
from core.config import SERVER_PORT, SERVER_WORKERS_COUNT
from core.di import app


@app.route("/")
async def temp(request):
    Wallet()


def start():
    app.run(workers=SERVER_WORKERS_COUNT, port=SERVER_PORT)





