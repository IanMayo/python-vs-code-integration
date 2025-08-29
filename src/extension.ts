import * as vscode from 'vscode';
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

    const disposable = vscode.commands.registerCommand('python-vscode-bridge.helloWorld', () => {
        vscode.window.showInformationMessage('Hello World from Python-VS Code Bridge!');
    });

    context.subscriptions.push(disposable);
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