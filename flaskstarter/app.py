# -*- coding: utf-8 -*-

from flaskstarter.model import add_product, drop_products
from flaskstarter.routes.api import api
from flaskstarter.services.external.productapi import fetch_products
from flaskstarter.extensions import db


# For import *
__all__ = ["create_app"]


def create_app(config=None):
    db.connect()
    with db.manual_commit() as _:
        db.begin()
        drop_products()
        db.commit()
    with db.manual_commit() as _:
        db.begin()
        for p in fetch_products():
            add_product(id=p["id"], name=p["name"], in_stock=p["in_stock"], description=p["description"], price=p["price"], weight=p["weight"], image=p["image"])
        db.commit()
    return api
