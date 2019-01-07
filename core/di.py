from gino.ext.sanic import Gino
from sanic import Sanic
from sanic_compress import Compress
from sanic_jinja2 import SanicJinja2

from core.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

app = Sanic()
app.config.DB_HOST = DB_HOST
app.config.DB_DATABASE = DB_NAME
app.config.DB_USER = DB_USER
app.config.DB_PASSWORD = DB_PASSWORD
db = Gino(app)

Compress(app)
jinja = SanicJinja2(app, pkg_name='core')
