from appli.model.flat import FlatProduct, FlatOrder
from appli.utils.taxes import calculate_tax, calculate_shipping_price


class Json:
    _inner: dict

    def __init__(self, json: dict):
        self._inner = json

    def is_like(self, schema: dict) -> bool:
        """Check if a JSON object matches a JSON schema.

        Args:
            schema (dict): JSON validation schema (key: type or key: {key: type} etc).

        Returns:
            bool: Wether this is a valid JSON according to the provided schema or not.
        """
        for k, v in schema.items():
            if (k not in self._inner) or (
                (
                    (is_dict := isinstance(v, dict))
                    and not Json(self._inner[k]).is_like(v)
                )
                or (not is_dict and not isinstance(self._inner[k], v))
            ):
                return False
        return True


def serialize_product(product: FlatProduct) -> dict:
    return {
        "name": product.name,
        "id": product.id,
        "in_stock": product.in_stock,
        "description": product.description,
        "price": product.price,
        "weight": product.weight,
        "image": product.image,
    }


def serialize_order(order: FlatOrder) -> dict:
    total_price = order.products.product.price * order.products.quantity
    return {
        "order": {
            "id": order.id,
            "total_price": total_price,
            "total_price_tax": (
                None
                if order.shipping_information is None
                else calculate_tax(order.shipping_information.province) * total_price
                + total_price
            ),
            "email": order.email,
            "credit_card": (
                {}
                if order.credit_card is None
                else {
                    "name": order.credit_card.name,
                    "first_digits": str(order.credit_card.number)[:4],
                    "last_digits": str(order.credit_card.number)[-4:],
                    "expiration_year": int(order.credit_card.expiration_year),
                    "expiration_month": int(order.credit_card.expiration_month),
                }
            ),
            "shipping_information": (
                {}
                if order.shipping_information is None
                else {
                    "country": order.shipping_information.country,
                    "address": order.shipping_information.address,
                    "postal_code": order.shipping_information.postal_code,
                    "city": order.shipping_information.city,
                    "province": order.shipping_information.province,
                }
            ),
            "transaction": (
                {}
                if order.transaction is None
                else {
                    "id": order.transaction.id,
                    "success": order.transaction.success,
                    "amount_charged": order.transaction.amount_charged,
                }
            ),
            "paid": order.paid,
            "product": {
                "id": order.products.product.id,
                "quantity": order.products.quantity,
            },
            "shipping_price": (
                None
                if order.products.product.weight is None
                else calculate_shipping_price(
                    order.products.product.weight * order.products.quantity
                )
            ),
        }
    }
