#!/usr/bin/env python3
"""
Production runner for the News Crawler Web Application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Set environment variables for production
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=False)
