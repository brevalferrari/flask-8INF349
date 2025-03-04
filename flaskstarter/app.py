# -*- coding: utf-8 -*-

from flaskstarter.model.model import add_product, drop_products
from flaskstarter.model.flat import FlatProduct
from flaskstarter.routes.api import api
from flaskstarter.services.external.productapi import fetch_products
from flaskstarter.extensions import db


# For import *
__all__ = ["create_app"]


def create_app(config=None):
    try:
        db.connect()
        with db.manual_commit() as _:
            db.begin()
            drop_products()
            db.commit()
        with db.manual_commit() as _:
            db.begin()
            for p in fetch_products():
                add_product(
                    FlatProduct(
                        id=p["id"],
                        name=p["name"],
                        price=p["price"],
                        image=p["image"],
                        in_stock=p["in_stock"],
                        description=p["description"],
                        weight=p["weight"],
                    )
                )
            db.commit()
    except:
        pass
    return api
