from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from repository import MT5Repository
from service import MarketDataService

class MarketDataApp:
    """
    Main Application class to setup Flask, SocketIO, and dependencies.
    """
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Dependency Injection
        self.repository = MT5Repository()
        self.service = MarketDataService(self.repository, self.socketio)
        
        self._setup_routes()

    def _setup_routes(self):
        """Define SocketIO event handlers"""
        @self.socketio.on('connect')
        def handle_connect():
            print("[INFO] Client connected")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("[INFO] Client disconnected")

    def run(self):
        print("[INFO] => Starting Market Data Application (Split Modules)")
        try:
            self.service.start()
            self.socketio.run(self.app, port=Config.PORT, allow_unsafe_werkzeug=True)
        except KeyboardInterrupt:
            print("[INFO] => Application stopping...")
            self.service.stop()

if __name__ == '__main__':
    app = MarketDataApp()
    app.run()
