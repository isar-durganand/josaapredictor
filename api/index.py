"""
Vercel Serverless Entry Point
This module exposes the Flask app for Vercel's Python runtime.
"""

import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, load_data

# Load data on cold start
load_data()

# Vercel expects 'app' as the WSGI handler
app = app
