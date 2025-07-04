import os
import sys
# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Flask, send_from_directory, jsonify, redirect
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.file_processor import file_processor_bp
from src.routes.ships import ships_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(file_processor_bp)
app.register_blueprint(ships_bp)

# Create database directory if it doesn't exist
db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
os.makedirs(db_dir, exist_ok=True)

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect('/master')

@app.route('/wizard')
def wizard():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/master')
def master_dashboard():
    return send_from_directory(app.static_folder, 'master-dashboard.html')

@app.route('/calendar')
def calendar_view():
    return send_from_directory(app.static_folder, 'calendar.html')

@app.route('/analytics')
def analytics_view():
    return send_from_directory(app.static_folder, 'analytics.html')

@app.route('/ship-info')
def ship_info():
    return send_from_directory(app.static_folder, 'ship-info.html')

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)