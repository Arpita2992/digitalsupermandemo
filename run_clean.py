#!/usr/bin/env python3
"""Production-ready Flask startup with SSL error suppression"""

import os
import logging
import sys
from werkzeug.serving import WSGIRequestHandler, make_server
from werkzeug._internal import _log

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main app
from app import app

class SilentRequestHandler(WSGIRequestHandler):
    """Custom request handler that suppresses SSL/TLS handshake errors"""
    
    def log_request(self, code='-', size='-'):
        """Only log successful requests"""
        if isinstance(code, str):
            if code.startswith('2') or code.startswith('3'):
                super().log_request(code, size)
        elif 200 <= code < 400:
            super().log_request(code, size)
    
    def handle_one_request(self):
        """Handle requests with SSL error suppression"""
        try:
            super().handle_one_request()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            # Silently ignore connection errors (SSL handshake failures)
            pass
        except Exception as e:
            # Log unexpected errors but don't crash
            if "Bad request version" not in str(e):
                _log('error', 'Request handling error: %s', e)

def run_flask_clean():
    """Run Flask with clean error handling"""
    
    # Suppress Werkzeug logging for SSL errors
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)
    
    # Create server with custom handler
    server = make_server(
        host='127.0.0.1',
        port=8888,
        app=app,
        threaded=True,
        request_handler=SilentRequestHandler
    )
    
    print("🚀 Digital Superman Flask Application")
    print("=" * 40)
    print("📡 URL: http://localhost:8888")
    print("🔒 Security: Rate limiting, CSRF protection")
    print("⚡ Performance: Monitoring active")
    print("🛡️  SSL/TLS errors: Suppressed")
    print("🎯 Status: Ready for testing")
    print("")
    print("Press Ctrl+C to stop the server")
    print("")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    run_flask_clean()
