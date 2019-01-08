import asyncio
import atexit

import aiohttp
import logging
import sys
import time

from core import config


class FormatterWithTime(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = time.strftime(self.default_time_format, ct)
        s = '%s.%03d' % (t, record.msecs)
        return s


class TelegramHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter(f"[%(name)s] %(message)s"))

    def emit(self, record):
        if asyncio.get_event_loop().is_closed():
            return
        try:
            asyncio.ensure_future(self.post(record))
        except Exception:
            self.handleError(record)

    async def post(self, record):
        async with aiohttp.ClientSession() as session:
            channel = config.LOG_TELEGRAM_CHANNELS.get(record.levelname, config.LOG_TELEGRAM_CHANNELS_DEFAULT)
            await session.post(
                f"https://api.telegram.org/bot{config.LOG_TELEGRAM_TOKEN}/sendMessage",
                data={
                    'chat_id': channel,
                    'parse_mode': 'Markdown',
                    'text': f"`{config.LOG_TELEGRAM_APP_NAME}` `{record.levelname[:3]}` " + self.format(record)
                },
            )


def setup_logging(logger_name, replace=False):
    logger = logging.getLogger(logger_name)
    logger.setLevel('INFO')

    if replace:
        for h in logger.handlers:
            logger.removeHandler(h)

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(FormatterWithTime('%(asctime)s [%(levelname)s] %(name)s %(message)s'))
    logger.addHandler(stdout_handler)

    logger.addHandler(TelegramHandler())

    return logger
