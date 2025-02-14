# -*- coding: utf-8 -*-

from flask import Flask


# For import *
__all__ = ["create_app"]


def create_app(config=None):
    # Create a Flask app

    app = Flask(__name__)

    return app
