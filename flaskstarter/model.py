from dataclasses import dataclass
from peewee import (
    CharField,
    BooleanField,
    TextField,
    DecimalField,
    IntegerField,
    Model,
    Check,
    ForeignKeyField,
)

from flaskstarter.services.external.chargingapi import charge
from .extensions import db
from .utils.json import serialize_order

@dataclass
class FlatProduct:
    id: int | None = None
    name: str
    in_stock: bool = True
    description: str | None = None
    price: float
    weight: int | None = None
    image: str

class Product(Model):
    name = CharField()
    in_stock = BooleanField(default=True)
    description = TextField(null=True)
    price = DecimalField(
        max_digits=5, decimal_places=2, constraints=[Check("price > 0")]
    )
    weight = IntegerField(null=True, constraints=[Check("weight > 0")])
    image = CharField()

    class Meta:
        database = db
    
    def flatten(self)-> FlatProduct:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatProduct(id=self.get_id(), name=self.name, in_stock=self.in_stock, description=self.description, price=self.price, weight=self.weight, image=self.image)

@dataclass
class FlatShippingInformation:
    id: int | None = None
    country: str
    address: str
    postal_code: str
    city: str
    province: str

class ShippingInformation(Model):
    country = CharField()
    address = CharField()
    postal_code = CharField()
    city = CharField()
    province = CharField(max_length=2)

    class Meta:
        database = db

    def flatten(self)-> FlatShippingInformation:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatShippingInformation(id=self.get_id(), country=self.country, address=self.address, postal_code=self.postal_code, city=self.city, province=self.province)

@dataclass
class FlatProductOrderQuantity:
    id: int | None = None
    # oid: FlatOrder
    product: FlatProduct
    quantity: int

class ProductOrderQuantity(Model):
    # TODO: uncomment line below and move class definition to have multiple products per order (next version)
    # oid = ForeignKeyField(Order, backref='products')
    pid = ForeignKeyField(Product, backref="order_quantities")
    quantity = IntegerField(constraints=[Check("quantity > 0")])

    class Meta:
        database = db
    
    def flatten(self)-> FlatProductOrderQuantity:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatProductOrderQuantity(id=self.get_id(), product=self.pid.flatten(), quantity=self.quantity)


@dataclass
class FlatCreditCardDetails:
    id: int | None = None
    name: str
    number: int
    expiration_year: int
    cvv: int
    expiration_month: int

class CreditCardDetails(Model):
    name = CharField()
    number = DecimalField(max_digits=16, decimal_places=0)
    expiration_year = DecimalField(max_digits=4, decimal_places=0)
    cvv = DecimalField(max_digits=3, decimal_places=0)
    expiration_month = DecimalField(
        max_digits=2,
        decimal_places=0,
        constraints=[Check("expiration_month < 13"), Check("expiration_month > 0")],
    )

    class Meta:
        database = db

    def flatten(self)-> FlatCreditCardDetails:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatCreditCardDetails(id=self.get_id(), name=self.name, number=self.number, expiration_year=self.expiration_year, cvv=self.cvv, expiration_month=self.expiration_month)

@dataclass
class FlatTransaction:
    id: int | None = None
    success: bool
    amount_charged: float

class Transaction(Model):
    id = CharField(max_length=32, primary_key=True)
    success = BooleanField()
    amount_charged = DecimalField(decimal_places=2)

    class Meta:
        database = db
    
    def flatten(self)-> FlatTransaction:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatTransaction(id=self.id, success=self.success, amount_charged=self.amount_charged)

@dataclass
class FlatOrder:
    id: int | None = None
    products: FlatProductOrderQuantity
    email: str | None = None
    credit_card: FlatCreditCardDetails | None = None
    shipping_information: FlatShippingInformation | None = None
    transaction: FlatTransaction | None = None
    paid: bool = False

class Order(Model):
    product = ForeignKeyField(ProductOrderQuantity)
    email = CharField(null=True)
    credit_card = ForeignKeyField(CreditCardDetails, null=True)
    shipping_information = ForeignKeyField(
        ShippingInformation, backref="orders_shipped_there", null=True
    )
    transaction = ForeignKeyField(Transaction, null=True)
    paid = BooleanField(default=False)

    class Meta:
        database = db

    def flatten(self)-> FlatOrder:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatOrder(id=self.get_id(), product=self.product, email=self.email, credit_card=self.credit_card.flatten(), shipping_information=self.shipping_information.flatten(), transaction=self.transaction.flatten(), paid=self.paid)

def get_product(product_id: int)-> FlatProduct:
    return Product.get_by_id(product_id).flatten()

def get_products() -> list[dict]:
    return list(map(lambda p: p.flatten(), Product.select()))


def add_product(product: FlatProduct):
    product.save(force_insert=True)


def drop_products():
    Product.delete().execute()


def add_order(order: FlatOrder) -> FlatOrder:
    poq = ProductOrderQuantity(pid=Product.get(id=order.products.product.id), quantity=order.products.quantity)
    poq.save()
    order = Order(product=poq)
    order.save()
    return order.flatten()


class OrderNotFound(Exception):
    pass


def get_order(order_id: int) -> FlatOrder:
    order: Order | None = Order.get_or_none(order_id)
    if order is None:
        raise OrderNotFound()

    return order.flatten()


def put_order_shipping_information(
    order_id: int,
    email: str,
    shipping_information: FlatShippingInformation
) -> FlatOrder:
    order: Order | None = Order.get_or_none(order_id)
    if order is None:
        raise OrderNotFound()

    si = order.shipping_information
    if si is None:  # no shipping information yet, create it
        si = ShippingInformation(
            country=shipping_information.country,
            address=shipping_information.address,
            postal_code=shipping_information.postal_code,
            city=shipping_information.city,
            province=shipping_information.province,
        )
        si.save()
        order.shipping_information = si
        order.email = email
        order.save()
    else:  # shipping information exists, update it
        si.country = shipping_information.country
        si.address = shipping_information.address
        si.postal_code = shipping_information.postal_code
        si.city = shipping_information.city
        si.province = shipping_information.province
        si.save()
        order.email = email
        order.save()

    return get_order(order_id)


def put_order_credit_card(
    order_id: int,
    credit_card: FlatCreditCardDetails
) -> FlatOrder:
    order: Order | None = Order.get_or_none(order_id)
    if order is None:
        raise OrderNotFound()

    credit_card: None | CreditCardDetails = order.credit_card
    with db.manual_commit() as _:
        db.begin()
        if credit_card is None:  # card does not exist yet
            credit_card = CreditCardDetails(
                name=credit_card.name,
                number=credit_card.number,
                expiration_year=credit_card.expiration_year,
                cvv=credit_card.cvv,
                expiration_month=credit_card.expiration_month,
            )
            credit_card.save()
            order.credit_card = credit_card
            order.save()
        else:  # card exists, update it
            credit_card.name = credit_card.name
            credit_card.number = credit_card.number
            credit_card.expiration_year = credit_card.expiration_year
            credit_card.cvv = credit_card.cvv
            credit_card.expiration_month = credit_card.expiration_month
            credit_card.save()
        db.commit()

    flat_order = get_order(order_id).flatten()
    order_dict = serialize_order(flat_order)
    transaction_dict = charge(
        credit_card.name,
        credit_card.number,
        credit_card.expiration_year,
        credit_card.cvv,
        credit_card.expiration_month,
        order_dict["order"]["total_price_tax"] + order_dict["order"]["shipping_price"],
    )["transaction"]
    with db.manual_commit() as _:
        db.begin()
        transaction = Transaction(
            id=transaction_dict["id"],
            success=transaction_dict["success"],
            amount_charged=transaction_dict["amount_charged"],
        )
        transaction.save(force_insert=True)
        order.transaction = transaction
        order.save()
        db.commit()

    return flat_order
