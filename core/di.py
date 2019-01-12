import asyncio
from urllib.parse import urlunparse

from gino.ext.sanic import Gino
from sanic import Sanic
from sanic.request import Request
from sanic.response import redirect
from sanic_compress import Compress
from sanic_jinja2 import SanicJinja2

from core.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, SERVER_DB_POOL_MIN_SIZE, SERVER_DB_POOL_MAX_SIZE


app = Sanic(configure_logging=False)

app.config.REQUEST_MAX_SIZE = 4000
app.config.REQUEST_TIMEOUT = 15
app.config.RESPONSE_TIMEOUT = 20

app.config.ACCESS_LOG = False

app.config.DB_HOST = DB_HOST
app.config.DB_DATABASE = DB_NAME
app.config.DB_USER = DB_USER
app.config.DB_PASSWORD = DB_PASSWORD

app.config.DB_POOL_MIN_SIZE = SERVER_DB_POOL_MIN_SIZE
app.config.DB_POOL_MAX_SIZE = SERVER_DB_POOL_MAX_SIZE

app.config.DB_USE_CONNECTION_FOR_REQUEST = False

Compress(app)  # must be before all response middleware
db = Gino(app)

jinja = SanicJinja2(app, pkg_name='core')


@app.listener('after_server_start')
async def setup_db(app, loop):
    pass


@app.listener('before_server_stop')
async def setup_db(app, loop):
    await asyncio.sleep(5)

@app.middleware('request')
async def halt_request(request: Request):
    if len(request.path) > 1:
        if request.path[-1] == '/':
            return redirect(
                urlunparse(
                    ('', '', request.path[:-1], None, request.query_string, None)
                ),
                status=301
            )
