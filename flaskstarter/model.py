from peewee import (
    CharField,
    BooleanField,
    TextField,
    DecimalField,
    IntegerField,
    Model,
    Check,
    ForeignKeyField,
    UUIDField,
    BigIntegerField,
)

from .extensions import db


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


class ShippingInformation(Model):
    country = CharField()
    address = CharField()
    postal_code = CharField()
    city = CharField()
    province = CharField(max_length=2)
    class Meta:
        database = db


class ProductOrderQuantity(Model):
    # TODO: uncomment line below and move class definition to have multiple products per order (next version)
    # oid = ForeignKeyField(Order, backref='products')
    pid = ForeignKeyField(Product, backref="order_quantities")
    quantity = IntegerField(constraints=[Check("quantity > 0")])
    class Meta:
        database = db


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


class Transaction(Model):
    id = UUIDField(primary_key=True)
    success = BooleanField()
    amount_charged = BigIntegerField()
    class Meta:
        database = db


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

def serialize_products(product: Product)-> dict: 
    return {
        "name": product.name,
        "id": product.get_id(),
        "in_stock": bool(product.in_stock),
        "description": product.description,
        "price": product.price,
        "weight": product.weight,
        "image": product.image
    }

def get_products()-> list[dict]: 
    return map(serialize_products, Product.select())

def add_test_product(name: str, price: float, weight: int, image: str):
    Product(name=name, price=price, weight=weight, image=image).save()

def add_order(product_id: int, quantity: int):
    poq = ProductOrderQuantity(pid=Product.get(id=product_id), quantity=quantity)
    poq.save()
    Order(product=poq).save()


#Fonction get_order()
def get_order(order_id: int) -> dict:
    order = Order.get_or_none(Order.id == order_id)
    if order is None:
        return {"error": "Commande introuvable"}
    
    total_price = sum(
        poq.product.price * poq.quantity for poq in ProductOrderQuantity.select().where(ProductOrderQuantity.order == order)
    )
    
    return {
        "id": order.id,
        "total_price": total_price,
        "paid": order.paid
    }