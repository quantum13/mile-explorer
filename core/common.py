import datetime
import os

import pytz


def require_env(key: str):
    assert os.getenv(key) is not None, f"Env {key} is not set"
    return os.getenv(key)


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=pytz.utc)
