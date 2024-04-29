from flask import Blueprint, jsonify, request
from db import db
from models import Customer

api_customers_bp = Blueprint("api_customers", __name__)


# reusable function to parse JSON data and required fields
def parse_json(data, *required_fields):
    for field in required_fields:
        if field not in data:
            return False, f"Invalid input. {field.capitalize()} is required"
    return True, None


# return all customers with GET
@api_customers_bp.route("/")
def customers_json():
    # select all customers
    customers = Customer.query.order_by(Customer.name).all()
    # convert customer objects to JSON
    customers_json_return = [customer.to_json() for customer in customers]
    return jsonify(customers_json_return)


# customer detail; shows contact info and orders
@api_customers_bp.route("<int:customer_id>")
def customer_detail_json(customer_id):
    # select customer record from db
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_json())


# create customer with POST
@api_customers_bp.route("/", methods=["POST"])
def customer_create():
    customer_json = request.json
    # name and phone are required fields
    success, error_message = parse_json(customer_json, "name", "phone")
    if not success:
        return error_message, 400

    # create Customer object
    customer = Customer(name=customer_json["name"], phone=customer_json["phone"])
    db.session.add(customer)
    db.session.commit()
    return "Created", 201


# update customer balance with PUT
@api_customers_bp.route("<int:customer_id>", methods=["PUT"])
def customer_update(customer_id):
    customer_json = request.json
    if "balance" not in customer_json:
        return "Invalid input, balance required", 400

    customer = Customer.query.get_or_404(customer_id)
    customer.balance = round(customer_json["balance"], 3)
    db.session.commit()
    return '', 204


# delete customer with DELETE
@api_customers_bp.route("<int:customer_id>", methods=["DELETE"])
def customer_delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return '', 204


