#!/usr/bin/env python3
"""
Debug script to test what's happening with the web application
"""

import sys
import os

print("🔍 Debug: Starting Task Planner Web Application")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")

# Test 1: Check if we can import basic modules
try:
    print("\n📦 Testing basic imports...")
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

# Test 2: Check if we can import our app module
try:
    print("\n📦 Testing app import...")
    import app
    print("✅ App module imported successfully")
    print(f"✅ Database manager status: {'Connected' if app.db_manager else 'Not connected'}")
except Exception as e:
    print(f"❌ App import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Try to start the server
try:
    print("\n🚀 Starting Flask server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("💡 Press Ctrl+C to stop")
    print("-" * 50)
    
    # Force flush output
    sys.stdout.flush()
    
    app.app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    
except KeyboardInterrupt:
    print("\n👋 Server stopped by user")
except Exception as e:
    print(f"\n❌ Server failed to start: {e}")
    import traceback
    traceback.print_exc()
