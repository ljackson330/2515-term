from sqlalchemy import Boolean, Float, Numeric, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from datetime import datetime

from db import db


class Customer(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), nullable=False, unique=True)
    phone = mapped_column(String(20), nullable=False)
    balance = mapped_column(Float, nullable=False, default=0)
    orders = relationship("Order")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "balance": round(self.balance, 2)
        }


class Category(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), nullable=False, unique=True)
    description = mapped_column(String(200))
    products = relationship("Product")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Product(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), nullable=False, unique=True)
    price = mapped_column(Float, nullable=False)
    quantity_available = mapped_column(Integer, nullable=False, default=0)
    category_id = mapped_column(Integer, ForeignKey(Category.id))
    category = relationship("Category", back_populates="products")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity_available": self.quantity_available
        }


class Order(db.Model):
    id = mapped_column(Integer, primary_key=True, nullable=False)
    customer_id = mapped_column(Integer, ForeignKey(Customer.id), nullable=False)
    customer = relationship("Customer", back_populates="orders")
    items = relationship("ProductOrder", back_populates="order", cascade="all, delete-orphan")
    created = mapped_column(DateTime, nullable=False, default=datetime.now)
    processed = mapped_column(DateTime, nullable=True)

    @property
    def total(self):
        return round(sum(item.product.price * item.quantity for item in self.items), 2)

    def process(self, strategy="adjust"):
        if self.processed:
            return False, "Order already processed"

        if self.customer.balance <= 0:
            return False, "Insufficient balance"

        for item in self.items:
            if item.quantity > item.product.quantity_available:
                if strategy == "reject":
                    return False, f"Insufficient quantity_available for item {item.product.name}"
                elif strategy == "ignore":
                    item.quantity = 0
                else:
                    item.quantity = item.product.quantity_available

            item.product.quantity_available -= item.quantity

        order_price = self.total
        self.customer.balance -= order_price
        self.processed = datetime.now()

        db.session.commit()
        return True, None


class ProductOrder(db.Model):
    id = mapped_column(Integer, primary_key=True, nullable=False)
    order_id = mapped_column(Integer, ForeignKey(Order.id), nullable=False)
    product_id = mapped_column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = mapped_column(Integer, nullable=False)
    product = relationship("Product")
    order = relationship("Order", back_populates="items")  # Back-populate from Order class


