# TODO: this is only a static api

from flask import Blueprint, request, Response
import json_schemas
from jsonschema import validate, ValidationError


def response_with_headers(body, status=200, **headers) -> Response:
    """Generate a response with the specified headers.

    Args:
        body (any): Response body.
        status (int, optional): HTTP status code. Defaults to 200.

    Returns:
        Response: Complete response with the provided headers.
    """
    response = Response(body, status=status)
    for k, val in headers.items():
        response.headers[k] = val
    return response


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


@api.get("/order/<int:order_id>")
def get_order(order_id: int) -> Response:
    """
    Une fois le processus d'achat initialisé, on peut récupérer la commande complète
    à tout moment avec cette requête GET.
    """
    return {
        "order": {
            "id": order_id,
            "total_price": 9148,
            "total_price_tax": 10520.20,
            "email": None,
            "credit_card": {},
            "shipping_information": {},
            "paid": None,
            "transaction": {},
            "product": {"id": 123, "quantity": 1},
            "shipping_price": 1000,
        }
    }


def add_credit_card(order_id: int, json: dict) -> Response:
    """Handles a PUT request on /order where the provided form data is supposed to be credit card details.

    Args:
        order_id (int): Order ID.
        json (dict): Form data.

    Returns:
        Response: Flask HTTP Response with json data.
    """
    try:
        validate(json, json_schemas.put_order_credit_card)
        if (client_information := True) is None:  # TODO
            return {
                "errors": {
                    "order": {
                        "code": "missing-fields",
                        "name": "Les informations du client sont nécessaire avant d'appliquer une carte de crédit",
                    }
                }
            }, 422
        if already_paid := False:  # TODO
            return {
                "errors": {
                    "order": {
                        "code": "already-paid",
                        "name": "La commande a déjà été payée.",
                    }
                }
            }, 422
        if not (card_accepted := True):  # TODO
            return {
                "credit_card": {
                    "code": "card-declined",
                    "name": "La carte de crédit a été déclinée.",
                }
            }
        return {
            "order": {
                "shipping_information": {
                    "country": "Canada",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "city": "Chicoutimi",
                    "province": "QC",
                },
                "email": "jgnault@uqac.ca",
                "total_price": 9148,
                "total_price_tax": 10520.20,
                "paid": True,
                "product": {"id": 123, "quantity": 1},
                "credit_card": {
                    "name": "John Doe",
                    "first_digits": "4242",
                    "last_digits": "4242",
                    "expiration_year": 2024,
                    "expiration_month": 9,
                },
                "transaction": {
                    "id": "wgEQ4zAUdYqpr21rt8A10dDrKbfcLmqi",
                    "success": True,
                    "amount_charged": 10148,
                },
                "shipping_price": 1000,
                "id": order_id,
            }
        }
    except ValidationError:
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                }
            }
        }, 422


def add_shipping_information(order_id: int, json: dict) -> Response:
    """Handles a PUT request on /order where the provided form data is supposed to be credit card details.

    Args:
        order_id (int): Order ID.
        json (dict): Form data.

    Returns:
        Response: Flask HTTP Response with json data.
    """
    try:
        validate(json, json_schemas.put_order_shipping_info)
        return {
            "order": {
                "shipping_information": {
                    "country": "Canada",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "city": "Chicoutimi",
                    "province": "QC",
                },
                "credit_card": {},
                "email": "jgnault@uqac.ca",
                "total_price": 9148,
                "total_price_tax": 10520.20,
                "transaction": {},
                "paid": False,
                "product": {"id": 123, "quantity": 1},
                "shipping_price": 1000,
                "id": order_id,
            }
        }
    except ValidationError:
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                }
            }
        }, 422


@api.put("/order/<int:order_id>")
def put_order(order_id: int) -> Response:
    """
    Par défaut, une commande ne contient aucune information sur le client. On doit
    fournir le courriel et l'adresse d'expédition du client.
    """
    json: dict = request.get_json()
    if json.keys[0] is "credit_card":
        return add_credit_card(order_id, json)
    else:
        return add_shipping_information(order_id, json)
