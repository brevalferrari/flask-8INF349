# -*- coding: utf-8 -*-

from flaskstarter.routes.api import api


# For import *
__all__ = ["create_app"]


def create_app(config=None):
    # Create a Flask app

    return api
