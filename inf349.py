# -*- coding: utf-8 -*-

from os import remove as rm

from appli import create_app
from appli.extensions import db
from appli.config import DefaultConfig
from appli.model.model import Product, ShippingInformation, ProductOrderQuantity, CreditCardDetails, Transaction, Order

application = create_app()


@application.cli.command("init-db")
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
