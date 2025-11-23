"""
Exemplo de cliente para testar a API de Agentes para WhatsApp.
Simula o comportamento do Orquestrador ao enviar mensagens e processar respostas.

Baseado na documentação: api-agents-whatsapp/README.md

Uso:
    python test_agents_api.py
"""
import asyncio
import httpx
from datetime import datetime
from typing import Optional

# URL da API local
API_BASE_URL = "http://localhost:5000"


async def test_health_check() -> bool:
    """
    Verifica se a API de Agentes está saudável e pronta.
    """
    print("\n🏥 Verificando saúde da API de Agentes...")
    print("-" * 70)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/health",
                timeout=5.0,
            )
            response.raise_for_status()

            result = response.json()
            print(f"✅ API está saudável! Status: {response.status_code}")
            print(f"\n📊 Informações da API:")
            print(f"  - Status: {result['status']}")
            print(f"  - Serviço: {result['service']}")
            print(f"  - Timestamp: {result['timestamp']}")
            print(f"\n  🔌 Servidores MCP:")
            for server, url in result['mcp_servers'].items():
                print(f"     - {server}: {url}")

            return True

    except httpx.RequestError as e:
        print(f"❌ Erro na requisição: {e}")
        print(f"   💡 Dica: A API não está respondendo. Inicie-a com:")
        print(f"      api-agents")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


async def process_message(
    user_message: str,
    user_id: str,
    session_id: str,
    message_type: str = "text",
    user_preferences: Optional[dict] = None,
) -> Optional[dict]:
    """
    Processa uma mensagem através do agente.
    Simula uma requisição do Orquestrador.

    Args:
        user_message: Mensagem do usuário
        user_id: ID do usuário no WhatsApp (formato: 5585988123456@c.us)
        session_id: ID da sessão de conversa
        message_type: Tipo de mensagem ("text" ou "audio")
        user_preferences: Preferências do usuário (topics, prefer_audio, etc)

    Returns:
        Dict com a resposta do agente ou None se falhar
    """
    payload = {
        "user_message": user_message,
        "user_id": user_id,
        "session_id": session_id,
        "message_type": message_type,
    }

    if user_preferences:
        payload["user_preferences"] = user_preferences

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/process-message",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()

            result = response.json()
            return result

    except httpx.HTTPStatusError as e:
        print(f"❌ Erro HTTP: {e.response.status_code}")
        print(f"   Detalhes: {e.response.text}")
    except httpx.RequestError as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

    return None


async def test_simple_text_message():
    """
    Testa: Mensagem de texto simples sobre legislação.
    
    Scenario: Usuário faz pergunta básica em texto.
    Expected: Resposta textual sem áudio.
    """
    print("\n📝 Teste 1: Mensagem de Texto Simples")
    print("-" * 70)

    user_id = "5585988123456@c.us"
    session_id = "sess_001"
    message = "O que é o Estatuto da Criança e do Adolescente?"

    print(f"👤 Usuário: {user_id}")
    print(f"📨 Mensagem: {message}")
    print(f"📍 Sessão: {session_id}")
    print(f"🎯 Tipo: text")

    result = await process_message(
        user_message=message,
        user_id=user_id,
        session_id=session_id,
        message_type="text",
    )

    if result:
        print(f"\n✅ Resposta recebida!")
        print(f"\n[DEBUG] Conteúdo da resposta:")
        print(result)
        try:
            print(f"\n📤 Response Details:")
            print(f"  - Session: {result['session_id']}")
            print(f"  - User: {result['user_id']}")
            print(f"  - Confiança: {result['confidence']:.2%}")
            print(f"  - Enviar Áudio: {result['should_send_audio']}")
            print(f"  - Timestamp: {result['timestamp']}\n")
            print(f"💬 Resposta do Agente:")
            print(f"   {result['response_text'][:300]}...")

            if result.get('auxiliary_text'):
                print(f"\n📎 Texto Auxiliar:")
                print(f"   {result['auxiliary_text']}")
        except Exception as e:
            print(f"[ERRO] Falha ao acessar campos esperados: {e}")
        return True
    else:
        print(f"❌ Falha ao processar mensagem")
        return False


async def test_message_with_audio_request():
    """
    Testa: Mensagem de áudio com preferência de resposta em áudio.
    
    Scenario: Usuário envia áudio e quer resposta também em áudio.
    Expected: Resposta com should_send_audio=true + auxiliary_text.
    """
    print("\n🎵 Teste 2: Mensagem de Áudio com Preferência de Áudio")
    print("-" * 70)

    user_id = "5585987654321@c.us"
    session_id = "sess_002"
    message = "Fale sobre os projetos de lei mais recentes sobre inteligência artificial"

    print(f"👤 Usuário: {user_id}")
    print(f"📨 Mensagem: {message}")
    print(f"📍 Sessão: {session_id}")
    print(f"🎯 Tipo: audio")

    result = await process_message(
        user_message=message,
        user_id=user_id,
        session_id=session_id,
        message_type="audio",
        user_preferences={
            "prefer_audio": True,
            "topics": ["tecnologia", "inovação"],
        },
    )

    if result:
        print(f"\n✅ Resposta recebida!")
        print(f"\n📤 Response Details:")
        print(f"  - Session: {result['session_id']}")
        print(f"  - User: {result['user_id']}")
        print(f"  - Confiança: {result['confidence']:.2%}")
        print(f"  - ⚠️  Enviar Áudio: {result['should_send_audio']}")
        print(f"  - Timestamp: {result['timestamp']}\n")
        print(f"💬 Resposta do Agente:")
        print(f"   {result['response_text'][:300]}...")

        if result.get('auxiliary_text'):
            print(f"\n📎 Texto Auxiliar (para TTS):")
            print(f"   {result['auxiliary_text']}")
            print(f"\n🎙️  Próximo Passo do Orquestrador:")
            print(f"   1. Enviar response_text para API de Áudio (/text-to-speech)")
            print(f"   2. Receber URL do áudio gerado")
            print(f"   3. Enviar áudio + auxiliary_text para WhatsApp")

        return True
    else:
        print(f"❌ Falha ao processar mensagem")
        return False


async def test_message_with_topics():
    """
    Testa: Mensagem com tópicos de interesse do usuário.
    
    Scenario: Usuário com preferências de tópicos predefinidas.
    Expected: Resposta considerando os tópicos de interesse.
    """
    print("\n🏷️  Teste 3: Mensagem com Tópicos de Interesse")
    print("-" * 70)

    user_id = "5585989999999@c.us"
    session_id = "sess_003"
    message = "Quais projetos estão em votação agora?"

    user_prefs = {
        "topics": ["educação", "saúde", "meio-ambiente"],
        "prefer_audio": False,
    }

    print(f"👤 Usuário: {user_id}")
    print(f"📨 Mensagem: {message}")
    print(f"📍 Sessão: {session_id}")
    print(f"🏷️  Tópicos de Interesse: {', '.join(user_prefs['topics'])}")
    print(f"🎙️  Preferência Áudio: {user_prefs['prefer_audio']}")

    result = await process_message(
        user_message=message,
        user_id=user_id,
        session_id=session_id,
        message_type="text",
        user_preferences=user_prefs,
    )

    if result:
        print(f"\n✅ Resposta recebida!")
        print(f"\n📤 Response Details:")
        print(f"  - Session: {result['session_id']}")
        print(f"  - User: {result['user_id']}")
        print(f"  - Confiança: {result['confidence']:.2%}")
        print(f"  - Enviar Áudio: {result['should_send_audio']}")
        print(f"  - Timestamp: {result['timestamp']}\n")
        print(f"💬 Resposta do Agente (considerando tópicos):")
        print(f"   {result['response_text'][:300]}...")

        return True
    else:
        print(f"❌ Falha ao processar mensagem")
        return False


async def test_multiple_messages_same_session():
    """
    Testa: Múltiplas mensagens na mesma sessão (continuidade).
    
    Scenario: Usuário mantém conversa sobre mesmo tópico.
    Expected: Agente mantém contexto da sessão.
    """
    print("\n💬 Teste 4: Múltiplas Mensagens - Mesma Sessão")
    print("-" * 70)

    user_id = "5585985555555@c.us"
    session_id = "sess_004"

    messages = [
        "Fale sobre projetos de educação",
        "Qual é o mais importante?",
        "Como posso participar?",
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n📨 Mensagem {i}: {message}")
        print(f"📍 Sessão: {session_id} (mesma sessão)")

        result = await process_message(
            user_message=message,
            user_id=user_id,
            session_id=session_id,
            message_type="text",
        )

        if result:
            print(f"✅ Resposta: {result['response_text'][:150]}...")
        else:
            print(f"❌ Falha ao processar")

        await asyncio.sleep(0.5)  # Pequeno delay entre mensagens

    return True


async def test_orchestrator_workflow():
    """
    Testa: Fluxo completo do Orquestrador.
    
    Simula como o Orquestrador utilizaria a API:
    1. Receber mensagem do WhatsApp
    2. Chamar API de Agentes
    3. Determinar se precisa de TTS
    4. Enviar resposta para WhatsApp
    """
    print("\n🔄 Teste 5: Fluxo Completo do Orquestrador")
    print("-" * 70)

    user_id = "5585983333333@c.us"
    session_id = "sess_005"
    user_message = "Explique como funciona o e-Cidadania"

    print("FLUXO DO ORQUESTRADOR:\n")

    # Step 1
    print("1️⃣  [Orquestrador] Recebeu mensagem do WhatsApp")
    print(f"   Usuário: {user_id}")
    print(f"   Mensagem: {user_message}\n")

    # Step 2
    print("2️⃣  [Orquestrador] Chamando API de Agentes...")
    result = await process_message(
        user_message=user_message,
        user_id=user_id,
        session_id=session_id,
        message_type="text",
        user_preferences={"topics": ["cidadania", "participação"]},
    )

    if not result:
        print("❌ Falha ao chamar API de Agentes")
        return False

    print(f"✅ Resposta recebida da API\n")

    # Step 3
    print("3️⃣  [Orquestrador] Analisando resposta...")
    print(f"   - Texto: {result['response_text'][:80]}...")
    print(f"   - Enviar Áudio: {result['should_send_audio']}")
    print(f"   - Confiança: {result['confidence']:.2%}\n")

    # Step 4
    if result['should_send_audio']:
        print("4️⃣  [Orquestrador] Áudio requerido! Fluxo:")
        print(f"   a) POST http://localhost:8001/text-to-speech")
        print(f"      payload: {{text: '{result['response_text'][:50]}...'}}")
        print(f"   b) Receber URL do áudio")
        print(f"   c) Enviar áudio + texto auxiliar para WhatsApp\n")
    else:
        print("4️⃣  [Orquestrador] Resposta por texto")
        print(f"   - POST /send-message no Servidor WhatsApp")
        print(f"   - Enviar: {result['response_text'][:80]}...\n")

    # Step 5
    print("5️⃣  [Orquestrador] Salvar metadados da conversa")
    print(f"   - session_id: {result['session_id']}")
    print(f"   - user_id: {result['user_id']}")
    print(f"   - timestamp: {result['timestamp']}")
    print(f"   - confidence: {result['confidence']}")

    return True


async def main():
    """
    Executa todos os testes da API de Agentes.
    """
    print("\n" + "=" * 70)
    print("🤖 TESTES DA API DE AGENTES PARA WHATSAPP")
    print("=" * 70)
    print("\nEsta aplicação simula o comportamento do Orquestrador ao")
    print("interagir com a API de Agentes.\n")

    # Health check
    is_healthy = await test_health_check()
    if not is_healthy:
        print("\n⚠️  Não foi possível conectar à API. Abortando testes.")
        return

    # Executar testes
    tests = [
        ("Texto Simples", test_simple_text_message),
        ("Áudio com Preferência Áudio", test_message_with_audio_request),
        ("Mensagem com Tópicos", test_message_with_topics),
        ("Múltiplas Mensagens", test_multiple_messages_same_session),
        ("Fluxo Orquestrador", test_orchestrator_workflow),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            await asyncio.sleep(1)  # Delay entre testes
        except Exception as e:
            print(f"\n❌ Erro ao executar teste: {e}")
            results.append((test_name, False))

    # Resumo
    print("\n\n" + "=" * 70)
    print("📋 RESUMO DOS TESTES")
    print("=" * 70)
    for test_name, result in results:
        status = "✅ Sucesso" if result else "❌ Falha"
        print(f"{status:12} - {test_name}")

    print("\n" + "=" * 70)
    print("🎯 PRÓXIMOS PASSOS:")
    print("=" * 70)
    print("1. Implementar Orquestrador que chamar a /process-message")
    print("2. Integrar com API de Áudio (/text-to-speech) se needed")
    print("3. Implementar persistência de sessões (MongoDB/Redis)")
    print("4. Criar sistema de gerenciamento de usuários")
    print("5. Adicionar rate limiting e autenticação")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")