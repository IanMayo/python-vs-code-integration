#!/usr/bin/env python3
"""
Basic Notification Example

This script demonstrates the simplest use case: sending a notification 
from Python to VS Code.
"""

import sys
import os

# Add the python_client directory to the path so we can import the bridge
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python_client'))

from vscode_bridge import VSCodeBridge, VSCodeBridgeError

def main():
    """Send a simple notification to VS Code."""
    
    # Create bridge instance
    bridge = VSCodeBridge()
    
    try:
        # Connect and send notification
        bridge.connect()
        bridge.notify("Hello from Python! 🐍")
        print("✓ Notification sent successfully!")
        
    except VSCodeBridgeError as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())