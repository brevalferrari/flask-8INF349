"""
JSON schemas to validate sent form data.
It's possible to say that some fields could have multiple types (like nullable types) by using Type1 | Type2.
"""

new_order = {"product": {"id": int, "quantity": int}}

put_order_shipping_info = {
    "order": {
        "email": str,
        "shipping_information": {
            "country": str,
            "address": str,
            "postal_code": str,
        },
    }
}

put_order_credit_card = {
    "credit_card": {
        "name": str,
        "number": str,
        "expiration_year": int,
        "cvv": str,
        "expiration_month": int,
    }
}
