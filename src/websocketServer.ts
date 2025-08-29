import * as vscode from 'vscode';
import * as WebSocket from 'ws';
import * as http from 'http';

interface GenericMessage {
    command: string;
    params?: any;
}

interface GenericResponse {
    result?: any;
    error?: {
        message: string;
        code: number | string;
    };
}

export class GenericWebSocketServer {
    private server: WebSocket.WebSocketServer | null = null;
    private httpServer: http.Server | null = null;
    private readonly port = 60123;
    private clients: Set<WebSocket> = new Set();
    private healthCheckInterval: NodeJS.Timeout | null = null;

    constructor() {}

    async start(): Promise<void> {
        try {
            // Create HTTP server first to handle port conflicts
            this.httpServer = http.createServer();
            
            // Handle port conflicts
            this.httpServer.on('error', (error: any) => {
                if (error.code === 'EADDRINUSE') {
                    console.error(`Port ${this.port} is already in use`);
                    vscode.window.showErrorMessage(
                        `WebSocket server port ${this.port} is already in use. Please close other applications using this port.`
                    );
                }
                throw error;
            });
            
            await new Promise<void>((resolve, reject) => {
                this.httpServer!.listen(this.port, 'localhost', () => {
                    console.log(`HTTP server listening on port ${this.port}`);
                    resolve();
                });
                this.httpServer!.on('error', reject);
            });

            // Create WebSocket server
            this.server = new WebSocket.WebSocketServer({ 
                server: this.httpServer,
                path: '/'
            });

            this.server.on('connection', (ws: WebSocket, req: http.IncomingMessage) => {
                console.log(`WebSocket client connected from ${req.socket.remoteAddress}`);
                this.clients.add(ws);

                // Set up message handling
                ws.on('message', async (data: Buffer) => {
                    try {
                        const message = data.toString();
                        console.log('Received message:', message);
                        
                        // Try to parse as JSON
                        let response: GenericResponse;
                        
                        try {
                            const parsedMessage: GenericMessage = JSON.parse(message);
                            response = await this.handleCommand(parsedMessage);
                        } catch (jsonError) {
                            // If not valid JSON, treat as raw message (for backward compatibility)
                            response = { result: `Echo: ${message}` };
                        }
                        
                        ws.send(JSON.stringify(response));
                    } catch (error) {
                        console.error('Error handling message:', error);
                        const errorResponse: GenericResponse = {
                            error: {
                                message: error instanceof Error ? error.message : 'Unknown error',
                                code: 500
                            }
                        };
                        ws.send(JSON.stringify(errorResponse));
                    }
                });

                ws.on('close', (code, reason) => {
                    console.log(`WebSocket client disconnected. Code: ${code}, Reason: ${reason}. Remaining clients: ${this.clients.size - 1}`);
                    this.clients.delete(ws);
                });

                ws.on('error', (error) => {
                    console.error('WebSocket client error:', error);
                    this.clients.delete(ws);
                });

                // Send welcome message
                ws.send(JSON.stringify({ result: 'Connected to Python-VS Code Bridge' }));
            });

            this.server.on('error', (error) => {
                console.error('WebSocket server error:', error);
                vscode.window.showErrorMessage(`WebSocket server error: ${error.message}`);
                
                // Attempt to restart the server after a brief delay
                setTimeout(() => {
                    console.log('Attempting to restart WebSocket server...');
                    this.stop().then(() => {
                        return this.start();
                    }).catch((restartError) => {
                        console.error('Failed to restart WebSocket server:', restartError);
                    });
                }, 2000);
            });

            console.log(`Python-VS Code Bridge WebSocket server started on ws://localhost:${this.port}`);
            vscode.window.showInformationMessage(`Python-VS Code Bridge started on port ${this.port}`);
            
            // Start health check logging every 30 seconds
            this.healthCheckInterval = setInterval(() => {
                const isServerRunning = this.server !== null;
                const isHttpServerListening = this.httpServer && this.httpServer.listening;
                console.log(`WebSocket Health Check - Server running: ${isServerRunning}, HTTP listening: ${isHttpServerListening}, Active clients: ${this.clients.size}`);
            }, 30000);

        } catch (error) {
            console.error('Failed to start WebSocket server:', error);
            vscode.window.showErrorMessage(`Failed to start WebSocket server: ${error instanceof Error ? error.message : 'Unknown error'}`);
            throw error;
        }
    }

    async stop(): Promise<void> {
        console.log('Stopping Python-VS Code Bridge WebSocket server...');
        
        // Clear health check interval
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }

        // Close all client connections
        this.clients.forEach(ws => {
            if (ws.readyState === 1) { // WebSocket.OPEN
                ws.close();
            }
        });
        this.clients.clear();

        // Close WebSocket server
        if (this.server) {
            await new Promise<void>((resolve) => {
                this.server!.close(() => {
                    console.log('WebSocket server closed');
                    resolve();
                });
            });
            this.server = null;
        }

        // Close HTTP server
        if (this.httpServer) {
            await new Promise<void>((resolve) => {
                this.httpServer!.close(() => {
                    console.log('HTTP server closed');
                    resolve();
                });
            });
            this.httpServer = null;
        }

        console.log('Python-VS Code Bridge WebSocket server stopped');
    }

    isRunning(): boolean {
        return this.server !== null && this.httpServer !== null;
    }

    private async handleCommand(message: GenericMessage): Promise<GenericResponse> {
        console.log(`Handling command: ${message.command}`);

        try {
            switch (message.command) {
                case 'notify':
                    return await this.handleNotifyCommand(message.params);
                
                case 'get_titles_of_active_editors':
                    return await this.handleGetTitlesCommand();
                
                case 'get_text_from_named_editor':
                    return await this.handleGetTextCommand(message.params);
                
                case 'set_text_of_active_editor':
                    return await this.handleSetTextCommand(message.params);
                    
                default:
                    return {
                        error: {
                            message: `Unknown command: ${message.command}`,
                            code: 400
                        }
                    };
            }
        } catch (error) {
            console.error(`Error handling command ${message.command}:`, error);
            return {
                error: {
                    message: error instanceof Error ? error.message : 'Command execution failed',
                    code: 500
                }
            };
        }
    }

    private async handleNotifyCommand(params: any): Promise<GenericResponse> {
        if (!params || typeof params.message !== 'string') {
            return {
                error: {
                    message: 'notify command requires a "message" parameter of type string',
                    code: 400
                }
            };
        }

        try {
            // Display VS Code notification
            vscode.window.showInformationMessage(params.message);
            
            console.log(`Displayed notification: "${params.message}"`);
            
            return { result: null };
        } catch (error) {
            console.error('Error displaying notification:', error);
            return {
                error: {
                    message: 'Failed to display notification',
                    code: 500
                }
            };
        }
    }

    private async handleGetTitlesCommand(): Promise<GenericResponse> {
        try {
            const openDocs = vscode.workspace.textDocuments;
            const editorTitles = openDocs.map(doc => ({
                title: doc.fileName.split('/').pop() || doc.fileName,
                uri: doc.uri.toString(),
                filename: doc.fileName
            }));

            return { result: editorTitles };
        } catch (error) {
            console.error('Error getting editor titles:', error);
            return {
                error: {
                    message: error instanceof Error ? error.message : 'Failed to get editor titles',
                    code: 500
                }
            };
        }
    }

    private async handleGetTextCommand(params: any): Promise<GenericResponse> {
        if (!params || typeof params.filename !== 'string') {
            return {
                error: {
                    message: 'get_text_from_named_editor command requires a "filename" parameter of type string',
                    code: 400
                }
            };
        }

        try {
            const document = this.findOpenDocument(params.filename);
            if (!document) {
                return {
                    error: {
                        message: `File not found or not open: ${params.filename}`,
                        code: 404
                    }
                };
            }

            const text = document.getText();
            return { result: text };
        } catch (error) {
            console.error('Error getting text from editor:', error);
            return {
                error: {
                    message: error instanceof Error ? error.message : 'Failed to get text from editor',
                    code: 500
                }
            };
        }
    }

    private async handleSetTextCommand(params: any): Promise<GenericResponse> {
        if (!params || typeof params.text !== 'string') {
            return {
                error: {
                    message: 'set_text_of_active_editor command requires a "text" parameter of type string',
                    code: 400
                }
            };
        }

        try {
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                return {
                    error: {
                        message: 'No active editor found',
                        code: 404
                    }
                };
            }

            const document = activeEditor.document;
            const edit = new vscode.WorkspaceEdit();
            edit.replace(
                document.uri,
                new vscode.Range(0, 0, document.lineCount, 0),
                params.text
            );

            await vscode.workspace.applyEdit(edit);
            return { result: null };
        } catch (error) {
            console.error('Error setting text in active editor:', error);
            return {
                error: {
                    message: error instanceof Error ? error.message : 'Failed to set text in active editor',
                    code: 500
                }
            };
        }
    }

    private findOpenDocument(filename: string): vscode.TextDocument | null {
        // Check if already open in editor
        const openDocs = vscode.workspace.textDocuments;
        for (const doc of openDocs) {
            if (doc.fileName.endsWith(filename) || doc.fileName === filename) {
                return doc;
            }
        }

        return null;
    }
}