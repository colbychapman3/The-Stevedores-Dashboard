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
    # Get port from environment variable (for deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=False)

