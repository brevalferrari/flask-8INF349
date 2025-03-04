from flask import Flask, request, Response
from flaskstarter.model.model import (
    add_order,
    get_products,
    get_order as _get_order,
    put_order_credit_card,
    put_order_shipping_information,
    get_product,
)
from flaskstarter.model.flat import (
    FlatOrder,
    FlatProductOrderQuantity,
    FlatCreditCardDetails,
    FlatShippingInformation,
)
import flaskstarter.routes.json_schemas as json_schemas
from flaskstarter.utils.json import Json, serialize_order


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


class ErrorCode:
    "API error codes."
    MISSING_FIELDS = "missing-fields"
    OUT_OF_INVENTORY = "out-of-inventory"
    ALREADY_PAID = "already-paid"
    CARD_DECLINED = "card-declined"


def product_error(message: str, code: str) -> Response:
    return {
        "errors": {
            "product": {
                "code": code,
                "name": message,
            }
        }
    }, 422


def order_error(message: str, code: str) -> Response:
    return {
        "errors": {
            "order": {
                "code": code,
                "name": message,
            }
        }
    }, 422


def credit_card_error(message: str, code: str) -> Response:
    return {
        "credit_card": {
            "code": code,
            "name": message,
        }
    }, 422


api = Flask(__name__)


@api.get("/")
def list_products() -> Response:
    """
    Cette URL doit retourner la liste complète des produits en format JSON
    disponibles pour passer une commande, incluant ceux qui ne sont pas en
    inventaire.
    """
    return {"products": get_products()}


@api.post("/order")
def new_order() -> Response:
    """
    La création d'une nouvelle commande se fait avec un appel POST à /order. Si la
    commande est créée, le code HTTP de retour doit être 302 et inclure le lien vers
    la commande nouvellement créée.
    """
    json = request.get_json()
    if not Json(json).is_like(json_schemas.new_order):
        return product_error(
            "La création d'une commande nécessite un produit", ErrorCode.MISSING_FIELDS
        )
    elif json["product"]["quantity"] < 1:
        return product_error(
            "La quantité du produit ne peut pas être inférieure à 1",
            ErrorCode.MISSING_FIELDS,
        )
    else:
        order = add_order(
            FlatOrder(
                products=FlatProductOrderQuantity(
                    product=get_product(json["product"]["id"]),
                    quantity=json["product"]["quantity"],
                )
            )
        )
        if not order.products.product.in_stock:
            return product_error(
                "Le produit demandé n'est pas en inventaire", ErrorCode.OUT_OF_INVENTORY
            )
        return response_with_headers(
            None,
            status=302,
            Location=f"/order/{order.id}",
        )


@api.get("/order/<int:order_id>")
def get_order(order_id: int) -> Response:
    """
    Une fois le processus d'achat initialisé, on peut récupérer la commande complète
    à tout moment avec cette requête GET.
    """
    return serialize_order(_get_order(order_id))


def add_credit_card(order_id: int, json: dict) -> Response:
    """Handles a PUT request on /order where the provided form data is supposed to be credit card details.

    Args:
        order_id (int): Order ID.
        json (dict): Form data.

    Returns:
        Response: Flask HTTP Response with json data.
    """
    if not Json(json).is_like(json_schemas.put_order_credit_card):
        return order_error(
            "Il manque un ou plusieurs champs qui sont obligatoires",
            ErrorCode.MISSING_FIELDS,
        )
    else:
        order = _get_order(order_id)
        cc = json["credit_card"]
        if order.shipping_information is None:
            return order_error(
                "Les informations du client sont nécessaire avant d'appliquer une carte de crédit",
                ErrorCode.MISSING_FIELDS,
            )
        if order.transaction and order.paid:
            return order_error("La commande a déjà été payée.", ErrorCode.ALREADY_PAID)
        result: FlatOrder = put_order_credit_card(
            order_id,
            FlatCreditCardDetails(
                name=cc["name"],
                number=int("".join([n for n in cc["number"] if n != " "])),
                expiration_year=int(cc["expiration_year"]),
                cvv=int(cc["cvv"]),
                expiration_month=int(cc["expiration_month"]),
            ),
        )
        if not result.transaction.success:
            return credit_card_error(
                "La carte de crédit a été déclinée.", ErrorCode.CARD_DECLINED
            )
        return serialize_order(result)


def add_shipping_information(order_id: int, json: dict) -> Response:
    """Handles a PUT request on /order where the provided form data is supposed to be credit card details.

    Args:
        order_id (int): Order ID.
        json (dict): Form data.

    Returns:
        Response: Flask HTTP Response with json data.
    """
    if not Json(json).is_like(json_schemas.put_order_shipping_info):
        return order_error(
            "Il manque un ou plusieurs champs qui sont obligatoires",
            ErrorCode.MISSING_FIELDS,
        )
    else:
        o = json["order"]
        s = o["shipping_information"]
        return serialize_order(
            put_order_shipping_information(
                order_id,
                o["email"],
                FlatShippingInformation(
                    country=s["country"],
                    address=s["address"],
                    postal_code=s["postal_code"],
                    city=s["city"],
                    province=s["province"],
                ),
            )
        )


@api.put("/order/<int:order_id>")
def put_order(order_id: int) -> Response:
    """
    Par défaut, une commande ne contient aucune information sur le client. On doit
    fournir le courriel et l'adresse d'expédition du client.
    """
    json: dict = request.get_json()
    if list(json.keys())[0] == "credit_card":
        return add_credit_card(order_id, json)
    else:
        return add_shipping_information(order_id, json)
