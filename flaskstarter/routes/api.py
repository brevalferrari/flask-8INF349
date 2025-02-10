# TODO: this is only a static api

from flask import Blueprint, request, Response

import json_schemas
from utils import response_with_headers
from jsonschema import validate, ValidationError

api = Blueprint("api", __name__)


@api.get("/")
def list_products() -> Response:
    """
    Cette URL doit retourner la liste complète des produits en format JSON
    disponibles pour passer une commande, incluant ceux qui ne sont pas en
    inventaire.
    """
    return {
        "products": [
            {
                "name": "Brown eggs",
                "id": 1,
                "in_stock": True,
                "description": "Raw organic brown eggs in a basket",
                "price": 28.1,
                "weight": 400,
                "image": "0.jpg",
            },
            {
                "description": "Sweet fresh stawberry on the wooden table",
                "image": "1.jpg",
                "in_stock": True,
                "weight": 299,
                "id": 2,
                "name": "Sweet fresh stawberry",
                "price": 29.45,
            },
        ]
    }


@api.post("/order")
def new_order() -> Response:
    """
    La création d'une nouvelle commande se fait avec un appel POST à /order. Si la
    commande est créée, le code HTTP de retour doit être 302 et inclure le lien vers
    la commande nouvellement créée.
    """
    try:
        validate(request.get_json(), json_schemas.new_order)
        if out_of_inventory := False:  # TODO
            return {
                "errors": {
                    "product": {
                        "code": "out-of-inventory",
                        "name": "Le produit demandé n'est pas en inventaire",
                    }
                }
            }, 422
        return response_with_headers(
            {"product": {"id": 123, "quantity": 2}},
            status=302,
            Location="/order/<int:order_id>",
        )
    except ValidationError as e:
        return {"errors": {"product": {"code": "missing-fields", "name": e}}}, 422
