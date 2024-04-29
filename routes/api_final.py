from flask import Blueprint, jsonify, request, url_for
from db import db
from models import Customer

from models import Product

api_final_bp = Blueprint("final", __name__)


# GET JSON of customers with 0 or negative balance
@api_final_bp.route("customers-warning", methods=["GET"])
def customers_warning():
    # select all customers
    customers = Customer.query.all()
    # convert customer objects to JSON where balance >= 0
    customers_json_return = [customer.to_json() for customer in customers if customer.balance <= 0]
    returnobj = []
    # create new return object with required attributes
    for customer in customers_json_return:
        returnobj.append({
            "name": customer["name"],
            "balance": customer["balance"],
            "url": url_for('api_customers.customer_detail_json', customer_id=customer["id"])
        })
    return jsonify(returnobj)


# GET all products where stock <= 0
@api_final_bp.route("out-of-stock", methods=["GET"])
def out_of_stock():
    # select all products
    products = Product.query.all()
    # convert all product objects to JSON where quantity_available <= 0
    products_json_return = [product.to_json() for product in products if product.quantity_available <= 0]
    returnobj = []
    # append to returnobj
    for product in products_json_return:
        returnobj.append(product["name"])
    return jsonify(returnobj)
