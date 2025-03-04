from flaskstarter.utils.json import Json
from flaskstarter.routes import json_schemas


def test_new_order_valid():
    assert Json({"product": {"id": 123, "quantity": 2}}).is_like(json_schemas.new_order)


def test_new_order_invalid():
    assert not Json({"product": {"id": "hello", "quantity": 2}}).is_like(
        json_schemas.new_order
    )


def test_new_order_missing_field():
    assert not Json({"product": {"id": 123}}).is_like(json_schemas.new_order)


def test_put_order_shipping_info_valid():
    assert Json(
        {
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
    ).is_like(json_schemas.put_order_shipping_info)


def test_put_order_shipping_info_invalid():
    assert not Json(
        {
            "order": {
                "email": "jgnault@uqac.ca",
                "shipping_information": {
                    "country": "Canada",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "city": None,
                    "province": "QC",
                },
            }
        }
    ).is_like(json_schemas.put_order_shipping_info)


def test_put_order_shipping_info_missing_field():
    assert not Json(
        {
            "order": {
                "email": "jgnault@uqac.ca",
                "shipping_information": {
                    "country": "Canada",
                    "postal_code": "G7X 3Y7",
                    "city": "Chicoutimi",
                    "province": "QC",
                },
            }
        }
    ).is_like(json_schemas.put_order_shipping_info)


def test_put_order_credit_card_valid():
    assert Json(
        {
            "credit_card": {
                "name": "John Doe",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9,
            }
        }
    ).is_like(json_schemas.put_order_credit_card)


def test_put_order_credit_card_invalid():
    assert not Json(
        {
            "credit_card": {
                "name": "John Doe",
                "number": {
                    "nested": "json",
                    "that": "has",
                    "nothing": "to do",
                    "here": 123,
                },
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9,
            }
        }
    ).is_like(json_schemas.put_order_credit_card)


def test_put_order_credit_card_missing_field():
    assert not Json(
        {
            "credit_card": {
                "name": "John Doe",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "expiration_month": 9,
            }
        }
    ).is_like(json_schemas.put_order_credit_card)
