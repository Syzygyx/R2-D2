#!/usr/bin/env python3
"""
SITH Web Simulator Launcher

Starts the web-based R2-D2 simulator.
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import flask
        import flask_socketio
        import eventlet
        print("✅ All dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main launcher function."""
    print("🤖 SITH Web Simulator Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot start simulator - missing dependencies")
        return 1
    
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("🌐 Starting web simulator...")
    print("📱 Opening browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Import and run the app
        from app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped by user")
    except Exception as e:
        print(f"❌ Error starting simulator: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())