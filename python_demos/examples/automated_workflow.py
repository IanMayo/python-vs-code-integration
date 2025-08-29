#!/usr/bin/env python3
"""
Automated Workflow Example

This script demonstrates a more complex workflow that combines all the
available API methods to perform automated analysis and processing.
"""

import sys
import os
import time
import re

# Add workspace root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python_client.vscode_bridge import VSCodeBridge, VSCodeBridgeError

def analyze_file_content(filename: str, content: str) -> dict:
    """Analyze file content and return statistics."""
    stats = {
        'filename': filename,
        'lines': len(content.split('\n')),
        'characters': len(content),
        'words': len(content.split()),
        'errors': len(re.findall(r'error|ERROR|Error', content)),
        'warnings': len(re.findall(r'warning|WARNING|Warning', content)),
        'todos': len(re.findall(r'TODO|FIXME|XXX', content, re.IGNORECASE)),
    }
    return stats

def generate_report(all_stats: list) -> str:
    """Generate a summary report from all file statistics."""
    if not all_stats:
        return "No files analyzed."
    
    total_lines = sum(stat['lines'] for stat in all_stats)
    total_chars = sum(stat['characters'] for stat in all_stats)
    total_words = sum(stat['words'] for stat in all_stats)
    total_errors = sum(stat['errors'] for stat in all_stats)
    total_warnings = sum(stat['warnings'] for stat in all_stats)
    total_todos = sum(stat['todos'] for stat in all_stats)
    
    report = f"""
# Code Analysis Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files analyzed: {len(all_stats)}
- Total lines: {total_lines:,}
- Total characters: {total_chars:,}
- Total words: {total_words:,}
- Errors found: {total_errors}
- Warnings found: {total_warnings}
- TODOs found: {total_todos}

## File Details
"""
    
    for stat in all_stats:
        report += f"""
### {stat['filename']}
- Lines: {stat['lines']:,}
- Characters: {stat['characters']:,}
- Words: {stat['words']:,}
- Errors: {stat['errors']}
- Warnings: {stat['warnings']}
- TODOs: {stat['todos']}
"""
    
    return report

def main():
    """Perform automated workflow: analyze files, generate report."""
    
    # Create bridge instance
    bridge = VSCodeBridge()
    
    try:
        # Connect to VS Code
        bridge.connect()
        bridge.notify("🔍 Starting automated code analysis...")
        
        # Get all open editors
        editors = bridge.get_editor_titles()
        
        if not editors:
            bridge.notify("No editors are open for analysis!")
            print("✗ No editors are open")
            return 1
        
        print(f"📊 Analyzing {len(editors)} open files...")
        bridge.notify(f"Analyzing {len(editors)} files...")
        
        # Analyze each file
        all_stats = []
        
        for i, editor in enumerate(editors, 1):
            filename = editor['title']
            print(f"  [{i}/{len(editors)}] Analyzing {filename}...")
            
            try:
                # Get file content
                content = bridge.get_text_from_editor(filename)
                
                # Analyze content
                stats = analyze_file_content(filename, content)
                all_stats.append(stats)
                
                # Show progress
                bridge.notify(f"Analyzed {filename} ({stats['lines']} lines)")
                
            except VSCodeBridgeError as e:
                print(f"    ⚠️  Could not analyze {filename}: {e}")
                continue
        
        # Generate comprehensive report
        print("📝 Generating analysis report...")
        report = generate_report(all_stats)
        
        # Set the report as the active editor content
        bridge.set_active_editor_text(report)
        
        # Final notification
        total_issues = sum(stat['errors'] + stat['warnings'] + stat['todos'] for stat in all_stats)
        bridge.notify(f"✅ Analysis complete! Found {total_issues} items requiring attention.")
        
        print("✓ Analysis complete! Report generated in active editor.")
        print(f"📈 Summary: {len(all_stats)} files, {total_issues} items found")
        
    except VSCodeBridgeError as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())