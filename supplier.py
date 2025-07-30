from flask import Flask, request, jsonify, render_template_string, redirect
from datetime import datetime
import threading
import time
import uuid

app = Flask(__name__)

# Simulated inventory
supplier_inventory = {
    'Milk': 20,
    'Bread': 15,
    'Eggs': 30
}

# Store incoming requests from retail stores
supplier_requests = []
@app.route('/inventory', methods=['GET'])
def get_inventory():
    return jsonify(supplier_inventory)
@app.route('/')

def home():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supplier Dashboard</title>
        <meta http-equiv="refresh" content="1">
        <style>
            body { font-family: Arial; padding: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
            th, td { border: 1px solid #ccc; padding: 8px; }
            th { background-color: #009688;color:white;}
            button {
              background-color: #009688;
              color: white;
              border: none;
              padding: 8px 14px;
              margin-top: 10px;
              cursor: pointer;
              border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <h2>📦 Supplier Inventory</h2>
        <table id="inventory-table">
            <thead>
                <tr><th>Product</th><th>Available Quantity</th></tr>
            </thead>
            <tbody>
                {% for product, qty in inventory.items() %}
                <tr><td>{{ product }}</td><td>{{ qty }}</td></tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>📋 Supplier Requests</h2>
        <table id="requests-table">
            <thead>
                <tr>
                    <th>Request ID</th><th>Product</th><th>Qty</th><th>Status</th>
                    <th>Store Name</th><th>Phone</th><th>Address</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for req in requests %}
                <tr>
                    <td>{{ req['id'] }}</td>
                    <td>{{ req['product'] }}</td>
                    <td>{{ req['quantity'] }}</td>
                    <td>{{ req['status'] }}</td>
                    <td>{{ req['store']['name'] }}</td>
                    <td>{{ req['store']['phone'] }}</td>
                    <td>{{ req['store']['address'] }}</td>
                    <td>
                        {% if req['status'] == 'Pending' %}
                        <form method="post" action="/update-request-status" style="display:inline;">
                            <input type="hidden" name="id" value="{{ req['id'] }}">
                            <input type="hidden" name="action" value="approve">
                            <button type="submit">Approve</button>
                        </form>
                        <form method="post" action="/update-request-status" style="display:inline;">
                            <input type="hidden" name="id" value="{{ req['id'] }}">
                            <input type="hidden" name="action" value="reject">
                            <button type="submit">Reject</button>
                        </form>
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, inventory=supplier_inventory, requests=supplier_requests)

@app.route('/new-request', methods=['POST'])
def new_request():
    data = request.get_json()
    product = data.get('product')
    quantity = data.get('quantity')
    store_info = data.get('store')

    if product not in supplier_inventory or not isinstance(quantity, int):
        return jsonify({'error': 'Invalid product or quantity'}), 400

    req_id = str(uuid.uuid4())[:8]
    supplier_requests.append({
        'id': req_id,
        'product': product,
        'quantity': quantity,
        'store': {
            'name': store_info.get('name'),
            'phone': store_info.get('phone'),
            'address': store_info.get('address')
        },
        'status': 'Pending',
        'dispatched_at': None
    })

    return jsonify({'message': 'Request received', 'id': req_id}), 200

@app.route('/update-request-status', methods=['POST'])
def update_request_status():
    req_id = request.form.get('id')
    action = request.form.get('action')

    for req in supplier_requests:
        if req['id'] == req_id and req['status'] == 'Pending':
            req['status'] = 'Approved' if action == 'approve' else 'Rejected'
            break
    return redirect('/')

def process_requests():
    while True:
        for req in supplier_requests:
            if req['status'] == 'Approved':

                print(f"[START] Processing request {req['id']}")
                time.sleep(1)
                req['status'] = 'processing started'
                # Simulate picking
                print(f"[Picking] {req['quantity']} x {req['product']}")
                time.sleep(1)
                req['status'] = 'picking items'
                # Simulate packing
                print(f"[Packing] {req['quantity']} x {req['product']}")
                time.sleep(1)
                req['status'] = 'packing items'


                # Dispatch
                if supplier_inventory[req['product']] >= req['quantity']:
                    supplier_inventory[req['product']] -= req['quantity']
                    req['status'] = 'Dispatched'
                    req['dispatched_at'] = datetime.now().isoformat()
                    print(f"[Dispatched] {req['product']} to {req['store']['name']}")
                else:
                    req['status'] = 'Failed - Out of stock'
                    print(f"[FAILED] Not enough stock for {req['id']}")
        time.sleep(5)

# Start background thread
threading.Thread(target=process_requests, daemon=True).start()

if __name__ == '__main__':
    app.run(port=5001, debug=True)
