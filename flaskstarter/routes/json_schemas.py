"""
JSON schemas to validate sent form data.
"""

new_order = {
    "type": "object",
    "properties": {"id": {"type": "number"}, "quantity": {"type": "number"}},
}

put_order_shipping_info = {
    "type": "object",
    "properties": {
        "order": {
            "email": {"type": "string"},
            "shipping_information": {
                "country": {"type": "string"},
                "address": {"type": "string"},
                "postal_code": {"type": "string"},
            },
        }
    },
}

put_order_credit_card = {
    "type": "object",
    "properties": {
        "credit_card": {
            "name": {"type": "string"},
            "number": {"type": "string"},
            "expiration_year": {"type": "number"},
            "cvv": {"type": "string"},
            "expiration_month": {"type": "number"},
        }
    },
}
