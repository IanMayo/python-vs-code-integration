"""
VS Code Bridge - Python Client

This module provides a simplified Python interface to communicate with the 
VS Code extension through WebSocket messages.
"""

import json
import logging
import threading
import atexit
from typing import Optional, Dict, Any, List, Union

try:
    import websocket
except ImportError:
    raise ImportError(
        "websocket-client library is required. Install it with: pip install websocket-client"
    )


class VSCodeBridgeError(Exception):
    """Exception raised for errors in the VS Code Bridge communication."""
    
    def __init__(self, message: str, code: Optional[Union[int, str]] = None):
        super().__init__(message)
        self.code = code


class VSCodeBridge:
    """WebSocket client for communicating with VS Code extension."""
    
    _instance: Optional['VSCodeBridge'] = None
    _lock = threading.Lock()
    
    def __new__(cls, port: int = 60123) -> 'VSCodeBridge':
        # Singleton pattern - ensure only one instance per port
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, port: int = 60123):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.port = port
        self.url = f"ws://localhost:{port}"
        self.ws: Optional[websocket.WebSocket] = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
        # Register cleanup
        atexit.register(self.cleanup)
    
    def connect(self) -> None:
        """Establish connection to the WebSocket server."""
        if self.connected and self.ws:
            return
            
        try:
            self.logger.info("Connecting to VS Code WebSocket server...")
            self.ws = websocket.create_connection(self.url, timeout=10)
            self.connected = True
            self.logger.info("Connected successfully!")
            
            # Read the welcome message
            try:
                welcome = self.ws.recv()
                self.logger.debug(f"Welcome message: {welcome}")
            except Exception:
                pass  # Welcome message is optional
                
        except Exception as e:
            self.connected = False
            self.ws = None
            raise VSCodeBridgeError(f"Connection failed: {str(e)}")
    
    def send_raw_message(self, message: str) -> str:
        """Send a raw string message and return the response."""
        if not self.connected:
            self.connect()
            
        if not self.connected or not self.ws:
            raise VSCodeBridgeError("Not connected to WebSocket server")
        
        try:
            # Send message
            self.ws.send(message)
            
            # Receive response
            response = self.ws.recv()
            # Ensure we return a string
            if isinstance(response, str):
                return response
            elif isinstance(response, bytes):
                return response.decode('utf-8')
            else:
                return str(response)
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            self.connected = False
            self.ws = None
            raise VSCodeBridgeError(f"Message send failed: {e}")
    
    def send_json_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON message and return the parsed response."""
        if not self.connected:
            self.connect()
        
        json_str = json.dumps(message)
        response_str = self.send_raw_message(json_str)
        
        try:
            response = json.loads(response_str)
            
            # Check for errors in response
            if 'error' in response:
                error_info = response['error']
                raise VSCodeBridgeError(
                    error_info.get('message', 'Unknown error'),
                    error_info.get('code')
                )
                
            return response
        except json.JSONDecodeError as e:
            raise VSCodeBridgeError(f"Invalid JSON response: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
        self.connected = False

    # Public API Methods
    
    def notify(self, message: str) -> None:
        """Display a notification in VS Code."""
        command = {
            "command": "notify",
            "params": {
                "message": message
            }
        }
        self.send_json_message(command)
    
    def get_editor_titles(self) -> List[Dict[str, str]]:
        """Get titles and URIs of all open editors."""
        command = {
            "command": "get_titles_of_active_editors",
            "params": {}
        }
        
        response = self.send_json_message(command)
        return response.get('result', [])
    
    def get_text_from_editor(self, filename: str) -> str:
        """Get the text content from a named editor."""
        command = {
            "command": "get_text_from_named_editor",
            "params": {
                "filename": filename
            }
        }
        
        response = self.send_json_message(command)
        return response.get('result', '')
    
    def set_active_editor_text(self, text: str) -> None:
        """Set the text content of the currently active editor."""
        command = {
            "command": "set_text_of_active_editor",
            "params": {
                "text": text
            }
        }
        
        self.send_json_message(command)