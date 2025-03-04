"Flat versions of Model classes with their database link removed and foreign keys resolved."
from dataclasses import dataclass


@dataclass
class FlatProduct:
    "Flat version of Product (with no link to the database)."
    name: str
    price: float
    image: str
    id: int | None = None
    in_stock: bool = True
    description: str | None = None
    weight: int | None = None


@dataclass
class FlatShippingInformation:
    "Flat version of ShippingInformation (with no link to the database)."
    country: str
    address: str
    postal_code: str
    city: str
    province: str
    id: int | None = None


@dataclass
class FlatProductOrderQuantity:
    "Flat version of ProductOrderQuantity (with no link to the database)."
    # oid: FlatOrder
    product: FlatProduct
    quantity: int
    id: int | None = None


@dataclass
class FlatCreditCardDetails:
    "Flat version of CreditCardDetails (with no link to the database)."
    name: str
    number: int
    expiration_year: int
    cvv: int
    expiration_month: int
    id: int | None = None


@dataclass
class FlatTransaction:
    "Flat version of Transaction (with no link to the database)."
    success: bool
    amount_charged: float
    id: str | None = None


@dataclass
class FlatOrder:
    "Flat version of Order (with no link to the database)."
    products: FlatProductOrderQuantity
    id: int | None = None
    email: str | None = None
    credit_card: FlatCreditCardDetails | None = None
    shipping_information: FlatShippingInformation | None = None
    transaction: FlatTransaction | None = None
    paid: bool = False
