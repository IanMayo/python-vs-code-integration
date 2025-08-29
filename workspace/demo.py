#!/usr/bin/env python3
"""
Python-VS Code Bridge - Interactive Demo

This script provides an interactive demonstration of all the bridge capabilities.
Run this script to see the Python-VS Code WebSocket bridge in action!

Prerequisites:
1. VS Code extension must be running (press F5 to launch Extension Development Host)
2. Python dependencies installed: pip install -r python_client/requirements.txt
3. Have some files open in VS Code for best demonstration
"""

import sys
import os
import time

from python_client.vscode_bridge import VSCodeBridge, VSCodeBridgeError

def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step: str):
    """Print a formatted step."""
    print(f"\n🔹 {step}")

def wait_for_user():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to continue...")

def demo_notifications(bridge: VSCodeBridge):
    """Demo the notification functionality."""
    print_header("1. NOTIFICATIONS DEMO")
    
    print("This demo shows how Python can send notifications to VS Code.")
    wait_for_user()
    
    notifications = [
        "🐍 Hello from Python!",
        "✨ Python-VS Code Bridge is working!",
        "🎯 This demonstrates bidirectional communication",
        "🚀 Ready for more advanced features..."
    ]
    
    for i, message in enumerate(notifications, 1):
        print_step(f"Sending notification {i}/{len(notifications)}: {message}")
        bridge.notify(message)
        time.sleep(1.5)  # Pause between notifications
    
    print("\n✅ Notification demo complete!")

def demo_editor_info(bridge: VSCodeBridge):
    """Demo getting editor information."""
    print_header("2. EDITOR INFORMATION DEMO")
    
    print("This demo shows how Python can query VS Code for open editor information.")
    wait_for_user()
    
    print_step("Querying VS Code for open editors...")
    
    try:
        editors = bridge.get_editor_titles()
        
        if not editors:
            print("❌ No editors are currently open in VS Code!")
            bridge.notify("Please open some files in VS Code for a better demo experience")
            return []
        
        print(f"\n📊 Found {len(editors)} open editor(s):")
        print("-" * 50)
        
        for i, editor in enumerate(editors, 1):
            print(f"{i:2}. 📄 {editor['title']}")
            print(f"     Path: {editor['filename']}")
            print(f"     URI:  {editor['uri']}")
            print()
        
        bridge.notify(f"Python discovered {len(editors)} open files!")
        print("✅ Editor information demo complete!")
        return editors
        
    except VSCodeBridgeError as e:
        print(f"❌ Error getting editor info: {e}")
        return []

def demo_text_reading(bridge: VSCodeBridge, editors: list):
    """Demo reading text from editors."""
    print_header("3. TEXT READING DEMO")
    
    if not editors:
        print("❌ No editors available for text reading demo.")
        return None
    
    print("This demo shows how Python can read text content from VS Code editors.")
    wait_for_user()
    
    # Use the first editor for demo
    selected_editor = editors[0]
    filename = selected_editor['title']
    
    print_step(f"Reading text from: {filename}")
    
    try:
        content = bridge.get_text_from_editor(filename)
        
        print(f"\n📖 Content preview from {filename}:")
        print("-" * 40)
        
        lines = content.split('\n')
        for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
            print(f"{i:2}: {line}")
        
        if len(lines) > 10:
            print(f"... ({len(lines) - 10} more lines)")
        
        print(f"\n📊 File statistics:")
        print(f"   Lines: {len(lines)}")
        print(f"   Characters: {len(content)}")
        print(f"   Words: {len(content.split())}")
        
        bridge.notify(f"Python read {len(lines)} lines from {filename}")
        print("✅ Text reading demo complete!")
        return content
        
    except VSCodeBridgeError as e:
        print(f"❌ Error reading text: {e}")
        return None

from typing import Optional

def demo_text_modification(bridge: VSCodeBridge, original_content: Optional[str]):
    """Demo modifying text in the active editor."""
    print_header("4. TEXT MODIFICATION DEMO")
    
    if not original_content:
        print("❌ No content available for text modification demo.")
        return
    
    print("This demo shows how Python can modify the text in VS Code's active editor.")
    print("⚠️  This will temporarily replace the content of your active editor!")
    
    response = input("\nProceed with text modification demo? (y/N): ").lower().strip()
    if response != 'y':
        print("Skipping text modification demo.")
        return
    
    print_step("Creating demo content...")
    
    demo_content = f"""# Python-VS Code Bridge Demo Results
Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Demo Summary
✅ Notifications: Successfully sent multiple notifications to VS Code
✅ Editor Info: Retrieved information about open editors  
✅ Text Reading: Read content from VS Code editor
✅ Text Modification: Modified active editor content (this document!)

## Original Content Analysis
- Lines: {len(original_content.split(chr(10)))}
- Characters: {len(original_content)}
- Words: {len(original_content.split())}

## Bridge Capabilities Demonstrated
1. **Bidirectional Communication**: Python ↔ VS Code
2. **Real-time Notifications**: Instant feedback in VS Code UI
3. **Editor Integration**: Read/write access to editor content
4. **File System Awareness**: Knowledge of open files and their paths

## Next Steps
- Explore the examples/ directory for more specific use cases
- Extend the bridge with additional commands for your needs
- Use this pattern for automated tooling and workflows

---
💡 **Tip**: You can restore the original content by pressing Ctrl+Z (Undo)

Original content has been preserved and can be restored.
"""
    
    try:
        bridge.set_active_editor_text(demo_content)
        bridge.notify("✨ Demo content generated! Check your active editor!")
        
        print("✅ Text modification demo complete!")
        print("   📝 Check your active VS Code editor to see the generated report")
        print("   💡 Press Ctrl+Z in VS Code to restore original content")
        
        # Wait a bit, then offer to restore
        time.sleep(3)
        
        restore = input("\nRestore original content now? (Y/n): ").lower().strip()
        if restore != 'n':
            print_step("Restoring original content...")
            bridge.set_active_editor_text(original_content)
            bridge.notify("Original content restored!")
            print("✅ Original content restored!")
        
    except VSCodeBridgeError as e:
        print(f"❌ Error modifying text: {e}")

def main():
    """Run the complete interactive demo."""
    print_header("PYTHON-VS CODE BRIDGE - INTERACTIVE DEMO")
    
    print("""
Welcome to the Python-VS Code Bridge interactive demonstration!

This demo will showcase all the key capabilities:
• Sending notifications from Python to VS Code
• Querying VS Code for information about open editors  
• Reading text content from VS Code files
• Modifying text content in VS Code editors

Prerequisites:
✅ VS Code extension running (press F5 to launch Extension Development Host)
✅ Python dependencies installed (pip install -r python_client/requirements.txt)
💡 For best experience, have some files open in VS Code

Let's get started!
""")
    
    wait_for_user()
    
    # Create bridge connection
    print_step("Connecting to VS Code...")
    bridge = VSCodeBridge()
    
    try:
        bridge.connect()
        print("✅ Connected to VS Code WebSocket bridge!")
        bridge.notify("🎉 Python demo script connected!")
        
    except VSCodeBridgeError as e:
        print(f"❌ Failed to connect to VS Code: {e}")
        print("\n💡 Make sure:")
        print("   1. VS Code extension is running (press F5 in VS Code)")
        print("   2. Extension Development Host window is open")
        print("   3. No firewall blocking localhost:60123")
        return 1
    
    # Run demonstrations
    try:
        # Demo 1: Notifications
        demo_notifications(bridge)
        
        # Demo 2: Editor information
        editors = demo_editor_info(bridge)
        
        # Demo 3: Text reading
        original_content = demo_text_reading(bridge, editors)
        
        # Demo 4: Text modification
        demo_text_modification(bridge, original_content)
        
        # Final summary
        print_header("DEMO COMPLETE!")
        
        bridge.notify("🎊 Python-VS Code Bridge demo completed successfully!")
        
        print("""
🎉 Congratulations! You've successfully demonstrated the Python-VS Code Bridge.

What you've seen:
✅ Python sending real-time notifications to VS Code
✅ Python querying VS Code for editor information
✅ Python reading file contents from VS Code
✅ Python modifying editor content in VS Code

## Next Steps:
📁 Explore the examples/ directory for specific use cases:
   • basic_notify.py - Simple notification example
   • editor_info.py - Editor information retrieval
   • text_replacement.py - Text manipulation example  
   • automated_workflow.py - Complex automation workflow

🔧 Extend the bridge for your own use cases:
   • Add new WebSocket commands in src/websocketServer.ts
   • Add corresponding Python methods in python_client/vscode_bridge.py
   • Build automated development workflows

📚 Check README.md for complete documentation and API reference.

Thank you for trying the Python-VS Code Bridge! 🚀
""")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
        bridge.notify("Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during demo: {e}")
        return 1

if __name__ == "__main__":
    exit(main())