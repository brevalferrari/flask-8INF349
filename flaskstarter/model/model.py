from random import randint
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
from flaskstarter.extensions import db
from flaskstarter.utils.json import serialize_order
from .flat import (
    FlatProduct,
    FlatShippingInformation,
    FlatProductOrderQuantity,
    FlatCreditCardDetails,
    FlatTransaction,
    FlatOrder,
)


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

    def flatten(self) -> FlatProduct:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatProduct(
            id=self.get_id(),
            name=str(self.name),
            in_stock=bool(self.in_stock),
            description=str(self.description),
            price=float(self.price),
            weight=self.weight and int(self.weight),
            image=str(self.image),
        )


class ShippingInformation(Model):
    country = CharField()
    address = CharField()
    postal_code = CharField()
    city = CharField()
    province = CharField(max_length=2)

    class Meta:
        database = db

    def flatten(self) -> FlatShippingInformation:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatShippingInformation(
            id=self.get_id(),
            country=str(self.country),
            address=str(self.address),
            postal_code=str(self.postal_code),
            city=str(self.city),
            province=str(self.province),
        )


class ProductOrderQuantity(Model):
    "Links a product to its quantity for an order."
    # TODO: uncomment line below and move class definition to have multiple products per order (next version)
    # oid = ForeignKeyField(Order, backref='products')
    pid = ForeignKeyField(Product, backref="order_quantities")
    quantity = IntegerField(constraints=[Check("quantity > 0")])

    class Meta:
        database = db

    def flatten(self) -> FlatProductOrderQuantity:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatProductOrderQuantity(
            id=self.get_id(), product=self.pid.flatten(), quantity=int(self.quantity)
        )


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

    def flatten(self) -> FlatCreditCardDetails:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatCreditCardDetails(
            id=self.get_id(),
            name=str(self.name),
            number=int(self.number),
            expiration_year=int(self.expiration_year),
            cvv=int(self.cvv),
            expiration_month=int(self.expiration_month),
        )


class Transaction(Model):
    id = CharField(max_length=32, primary_key=True)
    success = BooleanField()
    amount_charged = DecimalField(decimal_places=2)

    class Meta:
        database = db

    def flatten(self) -> FlatTransaction:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatTransaction(
            id=str(self.id),
            success=bool(self.success),
            amount_charged=float(self.amount_charged),
        )


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

    def flatten(self) -> FlatOrder:
        """Convert this object to a flat dataclass, cutting every link with the database."""
        return FlatOrder(
            id=self.get_id(),
            products=self.product.flatten(),
            email=self.email and str(self.email),
            credit_card=self.credit_card and self.credit_card.flatten(),
            shipping_information=self.shipping_information
            and self.shipping_information.flatten(),
            transaction=self.transaction and self.transaction.flatten(),
            paid=bool(self.paid),
        )


def get_product(product_id: int) -> FlatProduct:
    return Product.get_by_id(product_id).flatten()


def get_products() -> list[dict]:
    return list(map(lambda p: p.flatten(), Product.select()))


def add_product(product: FlatProduct):
    Product(
        name=product.name,
        in_stock=product.in_stock,
        description=product.description,
        price=product.price,
        weight=product.weight,
        image=product.image,
    ).save(force_insert=True)


def drop_products():
    Product.delete().execute()


def add_order(order: FlatOrder) -> FlatOrder:
    poq = ProductOrderQuantity(
        pid=Product.get(id=order.products.product.id), quantity=order.products.quantity
    )
    poq.save()
    new_order = Order(product=poq)
    new_order.save()
    return new_order.flatten()


class OrderNotFound(Exception):
    pass


def get_order(order_id: int) -> FlatOrder:
    order: Order | None = Order.get_or_none(order_id)
    if order is None:
        raise OrderNotFound()

    return order.flatten()


def put_order_shipping_information(
    order_id: int, email: str, shipping_information: FlatShippingInformation
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


def invalid_uuid_generator() -> str:
    """Invalid UUID generator

    Returns:
        str: A random UUID in the style of those from the products API.
    """
    result = ""
    for _i in range(32):
        match randint(0, 2):
            case 0:
                result += chr(randint(48, 57))
            case 1:
                result += chr(randint(65, 90))
            case 2:
                result += chr(randint(97, 122))
    return result


def put_order_credit_card(
    order_id: int, credit_card: FlatCreditCardDetails
) -> FlatOrder:
    order: Order | None = Order.get_or_none(order_id)
    if order is None:
        raise OrderNotFound()

    existing_credit_card: None | CreditCardDetails = order.credit_card
    with db.manual_commit() as _:
        db.begin()
        if existing_credit_card is None:  # card does not exist yet
            existing_credit_card = CreditCardDetails(
                name=credit_card.name,
                number=credit_card.number,
                expiration_year=credit_card.expiration_year,
                cvv=credit_card.cvv,
                expiration_month=credit_card.expiration_month,
            )
            existing_credit_card.save()
            order.credit_card = existing_credit_card
            order.save()
        else:  # card exists, update it
            existing_credit_card.name = credit_card.name
            existing_credit_card.number = credit_card.number
            existing_credit_card.expiration_year = credit_card.expiration_year
            existing_credit_card.cvv = credit_card.cvv
            existing_credit_card.expiration_month = credit_card.expiration_month
            existing_credit_card.save()
        db.commit()

    flat_order = order.flatten()
    order_dict = serialize_order(flat_order)
    charging_results = charge(
        credit_card.name,
        credit_card.number,
        credit_card.expiration_year,
        str(credit_card.cvv),
        credit_card.expiration_month,
        order_dict["order"]["total_price_tax"] + order_dict["order"]["shipping_price"],
    )
    transaction_dict = (
        charging_results["transaction"]
        if "transaction" in charging_results
        else {"id": invalid_uuid_generator(), "success": False, "amount_charged": 0.0}
    )
    with db.manual_commit() as _:
        db.begin()
        transaction = Transaction(
            id=transaction_dict["id"],
            success=transaction_dict["success"],
            amount_charged=transaction_dict["amount_charged"],
        )
        transaction.save(force_insert=True)
        order.transaction = transaction
        if transaction.success:
            order.paid = True
        order.save()
        db.commit()

    return order.flatten()
