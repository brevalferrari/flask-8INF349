# -*- coding: utf-8 -*-

from os import remove as rm

from flaskstarter import create_app
from flaskstarter.extensions import db
from flaskstarter.config import DefaultConfig
from flaskstarter.model.model import Product, ShippingInformation, ProductOrderQuantity, CreditCardDetails, Transaction, Order

application = create_app()


@application.cli.command("initdb")
def initdb(config=DefaultConfig()):
    """Init/reset database."""
    db.close()
    try:
        rm(config.DATABASE_URI)
    except FileNotFoundError:
        pass
    db.connect()
    db.create_tables([Product, ShippingInformation, ProductOrderQuantity, CreditCardDetails, Transaction, Order])

    # préparation de la base
