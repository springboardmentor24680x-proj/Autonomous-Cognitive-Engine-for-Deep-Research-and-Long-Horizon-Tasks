#!/usr/bin/env python3
"""
Simple test server to verify network connectivity
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🎉 Test Server Working!</h1>
    <p>If you can see this, your network connection is fine.</p>
    <p>The main app should work on the same port.</p>
    '''

if __name__ == '__main__':
    print("🧪 Starting simple test server...")
    print("🌐 URL: http://localhost:3000")
    app.run(debug=False, host='0.0.0.0', port=3000)