import json
import os

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

products = []
nextProductId = 0


def validate_product_structure_create(product):
    return 'name' in product.keys() and 'description' in product.keys() and len(product.keys()) == 2 and type(
        product['name']) == type(str()) and type(product['description']) == type(str())


def validate_product_structure_update(product):
    for item in product.items():
        if item[0] != 'name' and item[0] != 'description' and item[0] != 'icon':  # предполагаем, что id изменить нельзя
            return False
        if type(item[1]) != type(str()):
            print(type(item[1]))
            return False

    return True


def find_product(id):
    for i, product in enumerate(products):
        if product['id'] == id:
            return i, product

    return -1, None


@app.route('/product', methods=['POST'])
def create_product():
    global nextProductId

    try:
        product = json.loads(request.data)
    except json.decoder.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON.'}), 400

    if not validate_product_structure_create(product):
        return jsonify({'error': 'Product structure invalid.'}), 400

    product['id'] = nextProductId
    nextProductId += 1
    products.append(product)

    return jsonify(product), 200


@app.route('/product/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def product_workflow(id: int):
    idx, product = find_product(id)

    if not product:
        return jsonify({'error': 'Product does not exist.'}), 404

    if request.method == 'GET':
        return jsonify(product), 200

    if request.method == 'PUT':
        try:
            updated_product = json.loads(request.data)
        except json.decoder.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON.'}), 400

        if not validate_product_structure_update(updated_product):
            return jsonify({'error': 'Product structure invalid.'}), 400

        if 'icon' in updated_product and updated_product['icon']:
            new_filename = updated_product['icon']
            old_filename = product.get('icon')
            if old_filename and old_filename != new_filename:
                if os.path.exists(old_filename):
                    os.rename(old_filename, new_filename)

                updated_product['icon'] = new_filename

        product.update(updated_product)
        products[idx] = product

        return jsonify(products[idx]), 200

    if request.method == 'DELETE':
        products.remove(product)

        return jsonify(product), 200


@app.route('/product/<int:id>/image', methods=['POST', 'GET'])
def upload_image(id: int):
    idx, product = find_product(id)
    if not product:
        return jsonify({'error': 'Product does not exist.'}), 404

    if request.method == 'POST':
        if 'icon' not in request.files:
            return jsonify({'error': 'No image part in the request'}), 400

        file = request.files['icon']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        file.save(file.filename)

        product['icon'] = file.filename
        products[idx] = product

        return jsonify({'product': product}), 200

    if request.method == 'GET':
        idx, product = find_product(id)
        if not product:
            return jsonify({'error': 'Product does not exist.'}), 404

        icon_filename = product.get('icon')
        if not icon_filename:
            return jsonify({'error': 'No icon for this product.'}), 400

        return send_file(icon_filename)
    
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products), 200


if __name__ == '__main__':
    app.run()
