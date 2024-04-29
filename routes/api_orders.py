from flask import Blueprint, request, redirect, url_for
from db import db
from models import Order, ProductOrder, Customer, Product

api_orders_bp = Blueprint("api_orders", __name__)


# parse JSON with required fields
def parse_json(data, *required_fields):
    for field in required_fields:
        if field not in data:
            return False, f"Invalid input. {field.capitalize()} is required"
    return True, None


# create order with POST
@api_orders_bp.route('/', methods=['POST'])
def create_order():
    new_order_json = request.json

    # customer_id and items are required fields
    success, error_message = parse_json(new_order_json, "customer_id", "items")
    if not success:
        return error_message, 400

    customer = db.get_or_404(Customer, new_order_json["customer_id"])
    order_items = []
    # each item should have a quantity int greater than 0
    for item in new_order_json['items']:
        if "quantity" not in item:
            return "Quantity is required for each item", 400
        if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
            return "Quantity must be a positive integer greater than 0", 400
        # product must exist in the shop db
        product_name = item['name']
        product = Product.query.filter_by(name=product_name).first()
        if not product:
            return f"Product '{product_name}' does not exist", 400
        # create ProductOrder object
        product_order = ProductOrder(quantity=item['quantity'], product_id=product.id)
        order_items.append(product_order)

    # create Order object
    new_order = Order(customer=customer, items=order_items)
    db.session.add(new_order)
    db.session.commit()
    return "Order created", 201


# delete order with POST
@api_orders_bp.route('/delete/<int:order_id>',methods=['POST'])
def delete_order_api(order_id):
    dead_order = db.get_or_404(Order, order_id)
    ProductOrder.query.filter_by(order_id=order_id).delete()
    db.session.delete(dead_order)
    db.session.commit()
    return redirect(url_for('html_routes.orders'))


# process order using the HTML button (must be POST as HTML does not support PUT requests for buttons)
@api_orders_bp.route("<int:order_id>/process", methods=["POST"])
def order_process_button(order_id):
    order = db.get_or_404(Order, order_id)
    if not order.process():
        return "Error processing order", 400
    return redirect(url_for('html_routes.orders'))


# process order using PUT
@api_orders_bp.route("<int:order_id>", methods=["PUT"])
def order_process(order_id):
    target_order = db.get_or_404(Order, order_id)
    # request must be JSON
    if not request.is_json:
        return 'Bad request, not JSON', 400

    # request must contain a boolean key 'process'
    order_json = request.json
    if 'process' not in order_json:
        return 'Bad request, missing process key', 400
    if not isinstance(order_json['process'], bool):
        return 'Bad request, process value must be boolean', 400

    # strategy must be 'adjust', 'reject', or 'ignore' with default 'adjust'
    strategy = order_json.get('strategy', 'adjust')
    if strategy not in ['adjust', 'reject', 'ignore']:
        return 'Bad request, invalid strategy', 400

    # if process key is True
    if order_json['process']:
        # for each item, get quantity_available
        original_quantity_available = {item.product.name: item.product.quantity_available for item in target_order.items}
        insufficient_stock = {}
        # for each item, check if there is sufficient quantity_available
        # if there is not, append the item to the insufficient_stock object
        for item in target_order.items:
            if item.quantity > item.product.quantity_available:
                insufficient_stock[item.product.name] = {
                    "ordered_quantity": item.quantity,
                    "quantity_available": item.product.quantity_available
                }

        # if strategy is 'reject' and there are insufficiently stocked items in the order
        if strategy == "reject" and insufficient_stock:
            response_body = {
                "strategy_used": strategy,
                "message": f"One or more items is not in sufficient stock. Order has not been processed, customer balance and item stock are unchanged",
                "insufficient_stock": insufficient_stock
            }
            return response_body, 400

        # if the order processing fails
        if not target_order.process(strategy=strategy):
            return 'Order processing failed', 400

        # get the new quantity_available after the order has processed and the quantity ordered has been
        # subtracted from the stock
        updated_quantity_available = {item.product.name: item.product.quantity_available for item in target_order.items}
        # create response body
        response_body = {
            "message": "Order processed",
            "strategy_used": strategy,
            "original_quantity_available": original_quantity_available,
            "updated_quantity_available": updated_quantity_available,
            "customer_balance": target_order.customer.balance
        }
        # if anything was insufficiently stocked, append the insufficient_stock object to the response body
        if insufficient_stock:
            response_body["insufficient_stock"] = insufficient_stock
        return response_body, 200
    else:
        return 'Process key was False, order processing canceled', 200
