#!/usr/bin/env python3
"""
Autonomous Cognitive Engine - Startup Script
Simple launcher for the web UI
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    try:
        import groq
        import langchain
        import langchain_groq
        import flask
        import flask_socketio
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f" Missing dependency: {e}")
        print(" Run: pip install -r requirements.txt")
        return False

def check_env():
    """Check if environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print(" GROQ_API_KEY not found in .env file")
        print(" Add your Groq API key to .env file")
        return False
    
    print(f" GROQ_API_KEY configured (starts with: {groq_key[:10]}...)")
    return True

def main():
    """Main startup function."""
    print(" Autonomous Cognitive Engine")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Check environment
    if not check_env():
        return False
    
    # Start the web UI
    print(" Starting Web UI...")
    print("📍 URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Import and run the app
        from app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f" Error starting web UI: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)