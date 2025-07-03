import os
import secrets

# Define base directory for robust path construction
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load secret key from environment variable or use a default (less secure, for development only)
SECRET_KEY = os.environ.get('MARITIME_SECRET_KEY')
if not SECRET_KEY:
    print("WARNING: MARITIME_SECRET_KEY environment variable not set. Using default development key.", file=sys.stderr)
    print("WARNING: For production, set a strong, unique MARITIME_SECRET_KEY environment variable.", file=sys.stderr)
    SECRET_KEY = secrets.token_hex(32) # Generate a random key for development if not set

MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'app.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
