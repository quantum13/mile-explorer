import asyncio

from gino.ext.sanic import Gino
from sanic import Sanic
from sanic_compress import Compress
from sanic_jinja2 import SanicJinja2

from core.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, SERVER_DB_POOL_MIN_SIZE, SERVER_DB_POOL_MAX_SIZE


app = Sanic(configure_logging=False)
app.config.DB_HOST = DB_HOST
app.config.DB_DATABASE = DB_NAME
app.config.DB_USER = DB_USER
app.config.DB_PASSWORD = DB_PASSWORD

app.config.DB_POOL_MIN_SIZE = SERVER_DB_POOL_MIN_SIZE
app.config.DB_POOL_MAX_SIZE = SERVER_DB_POOL_MAX_SIZE

db = Gino(app)

# Compress(app)
jinja = SanicJinja2(app, pkg_name='core')


@app.listener('after_server_start')
async def setup_db(app, loop):
    pass


@app.listener('before_server_stop')
async def setup_db(app, loop):
    await asyncio.sleep(5)
