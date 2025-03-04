from urllib.request import urlopen as open
from json import loads as parse_json


def fetch_products() -> list[dict]:
    return parse_json(
        open("https://dimensweb.uqac.ca/~jgnault/shops/products/").read().decode("utf8")
    )["products"]
