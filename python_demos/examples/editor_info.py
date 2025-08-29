#!/usr/bin/env python3
"""
Editor Information Example

This script demonstrates how to get information about all open editors
in VS Code.
"""

import sys
import os

# Add workspace root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python_client.vscode_bridge import VSCodeBridge, VSCodeBridgeError

def main():
    """Get and display information about all open editors."""
    
    # Create bridge instance
    bridge = VSCodeBridge()
    
    try:
        # Connect to VS Code
        bridge.connect()
        
        # Get editor titles
        editors = bridge.get_editor_titles()
        
        # Display results
        print(f"Found {len(editors)} open editor(s):")
        print("=" * 50)
        
        for i, editor in enumerate(editors, 1):
            print(f"{i}. 📄 {editor['title']}")
            print(f"   URI: {editor['uri']}")
            print(f"   Full path: {editor['filename']}")
            print()
        
        # Send notification with count
        bridge.notify(f"Found {len(editors)} open editors")
        print("✓ Information retrieved and notification sent!")
        
    except VSCodeBridgeError as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())