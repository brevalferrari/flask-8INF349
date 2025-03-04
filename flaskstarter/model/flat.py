from dataclasses import dataclass

@dataclass
class FlatProduct:
    name: str
    price: float
    image: str
    id: int | None = None
    in_stock: bool = True
    description: str | None = None
    weight: int | None = None

@dataclass
class FlatShippingInformation:
    country: str
    address: str
    postal_code: str
    city: str
    province: str
    id: int | None = None

@dataclass
class FlatProductOrderQuantity:
    # oid: FlatOrder
    product: FlatProduct
    quantity: int
    id: int | None = None

@dataclass
class FlatCreditCardDetails:
    name: str
    number: int
    expiration_year: int
    cvv: int
    expiration_month: int
    id: int | None = None

@dataclass
class FlatTransaction:
    success: bool
    amount_charged: float
    id: str | None = None

@dataclass
class FlatOrder:
    products: FlatProductOrderQuantity
    id: int | None = None
    email: str | None = None
    credit_card: FlatCreditCardDetails | None = None
    shipping_information: FlatShippingInformation | None = None
    transaction: FlatTransaction | None = None
    paid: bool = False
