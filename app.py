from flask import Flask, send_from_directory, make_response, render_template

app = Flask(__name__)

# PWA routes
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'no-cache' # Ensure the SW is fetched fresh
    return response

@app.route('/offline')
def offline_page(): # Renamed to avoid conflict with offline module if any
    return render_template('offline.html')

# Placeholder application routes (referenced in sw.js and base.html)
@app.route('/')
def index():
    # In a real app, you'd render a proper index page.
    # For now, we can just use base.html directly or create a simple index.html
    # For a slightly better experience, let's create a simple index.html template
    return render_template('index.html')

@app.route('/ship-status')
def ship_status():
    # Placeholder for ship status page
    # return render_template('base.html', title="Ship Status", content_message="Ship Status Page - Content Placeholder")
    return render_template('ship_status.html')


@app.route('/berth-management')
def berth_management():
    # Placeholder for berth management page
    # return render_template('base.html', title="Berth Management", content_message="Berth Management Page - Content Placeholder")
    return render_template('berth_management.html') # Covers "berth-assignments"

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

# Example API endpoint (referenced in sw.js for background sync)
@app.route('/api/ship-status', methods=['POST'])
def api_ship_status():
    # This is where you would handle incoming ship status updates
    # For now, just a placeholder response
    from flask import jsonify, request
    if request.is_json:
        data = request.json
        print(f"Received ship status update: {data}")
        # In a real app, save this to a database
        return jsonify({"message": "Update received", "data": data}), 200
    return jsonify({"message": "Invalid request, JSON expected"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001) # Changed port to avoid common conflicts
