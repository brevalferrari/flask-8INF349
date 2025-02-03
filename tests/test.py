# -*- coding: utf-8 -*-

import pytest

from flask_login import current_user
from flaskstarter import create_app
from flaskstarter.extensions import db
from flaskstarter.user import Users, USER, ACTIVE


@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True
    app.testing = True

    client = app.test_client()
    yield client


def test_liste_produits(client):
    response: dict = client.get("/")
    attendu = {
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
    assert attendu == response.data, "test failed"

# Test des fonctions métiers (calcul prix livraison & carte de crédit)
def test_calculate_shipping_price():
    assert calculate_shipping_price(100) == 5
    assert calculate_shipping_price(600) == 10
    assert calculate_shipping_price(2500) == 25  

def test_is_card_accepted():
    assert is_card_accepted("4242 4242 4242 4242") == "valid"
    assert is_card_accepted("4000 0000 0000 0002") == "declined"
    assert is_card_accepted("1234 5678 9101 1121") is None


# Test récupération des produits (GET /)
def test_product(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert "products" in data
    assert len(data['products']) > 0  


# Test création de commande (POST /order)
def test_create_order(client):
    product_data = {"product": {"id": 1, "quantity": 2}}
    response = client.post('/order', json=product_data)
    
    assert response.status_code == 302
    location = response.headers.get('Location')
    assert location is not None


# Test récupération d'une commande existante (GET /order/<id>)
def test_get_order(client):
    # Création d'une commande
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    response = client.get(f"/order/{order_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert 'order' in data
    assert data['order']['id'] == int(order_id)


# Test mise à jour d'une commande avec adresse et email (PUT /order/<id>)
def test_update_order_shipping_info(client):
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    update_data = {
        "order": {
            "email": "jgnault@uqac.ca",
            "shipping_information": {
                "country": "Canada",
                "address": "201, rue Président-Kennedy",
                "postal_code": "G7X 3Y7",
                "city": "Chicoutimi",
                "province": "QC"
            }
        }
    }
    response = client.put(f'/order/{order_id}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['order']['email'] == "jgnault@uqac.ca"


# Test paiement réussi (PUT /order/<id>)
def test_payment_success(client):
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    client.put(f"/order/{order_id}", json={
        "order": {
            "email": "jgnault@uqac.ca",
            "shipping_information": {
                "country": "Canada",
                "address": "201, rue Président-Kennedy",
                "postal_code": "G7X 3Y7",
                "city": "Chicoutimi",
                "province": "QC"
            }
        }
    })

    payment_data = {
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "cvv": "123",
            "expiration_month": 9
        }
    }
    response = client.put(f'/order/{order_id}', json=payment_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['order']['paid'] is True


# Test carte refusée (PUT /order/<id>)
def test_payment_declined(client):
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 2}})
    order_id = order_response.headers["Location"].split("/")[-1]

    payment_data = {
        "credit_card": {
            "name": "John Doe",
            "number": "4000 0000 0000 0002",  # Carte refusée
            "expiration_year": 2024,
            "cvv": "123",
            "expiration_month": 9
        }
    }
    response = client.put(f'/order/{order_id}', json=payment_data)
    assert response.status_code == 422
    data = response.get_json()
    assert data["errors"]["credit_card"]["code"] == "card-declined"

def test_Nouvelle_Commande(client):
    response: dict = client.post("/order",
    attendu = {
        "product": { "id": 123, "quantity": 2 }
    })
    # assert attendu == response.data, "missing-fields"
    assert response.status_code == 302, "La commande devrait être créée avec un status 302"
    assert "Location" in response.headers, "La réponse doit contenir l'en-tête 'Location'"

def test_Commande_Sans_Produit(client):
    # Envoi d'une requête vide (erreur attendue)
    response = client.post("/order", json={})

    # Vérification du code de statut et du message d'erreur attendu
    assert response.status_code == 422, "L'API devrait retourner une erreur 422 si 'product' est manquant"
    assert response.json == {
        "errors": {
            "product": {
                "code": "missing-fields",
                "name": "La création d'une commande nécessite un produit"
            }
        }
    }, "Le message d'erreur retourné est incorrect"

def test_Commande_Produit_Hors_Stock(client):
    # Supposons que le produit 999 est hors stock
    response = client.post("/order", json={
        "product": { "id": 999, "quantity": 1 }
    })

    # Vérification du code de statut et du message d'erreur attendu
    assert response.status_code == 422, "L'API devrait retourner une erreur 422 si le produit n'est pas en stock"
    assert response.json == {
        "errors": {
            "product": {
                "code": "out-of-inventory",
                "name": "Le produit demandé n'est pas en inventaire"
            }
        }
    }, "Le message d'erreur retourné est incorrect"

