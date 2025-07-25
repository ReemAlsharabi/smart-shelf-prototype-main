# Smart Shelf Replenishment System with Environmental Monitoring

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random
import threading
import time

app = Flask(__name__)

# ===================== DATA STORES =====================
products = {
    'Milk': {
        'stock': 10,
        'threshold': 5,
        'sales': 0,
        'safe_temp': (2, 8),
        'safe_humidity': (60, 90),
        'sensors': {
            'shelf': {'temp': 5.0, 'humidity': 75},
            'inventory': {'temp': 7.0, 'humidity': 65}
        }
    },
    'Bread': {
        'stock': 20,
        'threshold': 8,
        'sales': 0,
        'safe_temp': (20, 25),
        'safe_humidity': (30, 60),
        'sensors': {
            'shelf': {'temp': 22.0, 'humidity': 45},
            'inventory': {'temp': 25.0, 'humidity': 55}
        }
    }
}

supplier_inventory = {
    'Milk': 15,
    'Bread': 8
}

restock_requests = []
request_id = 1
sensor_history = {p: [] for p in products.keys()}

# ===================== BACKGROUND SENSOR UPDATE =====================
def update_environment():
    while True:
        for pname, pdata in products.items():
            # Get safe bounds
            t_min, t_max = pdata['safe_temp']
            h_min, h_max = pdata['safe_humidity']

            # 50% chance to go out of bounds slightly (to trigger alerts)
            def maybe_outside(value_range, lower_wiggle=2, upper_wiggle=2):
                if random.random() < 0.5:
                    return round(random.uniform(value_range[0], value_range[1]), 1)
                else:
                    if random.random() < 0.5:
                        return round(random.uniform(value_range[0] - lower_wiggle, value_range[0] - 0.1), 1)
                    else:
                        return round(random.uniform(value_range[1] + 0.1, value_range[1] + upper_wiggle), 1)

            pdata['sensors']['shelf']['temp'] = maybe_outside((t_min, t_max))
            pdata['sensors']['shelf']['humidity'] = int(maybe_outside((h_min, h_max), 5, 10))
            pdata['sensors']['inventory']['temp'] = maybe_outside((t_min + 2, t_max + 2))
            pdata['sensors']['inventory']['humidity'] = int(maybe_outside((h_min, h_max), 5, 10))

            # Record history (last 20)
            sensor_history[pname].append({
                'timestamp': datetime.now().isoformat(),
                'shelf': pdata['sensors']['shelf'].copy(),
                'inventory': pdata['sensors']['inventory'].copy()
            })
            if len(sensor_history[pname]) > 20:
                sensor_history[pname] = sensor_history[pname][-20:]
        time.sleep(10)


env_thread = threading.Thread(target=update_environment)
env_thread.daemon = True
env_thread.start()

# ===================== ROUTES =====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stock', methods=['GET', 'POST'])
def manage_stock():
    global request_id
    if request.method == 'POST':
        data = request.get_json()
        product = data.get('product')
        new_stock = data.get('stock')

        if product not in products or new_stock < 0:
            return jsonify({'error': 'Invalid data'}), 400

        old_stock = products[product]['stock']
        products[product]['stock'] = new_stock

        if old_stock > new_stock:
            products[product]['sales'] += (old_stock - new_stock)

        needed_qty = max(0, products[product]['threshold'] - products[product]['stock'])
        pending_qty = sum(r['quantity'] for r in restock_requests if r['product'] == product and r['status'] == 'Pending')

        if needed_qty > pending_qty and supplier_inventory.get(product, 0) > 0:
            restock_requests.append({
                'id': request_id,
                'product': product,
                'quantity': min(needed_qty - pending_qty, supplier_inventory[product]),
                'status': 'Pending',
                'timestamp': datetime.now().isoformat(),
                'comment': ""
            })
            request_id += 1

        return jsonify({product: products[product]})

    return jsonify(products)

@app.route('/requests', methods=['GET', 'POST'])
def handle_requests():
    global request_id
    if request.method == 'POST':
        data = request.get_json()
        req_id = data.get('id')
        action = data.get('action')
        comment = data.get('comment', '')

        for r in restock_requests:
            if r['id'] == req_id and r['status'] == 'Pending':
                product = r['product']
                available = supplier_inventory.get(product, 0)
                if action == 'approve' and available <= 0:
                    r['comment'] += " | Skipped: no supplier stock available."
                    break

                r['status'] = 'Approved' if action == 'approve' else 'Rejected'
                r['comment'] = comment
                r['decision_time'] = datetime.now().isoformat()

                if r['status'] == 'Approved':
                    requested_qty = r['quantity']
                    current_need = max(0, products[product]['threshold'] - products[product]['stock'])
                    other_pending = sum(x['quantity'] for x in restock_requests if x['product'] == product and x['status'] == 'Pending' and x['id'] != req_id)
                    net_need = max(0, current_need - other_pending)
                    restock_qty = min(requested_qty, available, net_need)
                    products[product]['stock'] += restock_qty
                    supplier_inventory[product] -= restock_qty

                    if restock_qty < requested_qty:
                        restock_requests.append({
                            'id': request_id,
                            'product': product,
                            'quantity': requested_qty - restock_qty,
                            'status': 'Pending',
                            'timestamp': datetime.now().isoformat(),
                            'comment': "Partial restock, awaiting inventory"
                        })
                        request_id += 1
                break
    return jsonify(restock_requests)

@app.route('/analytics')
def analytics():
    return jsonify({
        'total': len(restock_requests),
        'pending': sum(1 for r in restock_requests if r['status'] == 'Pending'),
        'approved': sum(1 for r in restock_requests if r['status'] == 'Approved'),
        'rejected': sum(1 for r in restock_requests if r['status'] == 'Rejected'),
        'sales': {p: v['sales'] for p, v in products.items()},
        'stock': {p: v['stock'] for p, v in products.items()},
        'supplier': supplier_inventory,
        'sensors': {p: v['sensors'] for p, v in products.items()},
        'alerts': check_environment_alerts()
    })

@app.route('/sensor-history')
def get_sensor_history():
    return jsonify(sensor_history)

@app.route('/config', methods=['POST'])
def update_config():
    data = request.get_json()
    product = data.get('product')
    if product not in products:
        return jsonify({'error': 'Invalid product'}), 400

    products[product]['threshold'] = data.get('threshold', products[product]['threshold'])
    products[product]['safe_temp'] = tuple(data.get('safe_temp', products[product]['safe_temp']))
    products[product]['safe_humidity'] = tuple(data.get('safe_humidity', products[product]['safe_humidity']))
    return jsonify({'message': 'Updated successfully'})

# ===================== ALERT CHECK =====================
def check_environment_alerts():
    alerts = {}
    for pname, pdata in products.items():
        alerts[pname] = []
        for loc in ['shelf', 'inventory']:
            sensor = pdata['sensors'].get(loc, {})
            temp = sensor.get('temp')
            humidity = sensor.get('humidity')
            if temp is None or humidity is None:
                continue
            min_temp, max_temp = pdata['safe_temp']
            min_h, max_h = pdata['safe_humidity']
            if not (min_temp <= temp <= max_temp):
                alerts[pname].append(f"{loc.capitalize()} temp out of range: {temp}°C")
            if not (min_h <= humidity <= max_h):
                alerts[pname].append(f"{loc.capitalize()} humidity out of range: {humidity}%")
    return alerts
@app.route('/report-environment', methods=['POST'])
def report_environment():
    data = request.get_json()
    product = data.get('product')

    if product not in products:
        return jsonify({'error': 'Invalid product'}), 400

    # Simulate resolving environmental issues (adjust temp/humidity back to normal)
    def resolve_env():
        for _ in range(3):
            products[product]['sensors']['shelf']['temp'] = round(random.uniform(*products[product]['safe_temp']), 1)
            products[product]['sensors']['shelf']['humidity'] = random.randint(*products[product]['safe_humidity'])
            time.sleep(5)

    threading.Thread(target=resolve_env).start()

    return jsonify({'message': f'Environmental issue reported for {product}, auto-adjustment started.'})

if __name__ == '__main__':
    app.run(debug=True)
