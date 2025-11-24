import { Request, Response } from 'express';
import { RAGService } from '../services/rag.service';
import axios from 'axios';
import { config } from '../config';

export class ChatController {
  private ragService: RAGService;

  constructor() {
    this.ragService = new RAGService();
  }

  async handleChat(req: Request, res: Response) {
    const { message, audioEnabled = true } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    console.log('[Chat Controller] Processing message:', message);
    console.log('[Chat Controller] Audio enabled:', audioEnabled);

    try {
      // SEMPRE usar RAG para perguntas sobre PLs
      const isPLQuery = this.isPLRelatedQuery(message);

      if (!isPLQuery) {
        return res.status(400).json({
          error: 'Este assistente responde apenas perguntas sobre Projetos de Lei (PLs). Por favor, faça uma pergunta sobre um PL específico.',
        });
      }

      // 1. Buscar informação usando RAG
      console.log('[Chat Controller] Querying RAG service...');
      const ragResult = await this.ragService.queryWithRAG(message);

      // 2. Validar se há contexto
      if (!ragResult.hasContext) {
        console.warn('[Chat Controller] No context found for query');
        return res.json({
          text: ragResult.answer,
          audio: audioEnabled ? await this.generateAudio(ragResult.answer) : null,
          sources: [],
          hasContext: false,
        });
      }

      // 3. Formatar resposta para ser idêntica em texto e áudio
      const formattedAnswer = this.ragService.formatAnswerForSpeech(ragResult);

      console.log('[Chat Controller] Formatted answer:', formattedAnswer);

      // 4. Gerar áudio com EXATAMENTE o mesmo conteúdo do texto
      let audioBase64 = null;
      if (audioEnabled) {
        console.log('[Chat Controller] Generating audio...');
        audioBase64 = await this.generateAudio(formattedAnswer);
        console.log('[Chat Controller] Audio generated successfully');
      }

      // 5. Retornar resposta estruturada
      return res.json({
        text: formattedAnswer,
        audio: audioBase64,
        sources: ragResult.sources,
        hasContext: true,
        debug: {
          query: message,
          isPLQuery,
          sourcesFound: ragResult.sources.length,
        },
      });

    } catch (error) {
      console.error('[Chat Controller] Error:', error);
      return res.status(500).json({
        error: 'Erro ao processar mensagem: ' + (error as Error).message,
      });
    }
  }

  private isPLRelatedQuery(message: string): boolean {
    const plKeywords = [
      'pl ', 'projeto de lei', 'projeto',
      'autor', 'autoria', 'status',
      'tramitação', 'votação', 'lei',
      'deputado', 'senador', 'câmara', 'senado'
    ];

    const messageLower = message.toLowerCase();
    return plKeywords.some(keyword => messageLower.includes(keyword));
  }

  private async generateAudio(text: string): Promise<string | null> {
    try {
      console.log('[Chat Controller] Calling audio API...');
      
      const response = await axios.post(
        `${config.audioApiUrl}/synthesize`,
        { text },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 30000,
        }
      );

      if (response.data && response.data.audio_base64) {
        console.log('[Chat Controller] Audio generated successfully');
        return response.data.audio_base64;
      }

      console.warn('[Chat Controller] No audio in response');
      return null;
    } catch (error) {
      console.error('[Chat Controller] Error generating audio:', error);
      return null;
    }
  }
}