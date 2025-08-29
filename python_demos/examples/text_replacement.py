#!/usr/bin/env python3
"""
Text Replacement Example

This script demonstrates how to read text from a specific editor
and replace the content of the active editor with modified text.
"""

import sys
import os

# Add workspace root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python_client.vscode_bridge import VSCodeBridge, VSCodeBridgeError

def main():
    """Read text from an editor and modify the active editor."""
    
    # Create bridge instance
    bridge = VSCodeBridge()
    
    try:
        # Connect to VS Code
        bridge.connect()
        
        # Get list of open editors
        editors = bridge.get_editor_titles()
        
        if not editors:
            bridge.notify("No editors are open!")
            print("✗ No editors are open")
            return 1
        
        # Show available files
        print("Available editors:")
        for i, editor in enumerate(editors, 1):
            print(f"{i}. {editor['title']}")
        
        # Ask user to select a file (for demo, we'll use the first one)
        if len(editors) > 0:
            selected_editor = editors[0]
            filename = selected_editor['title']
            
            print(f"\nReading text from: {filename}")
            
            # Get text from the selected editor
            current_text = bridge.get_text_from_editor(filename)
            
            print(f"Original text length: {len(current_text)} characters")
            print(f"First 100 characters: {current_text[:100]}...")
            
            # Transform the text (convert to uppercase for demo)
            transformed_text = current_text.upper()
            
            # Set the text in the active editor
            bridge.set_active_editor_text(transformed_text)
            
            # Notify completion
            bridge.notify(f"Text from {filename} converted to uppercase!")
            print("✓ Text transformation complete!")
        
    except VSCodeBridgeError as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())