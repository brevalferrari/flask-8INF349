# -*- coding: utf-8 -*-

from os import path


class BaseConfig(object):

    PROJECT_ROOT = path.abspath(path.dirname(path.dirname(__file__)))

    DEBUG = False
    TESTING = False


class DefaultConfig(BaseConfig):

    DEBUG = True

    # SQLITE for production
    DATABASE_URI = "badatase.db"

    # Flask-cache
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 60
