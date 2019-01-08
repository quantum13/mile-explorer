from sanic import Sanic
from sanic.response import redirect

from core import config
from core.logging import setup_logging


def redirect_to_ssl(request):
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, status=301)


def start():


    app = Sanic(configure_logging=False)
    app.request_middleware.append(redirect_to_ssl)

    app.config.REQUEST_MAX_SIZE = 4000
    app.config.REQUEST_TIMEOUT = 5
    app.config.RESPONSE_TIMEOUT = 5

    config.LOG_TELEGRAM_APP_NAME = 'proxy'

    setup_logging('sanic.root', replace=True)
    setup_logging('sanic.error', replace=True)

    app.run(host='0.0.0.0', workers=1, port=8081, debug=False, access_log=False)




