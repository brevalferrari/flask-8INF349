class UnknownProvince(Exception):
    pass


def calculate_tax(province: str) -> float:
    """Calcule les taxes en fonction de la province.

    Args:
        province (str): Code de province (deux caractères).

    Raises:
        UnknownProvince: La province est inconnue au bataillon.

    Returns:
        float: Taxe
    """
    match province:
        case "QC":
            return 0.15
        case "ON":
            return 0.13
        case "AB":
            return 0.05
        case "BC":
            return 0.12
        case "NS":
            return 0.14
        case _:
            raise UnknownProvince()


def calculate_shipping_price(grams: int) -> float:
    """Calcule le prix total pour expédier la commande.

    Args:
        grams (int): Poids total de la commande en grammes.

    Returns:
        float: Prix d'expédition.
    """
    if grams < 0:
        return 0.0
    elif grams < 500:
        return 5.0
    elif grams < 2000:
        return 10.0
    else:
        return 25.0
