import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { GenericWebSocketServer } from './websocketServer';

let webSocketServer: GenericWebSocketServer | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('Python-VS Code Bridge Extension is now active!');
    
    vscode.window.showInformationMessage('Python-VS Code Bridge Extension has been activated successfully!');

    // Start WebSocket server
    webSocketServer = new GenericWebSocketServer();
    webSocketServer.start().catch(error => {
        console.error('Failed to start WebSocket server:', error);
        vscode.window.showErrorMessage('Failed to start Python-VS Code Bridge WebSocket Server. Python integration may not work.');
    });
    
    // Add cleanup to subscriptions
    context.subscriptions.push({
        dispose: () => {
            if (webSocketServer) {
                webSocketServer.stop().catch(error => {
                    console.error('Error stopping WebSocket server during cleanup:', error);
                });
            }
        }
    });

    // Register commands
    const helloWorldCommand = vscode.commands.registerCommand('python-vscode-bridge.helloWorld', () => {
        vscode.window.showInformationMessage('Hello World from Python-VS Code Bridge!');
    });

    const openDemoCommand = vscode.commands.registerCommand('python-vscode-bridge.openPythonDemo', async () => {
        const demoPath = path.join(context.extensionPath, 'python_demos');
        if (fs.existsSync(demoPath)) {
            const uri = vscode.Uri.file(demoPath);
            await vscode.commands.executeCommand('vscode.openFolder', uri, { forceNewWindow: true });
        } else {
            vscode.window.showErrorMessage('Python demo files not found. Please reinstall the extension.');
        }
    });

    const installDepsCommand = vscode.commands.registerCommand('python-vscode-bridge.installPythonDeps', async () => {
        const terminal = vscode.window.createTerminal('Python Bridge Setup');
        const demoPath = path.join(context.extensionPath, 'python_demos', 'python_client');
        
        terminal.show();
        terminal.sendText(`cd "${demoPath}"`);
        terminal.sendText('pip install -r requirements.txt');
        
        vscode.window.showInformationMessage('Installing Python dependencies. Check the terminal for progress.');
    });

    context.subscriptions.push(helloWorldCommand, openDemoCommand, installDepsCommand);
}

export function deactivate() {
    console.log('Python-VS Code Bridge Extension is now deactivated');
    
    // Stop WebSocket server
    if (webSocketServer) {
        webSocketServer.stop().catch(error => {
            console.error('Error stopping WebSocket server:', error);
        });
        webSocketServer = null;
    }
}