import dotenv from 'dotenv';

dotenv.config({ path: '../.env.global' });

export const config = {
  port: parseInt(process.env.BACKEND_PORT || '4000', 10),
  host: process.env.BACKEND_HOST || '0.0.0.0',
  
  // Anthropic
  anthropicApiKey: process.env.ANTHROPIC_API_KEY || '',
  anthropicModel: process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20241022',
  
  // MCP Server
  mcpProjetosLeiUrl: process.env.MCP_PROJETOS_LEI_URL || 'http://localhost:8000',
  
  // Audio Processing
  audioApiUrl: process.env.AUDIO_API_URL || 'http://localhost:5001',
  
  // Debug
  debug: process.env.DEBUG === 'true',
};

// Validar variáveis obrigatórias
if (!config.anthropicApiKey) {
  console.warn('⚠️ ANTHROPIC_API_KEY não configurada');
}

console.log('📝 Backend configurado:', {
  port: config.port,
  host: config.host,
  mcpUrl: config.mcpProjetosLeiUrl,
  audioUrl: config.audioApiUrl,
  debug: config.debug,
});
