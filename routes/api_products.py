from flask import Blueprint, jsonify, request
from db import db
from models import Product, Category

api_products_bp = Blueprint("api_products", __name__)


# function to parse JSON and handle required fields
def parse_json(data, *required_fields):
    for field in required_fields:
        if field not in data:
            return False, f"Invalid input. {field.capitalize()} is required"
    return True, None


# return all products with GET
@api_products_bp.route("/")
def products_json():
    products = Product.query.order_by(Product.name).all()
    return jsonify([product.to_json() for product in products])


# create a product with POST
@api_products_bp.route("/", methods=["POST"])
def product_create():
    success, error_message = parse_json(request.json, "name", "price")
    if not success:
        return error_message, 400

    price = request.json.get("price")
    if not isinstance(price, (int, float)) or price <= 0:
        return "Price must be a positive integer or float", 400

    product = Product(name=request.json["name"],
                      price=request.json["price"],
                      quantity_available=request.json.get("quantity_available"))
    db.session.add(product)
    db.session.commit()
    return "created", 201


# update product price or quantity with PUT
@api_products_bp.route("<int:product_id>", methods=["PUT"])
def product_update(product_id):
    product_json = request.json
    db_product = Product.query.get_or_404(product_id)

    # name and/or price are required fields
    if "name" not in product_json and "price" not in product_json:
        return "Invalid input. Either 'name' or 'price' is required", 400

    # price must be a positive int or float if provided
    if "price" in product_json:
        price = product_json["price"]
        if not isinstance(price, (int, float)) or price <= 0:
            return "Price must be a positive integer or float", 400

    # update db record
    db_product.name = product_json.get('name', db_product.name)
    db_product.price = product_json.get('price', db_product.price)
    db_product.quantity_available = product_json.get('quantity_available', db_product.quantity_available)

    db.session.commit()
    return '', 204


# delete product with DELETE
@api_products_bp.route("<int:product_id>", methods=["DELETE"])
def product_delete(product_id):
    db_product = Product.query.get_or_404(product_id)
    db.session.delete(db_product)
    db.session.commit()
    return '', 204


# POST to return products below a certain stock value provided
# in the body of the response as key "threshold"
@api_products_bp.route("final/warning", methods=["POST"])
def product_final():
    # parse JSON with the function, passing "threshold" as a required field
    success, error_message = parse_json(request.json, "threshold")
    if not success:
        return error_message, 400

    # get the threshold value
    threshold = request.json.get("threshold")

    # get all products
    products = Product.query.all()
    # filter and jsonify those where quantity_available <= threshold
    products_json_return = [product.to_json() for product in products if product.quantity_available <= threshold]
    # build response body
    product_return = []
    for product in products_json_return:
        product_return.append({
            "name": product["name"],
            "available": product["quantity_available"]
        })
    response_body = {
        "threshold": threshold,
        "products": product_return
    }
    return response_body

# return all categories with GET
@api_products_bp.route("/categories", methods=["GET"])
def categories_json():
    categories = Category.query.order_by(Category.name).all()
    return jsonify([category.to_json() for category in categories])


@api_products_bp.route("final/categories/<category_name>", methods=["PUT"])
def category_fill(category_name):
    success, error_message = parse_json(request.json, "products")
    if not success:
        return error_message, 400

    products = request.json.get("products")

    category = Category.query.filter_by(name=category_name).first_or_404()

    for product in products:
        product_obj = Product.query.filter_by(name=product).first()
        product_obj.category = category

    db.session.commit()

    products = Product.query.all()
    products_json_return = [product.to_json() for product in products if product.category.id == category.id]
    returnobj = []
    for product in products_json_return:
        returnobj.append(product["name"])
    return_body = {"products": returnobj}

    return jsonify(return_body)

