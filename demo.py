import requests
import json

# define the base url of the flask app
BASE_URL = 'http://127.0.0.1:8888'

# create products objects
products_data = [
    {
        "name": "example4",
        "price": 1.49,
        "quantity_available": 28
    },
    {
        "name": "example5",
        "price": 0.99,
        "quantity_available": 20
    },
    {
        "name": "example6",
        "price": 1.29,
        "quantity_available": 15
    }
]

# create new products
for product_data in products_data:
    response = requests.post(f'{BASE_URL}/api/products', json=product_data)
    if response.status_code == 201:
        print(f"Product '{product_data['name']}' created successfully")
    else:
        print(f"Failed to create product '{product_data['name']}'")

# create order objects
orders_data = [
    {
        "items": [
            {"name": "example4", "quantity": 10},
            {"name": "example6", "quantity": 8}
        ],
        "customer_id": 23
    },
    {
        "items": [
            {"name": "example4", "quantity": 30},
            {"name": "example5", "quantity": 10}
        ],
        "customer_id": 21
    },
    {
        "items": [
            {"name": "example6", "quantity": 15},
            {"name": "example4", "quantity": 5}
        ],
        "customer_id": 22
    }
]

print("\n")

# place new orders
for index, order_data in enumerate(orders_data, start=16):
    response = requests.post(f'{BASE_URL}/api/orders', json=order_data)
    if response.status_code == 201:
        print(f"Order {index} placed successfully")
    else:
        print(f"Failed to place order {index}")

print("\n")

# processing order 16 should process successfully as it only contains items that are fully in stock
process_order = input(f"Process order 16? (Y/N): ")
if process_order.upper() == 'Y':
    # make a put request to /api/orders/15 with a process key of True
    process_response = requests.put(f'{BASE_URL}/api/orders/16', json={"process": True})
    if process_response.status_code == 200:
        print(f"Order 15 processed successfully")
        print(json.dumps(process_response.json(), indent=4))

print("\n")

# process order 17 with strategy reject. this order contains products not in sufficient stock, this should
# not successfully process and make no changes to any product quantities or customer balance
process_order = input(f"Process order 17 with strategy reject? (Y/N): ")
if process_order.upper() == 'Y':
    # make a put request to /api/orders/16 with process key True and strategy reject
    process_response = requests.put(f'{BASE_URL}/api/orders/17', json={"process": True, "strategy": "reject"})
    print(json.dumps(process_response.json(), indent=4))

print("\n")

# re-process order 17 with strategy ignore. this should set the quantity of product example4 to 0 and continue
# processing example5 as usual, subtracting the quantity from the store stock and from customer balance
process_order = input(f"Process order 17 with strategy ignore? (Y/N): ")
if process_order.upper() == 'Y':
    process_response = requests.put(f'{BASE_URL}/api/orders/17', json={"process": True, "strategy": "ignore"})
    print(json.dumps(process_response.json(), indent=4))  # Print the response body with indentation

print("\n")

# process order 18 with default strategy (adjust) this should adjust the quantity of product example6 to exactly
# the quantity available, and subtract that from quantity_available and customer balance
process_order = input("Process order 18 with default strategy? (Y/N): ")
if process_order.upper() == 'Y':
    process_response = requests.put(f'{BASE_URL}/api/orders/18', json={"process": True})
    print(json.dumps(process_response.json(), indent=4))  # Print the response body with indentation

# attempt to create an order with a non-existent product
input("Create an order with a non-existent product? (Y/N): ")
# non-existent product order
invalid_product_order = {
    "customer_id": 1,
    "items": [
        {"name": "non_existing_product", "quantity": 5}
    ]
}

# make a put request to /api/orders
response = requests.post(f'{BASE_URL}/api/orders', json=invalid_product_order)
print(f"Response code: {response.status_code}")
print(f"Response body: {response.text}")

# attempt to create an order with an invalid quantity value
input(f"Create an order with an invalid quantity? (Y/N): ")
# invalid quantity order object
invalid_quantity_order = {
    "customer_id": 2,
    "items": [
        {"name": "example4", "quantity": -3}
    ]
}

# make a post request to /api/orders with the invalid quantity
response = requests.post(f'{BASE_URL}/api/orders', json=invalid_quantity_order)
print(f"Response code: {response.status_code}")
print(f"Response body: {response.text}")

# attempt to create a product with an invalid price
input("Create a product with an invalid price? (Y/N) ")
# invalid product object
invalid_product = {
    "name": "example10",
    "price": -5,
    "quantity_available": 15
}
# make a post request to /api/products with the invalid product object
response = requests.post(f"{BASE_URL}/api/products", json=invalid_product)
print(f"Response code: {response.status_code}")
print(f"Response body: {response.text}")
