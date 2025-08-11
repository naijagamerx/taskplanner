#!/usr/bin/env python3
"""
Minimal Flask app to test if the web server works
"""

try:
    from flask import Flask, render_template_string
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Task Planner Web - Test</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">🎉 Task Planner Web is Working!</h1>
                <p class="text-center">The web server is running successfully.</p>
                <div class="text-center">
                    <a href="/test" class="btn btn-primary">Test Page</a>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    @app.route('/test')
    def test():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>✅ Test Page</h1>
                <p>This confirms the Flask application is working correctly.</p>
                <a href="/" class="btn btn-secondary">Back to Home</a>
            </div>
        </body>
        </html>
        ''')
    
    if __name__ == '__main__':
        print("🌐 Starting minimal Task Planner Web Application...")
        print("📍 Access at: http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
except ImportError as e:
    print(f"❌ Flask not available: {e}")
    print("Please install Flask: pip install flask")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
