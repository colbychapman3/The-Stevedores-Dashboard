from flask import Flask, render_template, jsonify, send_from_directory, make_response, request
import os

app = Flask(__name__)

# PWA routes
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/offline')
def offline_page():
    return render_template('offline.html')

# Main application routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ships')
def ships():
    return render_template('ships.html')

@app.route('/containers')
def containers():
    return render_template('containers.html')

@app.route('/crew')
def crew():
    return render_template('crew.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/master-dashboard')
def master_dashboard():
    return render_template('master-dashboard.html')

# Enhanced PWA routes
@app.route('/ship-status')
def ship_status():
    return render_template('ship_status.html')

@app.route('/berth-management')
def berth_management():
    return render_template('berth_management.html')

@app.route('/vessel-schedules')
def vessel_schedules():
    return render_template('vessel_schedules.html')

@app.route('/safety-protocols')
def safety_protocols():
    return render_template('safety_protocols.html')

@app.route('/emergency-contacts')
def emergency_contacts():
    return render_template('emergency_contacts.html')

@app.route('/tide-tables')
def tide_tables():
    return render_template('tide_tables.html')

# API endpoints
@app.route('/api/stats')
def api_stats():
    return jsonify({
        'ships': {'total': 4, 'active': 2, 'maintenance': 1, 'inactive': 1},
        'containers': {'total': 156, 'loaded': 89, 'empty': 45, 'transit': 22},
        'crew': {'total': 24, 'on_duty': 18, 'off_duty': 4, 'break': 2}
    })

@app.route('/api/ship-status', methods=['POST'])
def api_ship_status():
    if request.is_json:
        data = request.json
        print(f"Received ship status update: {data}")
        return jsonify({"message": "Update received", "data": data}), 200
    return jsonify({"message": "Invalid request, JSON expected"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
