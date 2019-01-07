import logging
import sys
import time


class FormatterWithTime(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = time.strftime(self.default_time_format, ct)
        s = '%s.%03d' % (t, record.msecs)
        return s


def setup_logging(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel('INFO')

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(FormatterWithTime('%(asctime)s [%(levelname)s] %(name)s %(message)s'))
    logger.addHandler(stdout_handler)

    return logger
