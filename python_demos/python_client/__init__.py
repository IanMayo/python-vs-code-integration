"""
Python-VS Code Bridge - Python Client Library

This module provides a Python interface to communicate with VS Code
through WebSocket messages. It allows Python scripts to interact with
VS Code editors and display notifications.
"""

from .vscode_bridge import VSCodeBridge, VSCodeBridgeError

__version__ = "0.0.1"
__all__ = ["VSCodeBridge", "VSCodeBridgeError"]

# Global instance for easy access
bridge = VSCodeBridge()