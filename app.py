from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

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

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'ships': {'total': 4, 'active': 2, 'maintenance': 1, 'inactive': 1},
        'containers': {'total': 156, 'loaded': 89, 'empty': 45, 'transit': 22},
        'crew': {'total': 24, 'on_duty': 18, 'off_duty': 4, 'break': 2}
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
