# -*- coding: utf-8 -*-
from types import NoneType
import pytest
from flask import Response
from json import dumps as serialize_json

from flaskstarter import create_app
from flaskstarter.utils.json import Json
from encodings.utf_8 import decode


@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True
    app.testing = True

    client = app.test_client()
    yield client


def dict_pretty_print(d: dict) -> str:
    return serialize_json(d, sort_keys=True, indent=4)


def test_liste_produits(client):
    attendu = {"products": list}
    attendu_product = {
        "name": str,
        "id": int,
        "in_stock": bool,
        "description": str,
        "price": float,
        "weight": int,
        "image": str,
    }
    data: dict = client.get("/").get_json()
    assert Json(data).is_like(attendu), "invalid product list schema"
    assert Json(data["products"][0]).is_like(attendu_product), "invalid product schema"


# Test création de commande (POST /order)
def test_create_order(client):
    product_data = {"product": {"id": 1, "quantity": 2}}
    response = client.post("/order", json=product_data)

    assert response.status_code == 302
    location = response.headers.get("Location")
    assert location is not None


# Test récupération d'une commande existante (GET /order/<id>)
def test_get_order(client):
    # Création d'une commande
    order_response = client.post("/order", json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    response = client.get(f"/order/{order_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert Json(data).is_like(
        {
            "order": {
                "id": int,
                "total_price": float,
                "total_price_tax": NoneType,
                "email": NoneType,
                "credit_card": dict,
                "shipping_information": dict,
                "paid": bool,
                "transaction": dict,
                "product": {"id": int, "quantity": int},
                "shipping_price": float,
            }
        }
    ), "shema validation failed, got inner types " + dict_pretty_print(
        {k: str(type(v)) for k, v in data["order"].items()}
    )
    data = data["order"]
    assert (
        data["credit_card"] == data["shipping_information"] == data["transaction"] == {}
    ), "optional data not empty"
    assert data["paid"] == False, "the order isn't paid yet!"
    assert data["id"] == int(order_id), "wrong order id"


# Test mise à jour d'une commande avec adresse et email (PUT /order/<id>)
def test_update_order_shipping_info(client):
    order_response = client.post("/order", json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    update_data = {
        "order": {
            "email": "jgnault@uqac.ca",
            "shipping_information": {
                "country": "Canada",
                "address": "201, rue Président-Kennedy",
                "postal_code": "G7X 3Y7",
                "city": "Chicoutimi",
                "province": "QC",
            },
        }
    }
    response = client.put(f"/order/{order_id}", json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["order"]["shipping_information"] == {
        "country": "Canada",
        "address": "201, rue Président-Kennedy",
        "postal_code": "G7X 3Y7",
        "city": "Chicoutimi",
        "province": "QC",
    }, "wrong shipping info"
    assert data["order"]["email"] == "jgnault@uqac.ca"


# Test paiement réussi (PUT /order/<id>)
def test_payment_success(client):
    order_response = client.post("/order", json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    client.put(
        f"/order/{order_id}",
        json={
            "order": {
                "email": "jgnault@uqac.ca",
                "shipping_information": {
                    "country": "Canada",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "city": "Chicoutimi",
                    "province": "QC",
                },
            }
        },
    )

    payment_data = {
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9,
        }
    }
    response = client.put(f"/order/{order_id}", json=payment_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["order"]["paid"] is True
    assert data["order"]["credit_card"] == {
       "name" : "John Doe",
       "first_digits" : "4242",
       "last_digits": "4242",
       "expiration_year" : 2025,
       "expiration_month" : 9
    }, "wrong credit card info"



# Test carte refusée (PUT /order/<id>)
def test_payment_declined(client):
    order_response = client.post("/order", json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    client.put(
        f"/order/{order_id}",
        json={
            "order": {
                "email": "jgnault@uqac.ca",
                "shipping_information": {
                    "country": "Canada",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "city": "Chicoutimi",
                    "province": "QC",
                },
            }
        },
    )

    payment_data = {
        "credit_card": {
            "name": "John Doe",
            "number": "4000 0000 0000 0002",  # Carte refusée
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9,
        }
    }
    response = client.put(f"/order/{order_id}", json=payment_data)
    assert response.status_code == 422
    data = response.get_json()
    assert data["credit_card"]["code"] == "card-declined"


def test_Commande_Sans_Produit(client):
    # Envoi d'une requête vide (erreur attendue)
    response = client.post("/order", json={})

    # Vérification du code de statut et du message d'erreur attendu
    assert (
        response.status_code == 422
    ), "L'API devrait retourner une erreur 422 si 'product' est manquant"
    assert response.json == {
        "errors": {
            "product": {
                "code": "missing-fields",
                "name": "La création d'une commande nécessite un produit",
            }
        }
    }, "Le message d'erreur retourné est incorrect"


def test_Commande_Produit_Hors_Stock(client):
    response = client.post("/order", json={"product": {"id": 4, "quantity": 1}})

    # Vérification du code de statut et du message d'erreur attendu
    assert (
        response.status_code == 422
    ), "L'API devrait retourner une erreur 422 si le produit n'est pas en stock"
    assert response.json == {
        "errors": {
            "product": {
                "code": "out-of-inventory",
                "name": "Le produit demandé n'est pas en inventaire",
            }
        }
    }, "Le message d'erreur retourné est incorrect"
