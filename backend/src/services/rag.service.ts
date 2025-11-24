import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';
import { config } from '../config';

interface RAGResult {
  answer: string;
  sources: Array<{
    pl_number: string;
    author: string;
    status: string;
    content: string;
  }>;
  hasContext: boolean;
}

export class RAGService {
  private anthropic: Anthropic;

  constructor() {
    this.anthropic = new Anthropic({
      apiKey: config.anthropicApiKey,
    });
  }

  async queryWithRAG(question: string): Promise<RAGResult> {
    console.log('[RAG Service] Starting query:', question);

    try {
      // SEMPRE usar MCP para buscar documentos relevantes
      const response = await this.anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4096,
        tools: [
          {
            type: 'computer_20241022',
            name: 'computer',
          },
        ],
        messages: [
          {
            role: 'user',
            content: `Você é um assistente especializado em informações sobre Projetos de Lei (PLs) brasileiros.

REGRAS OBRIGATÓRIAS:
1. SEMPRE use o sistema de busca de documentos (MCP) para encontrar informações sobre PLs
2. NUNCA invente ou alucine informações sobre PLs
3. Se não encontrar informações nos documentos, diga claramente "Não encontrei informações sobre este PL"
4. SEMPRE cite o número do PL, autor e status quando disponível
5. Base suas respostas APENAS nos documentos encontrados

Pergunta do usuário: ${question}

Passo 1: Use o MCP para buscar documentos relevantes sobre a pergunta
Passo 2: Analise os documentos encontrados
Passo 3: Responda APENAS com informações dos documentos encontrados

Formato da resposta (JSON):
{
  "answer": "resposta clara e objetiva baseada nos documentos",
  "sources": [
    {
      "pl_number": "número do PL",
      "author": "autor do PL",
      "status": "status atual",
      "content": "trecho relevante do documento"
    }
  ],
  "hasContext": true/false
}`,
          },
        ],
      });

      console.log('[RAG Service] Response:', JSON.stringify(response, null, 2));

      // Validar se há contexto nos documentos
      const hasContext = this.validateContext(response);

      if (!hasContext) {
        console.warn('[RAG Service] No context found in documents');
        return {
          answer: 'Não encontrei informações sobre este Projeto de Lei nos documentos disponíveis. Por favor, verifique o número do PL ou forneça mais detalhes.',
          sources: [],
          hasContext: false,
        };
      }

      // Extrair resposta estruturada
      const result = this.extractStructuredResponse(response);
      
      console.log('[RAG Service] Structured result:', result);
      
      return result;
    } catch (error) {
      console.error('[RAG Service] Error:', error);
      throw new Error('Erro ao consultar documentos: ' + (error as Error).message);
    }
  }

  private validateContext(response: any): boolean {
    // Verificar se a resposta contém referências a documentos reais
    const content = JSON.stringify(response);
    
    // Procurar por padrões que indicam uso de documentos
    const hasDocumentReference = 
      content.includes('pl_number') ||
      content.includes('PL ') ||
      content.includes('Projeto de Lei') ||
      content.includes('author') ||
      content.includes('status');

    return hasDocumentReference;
  }

  private extractStructuredResponse(response: any): RAGResult {
    try {
      // Extrair conteúdo da resposta
      const content = response.content.find((c: any) => c.type === 'text')?.text || '';
      
      // Tentar parsear JSON se estiver presente
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        return {
          answer: parsed.answer || content,
          sources: parsed.sources || [],
          hasContext: parsed.hasContext !== false,
        };
      }

      // Fallback: extrair informações manualmente
      return {
        answer: content,
        sources: [],
        hasContext: true,
      };
    } catch (error) {
      console.error('[RAG Service] Error parsing response:', error);
      return {
        answer: 'Erro ao processar resposta dos documentos.',
        sources: [],
        hasContext: false,
      };
    }
  }

  formatAnswerForSpeech(result: RAGResult): string {
    // Formatar resposta para ser idêntica em texto e áudio
    if (!result.hasContext) {
      return result.answer;
    }

    let speech = result.answer;

    // Adicionar fontes de forma clara
    if (result.sources.length > 0) {
      speech += '\n\nFontes consultadas:\n';
      result.sources.forEach((source, index) => {
        speech += `${index + 1}. ${source.pl_number} - Autor: ${source.author} - Status: ${source.status}\n`;
      });
    }

    return speech;
  }
}
