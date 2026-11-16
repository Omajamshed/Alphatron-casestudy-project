"""
Vercel Serverless Function entrypoint for ContractGuard FastAPI Backend.
Vercel's Python runtime automatically looks for an 'app' instance in /api/index.py.
"""

import sys
import os

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the FastAPI application
from app.main import app
