from urllib.request import Request, urlopen as open
from json import loads as parse_json, dumps as serialize


def charge(
    name: str,
    number: int,
    expiration_year: int,
    cvv: str,
    expiration_month: int,
    amount_charged: float,
) -> dict:
    req = Request("https://dimensweb.uqac.ca/~jgnault/shops/pay/")
    req.add_header("Content-Type", "application/json")
    json = {
        "credit_card": {
            "name": name,
            "number": " ".join(
                [str(number)[i : i + 4] for i in range(0, len(str(number)), 4)]
            ),
            "expiration_year": expiration_year,
            "cvv": cvv,
            "expiration_month": expiration_month,
        },
        "amount_charged": amount_charged,
    }
    return parse_json(open(req, str.encode(serialize(json))).read().decode("utf8"))
