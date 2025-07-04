#!/usr/bin/env python3
"""
Main entry point for the Maritime Dashboard Flask application.
This file is used for deployment and imports the actual Flask app from src/main.py
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app from the src directory
from src.main import app

if __name__ == '__main__':
    import sys
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    app.run(debug=True, host='0.0.0.0', port=port)