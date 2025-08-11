#!/usr/bin/env python3
"""
Simple test script to run the web application
"""

import sys
import os

print("🔍 Testing web application startup...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    print("📦 Importing Flask...")
    from flask import Flask
    print("✅ Flask imported successfully")
    
    print("📦 Importing app module...")
    import app
    print("✅ App module imported successfully")
    
    print("🚀 Starting Flask application...")
    print("📍 Access at: http://localhost:5000")
    app.app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
