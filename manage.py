from sqlalchemy import select, Null

from db import db
from models import Customer, Product, Order, ProductOrder, Category
from main import flaskapp as app
from sqlalchemy.sql import functions as func
import sqlalchemy
import random
import csv


def create_random_order():
    # select a random customer
    customer = db.session.query(Customer).order_by(func.random()).first()
    # create an order for the selected customer
    order = Order(customer=customer)
    db.session.add(order)

    # add random products to the order
    for _ in range(2):
        product = db.session.query(Product).order_by(func.random()).first()
        rand_qty = random.randint(10, 20)
        association = ProductOrder(order=order, product=product, quantity=rand_qty)
        db.session.add(association)

    db.session.commit()


# seed database from data/customers.csv and data/product_categories.csv
def seed_database():
    with app.app_context():
        # create database tables if they don't exist
        db.create_all()

        # seed products with categories from CSV
        with open('data/product_categories.csv', "r") as file:
            csv_reader = csv.reader(file, delimiter=',')
            # skip header
            next(csv_reader)
            for row in csv_reader:
                cat_exists = Category.query.filter_by(name=row[2]).first()
                if not cat_exists:
                    obj = Category(name=row[2])
                    db.session.add(obj)

        db.session.commit()
        with open('data/product_categories.csv', "r") as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                prod_exists = Product.query.filter_by(name=row[0]).first()
                if not prod_exists:
                    cat = Category.query.filter_by(name=row[2]).first()
                    obj = Product(name=row[0], price=row[1], quantity_available=random.randint(0, 50), category=cat)
                    db.session.add(obj)
        db.session.commit()

        # seed customers from CSV
        with open('data/customers.csv', "r") as file:
            csv_reader = csv.reader(file, delimiter=',')
            # skip header
            next(csv_reader)
            for row in csv_reader:
                # ensure the control Example customers have balance so we can process their orders
                balance = 150 if row[0].startswith('Example') else random.randint(0, 1) * random.randint(0, 150)
                obj = Customer(name=row[0], phone=row[1], balance=balance)
                db.session.add(obj)
        db.session.commit()


if __name__ == "__main__":
    seed_database()
