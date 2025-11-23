import axios from "axios";

export class MessageHandlers {
  constructor(config = {}) {
    // A URL do orquestrador é a única dependência externa necessária.
    this.orchestratorUrl = config.orchestratorUrl;
    console.log("[Config] URL do Orquestrador:", this.orchestratorUrl);

    if (!this.orchestratorUrl) {
      console.warn("[Aviso] URL do orquestrador não definida. As mensagens recebidas não serão processadas.");
    }
  }

  /**
   * Configura os listeners de eventos no cliente do WhatsApp.
   * @param {wwebjs.Client} whatsappClient - O cliente inicializado do whatsapp-web.js.
   */
  setup(whatsappClient) {
    whatsappClient.on("message", async (msg) => {
      // Ignora mensagens de status ou chamadas
      if (msg.type === 'e2e_notification' || msg.type === 'call_log') {
        return;
      }
      
      try {
        const contact = await msg.getContact();
        const chat = await msg.getChat();

        const payload = {
          messageId: msg.id.id,
          from: msg.from,
          to: msg.to,
          author: msg.author, // Undefined se não for em grupo
          body: msg.body,
          type: msg.type,
          timestamp: msg.timestamp,
          isGroup: chat.isGroup,
          sender: {
            id: contact.id._serialized,
            name: contact.name || contact.pushname,
            shortName: contact.shortName,
            isMe: contact.isMe,
            isUser: contact.isUser,
            isGroup: contact.isGroup,
          }
        };

        // Se for mídia, adiciona a informação para o orquestrador decidir o que fazer
        if (msg.hasMedia) {
          try {
            const media = await msg.downloadMedia();
            
            payload.media = {
              mimetype: media.mimetype || this._guessAudioMimetype(msg.type),
              filename: media.filename || `${msg.type}_${msg.id.id}`,
              // Armazena dados em base64 se necessário, ou URL se disponível
              data: media.data, // base64
              size: media.data?.length || 0,
            };

            console.log(`[📥 Mídia Processada] Tipo: ${payload.media.mimetype}, Tamanho: ${payload.media.size} bytes`);
          } catch (mediaError) {
            console.warn("[⚠️  Aviso] Falha ao baixar mídia, enviando apenas metadados:", mediaError.message);
            payload.media = {
              mimetype: this._guessAudioMimetype(msg.type),
              filename: undefined,
              error: "Falha ao processar mídia",
            };
          }
        }
        
        console.log(`[📨 Mensagem Recebida] De: ${payload.sender.name} (${payload.sender.id}). Tipo: ${payload.type}.`);
        console.log(`[Mensagem]: ${payload.body}`);
        console.log(payload);
        await this._forwardToOrchestrator(payload);

      } catch (error) {
        console.error("[❌ Erro] Falha ao processar e encaminhar mensagem:", error);
      }
    });

    whatsappClient.on("ready", () => {
      console.log("[✅] Handlers prontos para receber mensagens.");
    });
  }
  
  _guessAudioMimetype(msgType) {
    const mimeMap = {
      'ptt': 'audio/ogg; codecs=opus',      // Audio PTT padrão do WhatsApp
      'audio': 'audio/mpeg',                // Áudio genérico
      'voice': 'audio/ogg; codecs=opus',
      'image': 'image/jpeg',
      'video': 'video/mp4',
      'document': 'application/octet-stream',
    };
    
    return mimeMap[msgType] || 'application/octet-stream';
  }

  /**
   * Encaminha a mensagem recebida para a API orquestradora.
   * @param {object} payload - Os dados da mensagem a serem enviados.
   */
  async _forwardToOrchestrator(payload) {
    if (!this.orchestratorUrl){
        console.warn("[Aviso] URL do orquestrador não definida. Ignorando encaminhamento da mensagem.");
        return;
    }

    try {
      await axios.post(this.orchestratorUrl, payload, {
        timeout: 10000, // 10 segundos de timeout
        headers: { "Content-Type": "application/json" }
      });
      console.log(`[🚀 Encaminhado] Mensagem ${payload.messageId} enviada para o orquestrador.`);
    } catch (error) {
      console.error(`[❌ Webhook] Erro ao enviar para o orquestrador (${this.orchestratorUrl}):`, error.message);
    }
  }
}