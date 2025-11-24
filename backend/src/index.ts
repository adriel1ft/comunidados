import express, { Request, Response } from 'express';
import cors from 'cors';
import { ChatController } from './controllers/chat.controller';
import { config } from './config';

const app = express();
const chatController = new ChatController();

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Logging middleware
app.use((req: Request, res: Response, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', service: 'backend', timestamp: new Date().toISOString() });
});

// Chat endpoint
app.post('/api/chat', async (req: Request, res: Response) => {
  await chatController.handleChat(req, res);
});

// Error handler
app.use((err: Error, req: Request, res: Response, next: any) => {
  console.error('[Error]', err);
  res.status(500).json({ error: 'Internal server error', message: err.message });
});

// Start server
app.listen(config.port, config.host, () => {
  console.log(`🚀 Backend rodando em http://${config.host}:${config.port}`);
  console.log(`📡 MCP Projetos Lei: ${config.mcpProjetosLeiUrl}`);
  console.log(`🎵 Audio API: ${config.audioApiUrl}`);
});