from flask import Flask
from pathlib import Path
from db import db

# import routes
from routes import api_products_bp, api_customers_bp, api_orders_bp, html_routes_bp, api_final_bp

# initialize flask
flaskapp = Flask(__name__)
flaskapp.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shopdatabase.db"
flaskapp.instance_path = Path(".").resolve()

# register blueprints
flaskapp.register_blueprint(api_customers_bp, url_prefix="/api/customers")
flaskapp.register_blueprint(api_products_bp, url_prefix="/api/products")
flaskapp.register_blueprint(api_orders_bp, url_prefix="/api/orders")
flaskapp.register_blueprint(html_routes_bp, url_prefix="/")
flaskapp.register_blueprint(api_final_bp, url_prefix="/final")

# initialize the db
db.init_app(flaskapp)


if __name__ == "__main__":
    flaskapp.run(debug=True, port=8888)
