from flask import Blueprint, render_template
from models import Order, ProductOrder, Customer, Product

html_routes_bp = Blueprint('html_routes', __name__)


# reusable function to return all records of a database
def get_all_records(model):
    return model.query.order_by(model.id).all()


# homepage
@html_routes_bp.route("/")
def home():
    return render_template("homepage.html")


# display all orders using orders.html template
@html_routes_bp.route('/orders')
def orders():
    order_records = get_all_records(Order)
    return render_template('orders.html', orders=order_records)


# display all customers using customers.html template
@html_routes_bp.route('/customers')
def customers():
    customer_records = get_all_records(Customer)
    return render_template('customers.html', customers=customer_records)


# display all products using products.html template
@html_routes_bp.route('/products')
def products():
    product_records = get_all_records(Product)
    return render_template('products.html', products=product_records)


# display a single customer using customer_detail.html template
@html_routes_bp.route('/customer_detail/<int:customer_id>')
def customer_detail(customer_id):
    customer = Customer.query.get(customer_id)
    return render_template('customer_detail.html', customer=customer)


# display a single order using order_detail.html template
@html_routes_bp.route('/order_detail/<int:order_id>')
def order_detail(order_id):
    order_records = Order.query.get(order_id)
    return render_template('order_detail.html', order=order_records)
