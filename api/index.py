"""
Vercel Serverless Entry Point for JoSAA College Predictor
This file wraps the Flask app for Vercel's serverless environment.
"""

import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app import app

# Vercel requires the app to be exposed as 'app' or 'handler'
# The @vercel/python runtime will automatically detect the Flask app
