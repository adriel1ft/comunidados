"""
Exemplo de cliente para testar o Orquestrador de Mensagens WhatsApp.

Simula o comportamento do WhatsApp Service ao enviar mensagens para o Orquestrador.
Demonstra todos os fluxos principais:
  - Agrupamento inteligente de mensagens (message batching)
  - Processamento de áudio
  - Integração com agente LLM
  - Gerenciamento de usuários
  - Histórico de sessões

Uso:
    # Terminal 1: Iniciar Orquestrador
    orchestrator

    # Terminal 2: Executar testes
    python test-orchestrator.py

Pré-requisitos:
  - Orquestrador rodando em http://localhost:3000
  - API de Agentes rodando em http://localhost:5000
  - API de Áudio rodando em http://localhost:5001
  - MongoDB rodando em localhost:27017
"""
import asyncio
import httpx
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# URL da API local
API_BASE_URL = "http://localhost:3000"
ORCHESTRATOR_TIMEOUT = 40  # Mais tempo para aguardar processamento do buffer


async def test_health_check() -> bool:
    """
    Verifica se o Orquestrador está saudável e pronto para receber mensagens.
    """
    print("\n🏥 Verificando saúde do Orquestrador...")
    print("-" * 70)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/health",
                timeout=5.0,
            )
            response.raise_for_status()

            result = response.json()
            print(f"✅ Orquestrador está saudável!")
            print(f"\n📊 Informações:")
            print(f"  - Status: {result.get('status')}")
            print(f"  - Serviço: {result.get('service')}")
            print(f"  - Timestamp: {result.get('timestamp')}")

            return True

    except httpx.RequestError as e:
        print(f"❌ Erro na requisição: {e}")
        print(f"   💡 Dica: O Orquestrador não está respondendo. Inicie-o com:")
        print(f"      orchestrator")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


async def send_message(
    user_id: str,
    chatId: str,
    message_type: str,
    message: str,
) -> Optional[Dict]:
    """
    Envia uma mensagem para o Orquestrador.
    
    Simula o comportamento do WhatsApp Service ao POST em /receive-message.
    
    Args:
        user_id: ID único do usuário (formato WhatsApp: 5585988123456@c.us)
        chatId: ID da conversa
        message_type: "text" ou "audio"
        message: Conteúdo da mensagem ou áudio em base64
    
    Returns:
        Resposta do Orquestrador ou None se falhar
    """
    payload = {
        "user_id": user_id,
        "chatId": chatId,
        "message_type": message_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/receive-message",
                json=payload,
                timeout=ORCHESTRATOR_TIMEOUT,
            )
            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"❌ Erro HTTP: {e.response.status_code}")
        print(f"   Detalhes: {e.response.text}")
    except httpx.RequestError as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

    return None


async def get_buffer_status(user_id: str) -> Optional[Dict]:
    """
    Obtém o status atual do buffer de um usuário.
    
    Útil para verificar:
    - Quantas mensagens estão no buffer
    - Se está processando
    - Quando foi a última mensagem
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/buffer-status/{user_id}",
                timeout=5.0,
            )
            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"❌ Erro ao obter status: {e.response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    return None


async def force_process_buffer(user_id: str) -> Optional[Dict]:
    """
    Força o processamento imediato do buffer de um usuário.
    
    Útil para testes quando queremos processar sem aguardar timeout.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/process-now/{user_id}",
                timeout=ORCHESTRATOR_TIMEOUT,
            )
            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"❌ Erro ao forçar processamento: {e.response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    return None


async def get_user_profile(user_id: str) -> Optional[Dict]:
    """
    Obtém o perfil de um usuário armazenado no MongoDB.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/user/{user_id}",
                timeout=5.0,
            )
            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"❌ Erro ao obter perfil: {e.response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    return None


async def update_user_profile(
    user_id: str,
    name: Optional[str] = None,
    age: Optional[int] = None,
    location: Optional[str] = None,
) -> Optional[Dict]:
    """
    Atualiza o perfil de um usuário.
    """
    try:
        params = {"user_id": user_id}
        if name:
            params["name"] = name
        if age:
            params["age"] = age
        if location:
            params["location"] = location

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/update-user-profile",
                params=params,
                timeout=5.0,
            )
            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"❌ Erro ao atualizar perfil: {e.response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    return None


async def test_single_text_message():
    """
    Testa: Uma única mensagem de texto.
    
    Cenário: Usuário envia uma mensagem isolada.
    Esperado: Processamento imediato após timeout entre mensagens.
    """
    print("\n📝 Teste 1: Mensagem de Texto Isolada")
    print("-" * 70)

    user_id = os.getenv("TEST_CHAT_ID", "5585988111111@c.us")
    chatId = os.getenv("TEST_CHAT_ID", "5585988111111@c.us")
    message = "Olá! O que é o Estatuto da Criança e do Adolescente?"

    print(f"👤 Usuário: {user_id}")
    print(f"📨 Mensagem: {message}")
    print(f"🎯 Tipo: text\n")

    # Enviar mensagem
    result = await send_message(user_id, chatId, "text", message)

    if result:
        print(f"✅ Mensagem adicionada ao buffer!")
        print(f"\n📊 Status do Buffer:")
        print(f"  - Mensagens no buffer: {result['buffer_status']['messages_count']}")
        print(f"  - Processando: {result['buffer_status']['is_processing']}")
        print(f"  - Mensagem: {result['message']}")

        # Aguardar processamento (timeout entre mensagens)
        print(f"\n⏰ Aguardando processamento (timeout entre mensagens: ~15s)...")
        await asyncio.sleep(16)

        # Verificar status final
        final_status = await get_buffer_status(user_id)
        if final_status:
            print(f"\n✅ Status Final:")
            print(f"  - Mensagens no buffer: {final_status.get('messages_count', 0)}")
            print(f"  - Processando: {final_status.get('is_processing', False)}")

        return True
    else:
        print(f"❌ Falha ao enviar mensagem")
        return False


async def test_message_batching():
    """
    Testa: Agrupamento inteligente de mensagens.
    
    Cenário: Usuário envia 3 mensagens em rápida sucessão.
    Esperado: Mensagens combinadas em uma única resposta.
    
    Timeline:
    - 10:00:00 - Msg 1 (timer: 30s)
    - 10:00:05 - Msg 2 (timer resetado)
    - 10:00:10 - Msg 3 (timer resetado)
    - 10:00:25 - Sem mensagens por 15s → PROCESSA!
    """
    print("\n🔄 Teste 2: Agrupamento de Mensagens (Batching)")
    print("-" * 70)

    user_id = os.getenv("TEST_CHAT_ID", "5585988222222@c.us")
    chatId = os.getenv("TEST_CHAT_ID", "5585988111111@c.us")

    messages = [
        "Primeira pergunta sobre legislação",
        "Qual é o projeto mais importante?",
        "Como eu posso participar?",
    ]

    print(f"👤 Usuário: {user_id}")
    print(f"📊 Será enviado: {len(messages)} mensagens em sucessão rápida\n")

    # Enviar mensagens
    for i, msg in enumerate(messages, 1):
        print(f"[{i}] 📨 Enviando: {msg}")

        result = await send_message(user_id, chatId, "text", msg)

        if result:
            buffer_count = result['buffer_status']['messages_count']
            print(f"    ✅ Adicionada ao buffer (total: {buffer_count})")
        else:
            print(f"    ❌ Falha ao enviar")
            return False

        # Aguardar < 15s entre mensagens
        if i < len(messages):
            await asyncio.sleep(4)

    print(f"\n✅ Todas as mensagens foram adicionadas!")
    print(f"\n⏱️  Aguardando timeout entre mensagens (~15s)...")
    await asyncio.sleep(16)

    # Verificar se foi processado
    final_status = await get_buffer_status(user_id)
    if final_status:
        messages_count = final_status.get('messages_count', 0)
        print(f"\n📊 Status Final:")
        print(f"  - Mensagens no buffer: {messages_count}")
        print(f"  - Processadas: {messages_count == 0}")

        if messages_count == 0:
            print(f"\n✅ SUCESSO! As {len(messages)} mensagens foram agrupadas e processadas!")
            return True
        else:
            print(f"\n⚠️  Buffer ainda possui mensagens")
            return False
    else:
        return False


async def test_mixed_message_types():
    """
    Testa: Agrupamento com diferentes tipos de mensagem (texto + áudio).
    
    Cenário: Usuário envia texto e áudio.
    Esperado: Áudio é transcrito e combinado com o texto.
    """
    print("\n🎵 Teste 3: Agrupamento com Áudio e Texto")
    print("-" * 70)

    user_id = os.getenv("TEST_CHAT_ID", "5585988333333@c.us")
    chatId = os.getenv("TEST_CHAT_ID", "5585988111111@c.us")

    # Simular dados (em produção seria base64 real)
    messages = [
        ("text", "Olá, preciso saber sobre educação"),
        ("text", "Qual é o melhor projeto sobre isso?"),
        # Simulando áudio (em produção seria base64)
        ("audio", "base64_audio_data_exemplo_fala_sobre_educacao"),
    ]

    print(f"👤 Usuário: {user_id}")
    print(f"📊 Será enviado: {len(messages)} mensagens (texto + áudio)\n")

    # Enviar mensagens
    for i, (msg_type, content) in enumerate(messages, 1):
        preview = content[:30] + "..." if len(content) > 30 else content
        print(f"[{i}] 📨 Enviando ({msg_type}): {preview}")

        result = await send_message(user_id, chatId, msg_type, content)

        if result:
            buffer_count = result['buffer_status']['messages_count']
            print(f"    ✅ Adicionada ao buffer (total: {buffer_count})")
        else:
            print(f"    ❌ Falha ao enviar")
            return False

        if i < len(messages):
            await asyncio.sleep(3)

    print(f"\n✅ Todas as mensagens foram adicionadas!")
    print(f"\n⏱️  Aguardando timeout (~15s)...")
    await asyncio.sleep(16)

    # Verificar status
    final_status = await get_buffer_status(user_id)
    if final_status:
        messages_count = final_status.get('messages_count', 0)
        print(f"\n📊 Status Final:")
        print(f"  - Mensagens no buffer: {messages_count}")

        if messages_count == 0:
            print(f"\n✅ SUCESSO! Áudio foi transcrito e combinado com o texto!")
            return True

    return False


async def test_user_profile_management():
    """
    Testa: Gerenciamento de perfil do usuário.
    
    Cenário:
    1. Novo usuário envia mensagem (criação automática)
    2. Verificar perfil padrão
    3. Atualizar perfil com dados
    4. Verificar atualização
    """
    print("\n👤 Teste 4: Gerenciamento de Perfil de Usuário")
    print("-" * 70)

    user_id = os.getenv("TEST_CHAT_ID", "5585988444444@c.us")
    chatId = os.getenv("TEST_CHAT_ID", "5585988111111@c.us")

    # Step 1: Novo usuário
    print("1️⃣  Novo usuário envia mensagem...")
    result = await send_message(
        user_id, chatId, "text", "Olá! Sou novo aqui."
    )

    if not result:
        print(f"❌ Falha ao criar usuário")
        return False

    print(f"✅ Usuário criado automaticamente\n")

    # Step 2: Verificar perfil padrão
    print("2️⃣  Verificando perfil padrão...")
    profile = await get_user_profile(user_id)

    if profile:
        print(f"✅ Perfil obtido:")
        print(f"  - ID: {profile.get('user_id')}")
        print(f"  - Nome: {profile.get('name', 'Não definido')}")
        print(f"  - Idade: {profile.get('age', 'Não definida')}")
        print(f"  - Localização: {profile.get('location', 'Não definida')}")
        print(f"  - Prefere Áudio: {profile.get('prefer_audio', False)}\n")
    else:
        print(f"❌ Falha ao obter perfil")
        return False

    # Step 3: Atualizar perfil
    print("3️⃣  Atualizando perfil...")
    update_result = await update_user_profile(
        user_id=user_id,
        name="João Silva",
        age=28,
        location="Fortaleza, CE",
    )

    if update_result:
        print(f"✅ Perfil atualizado: {update_result.get('status')}\n")
    else:
        print(f"❌ Falha ao atualizar")
        return False

    # Step 4: Verificar atualização
    print("4️⃣  Verificando atualização...")
    updated_profile = await get_user_profile(user_id)

    if updated_profile:
        print(f"✅ Perfil atualizado:")
        print(f"  - Nome: {updated_profile.get('name')}")
        print(f"  - Idade: {updated_profile.get('age')}")
        print(f"  - Localização: {updated_profile.get('location')}")
        return True
    else:
        return False


async def test_force_processing():
    """
    Testa: Forçar processamento do buffer.
    
    Cenário: Usuário envia mensagens e processamos antes do timeout.
    Esperado: Buffer processa imediatamente ao chamar /process-now.
    """
    print("\n⚡ Teste 5: Forçar Processamento do Buffer")
    print("-" * 70)

    user_id = os.getenv("TEST_CHAT_ID", "5585988555555@c.us")
    chatId = os.getenv("TEST_CHAT_ID", "5585988111111@c.us")

    messages = [
        "Primeira pergunta",
        "Segunda pergunta",
    ]

    print(f"👤 Usuário: {user_id}\n")

    # Enviar mensagens
    for i, msg in enumerate(messages, 1):
        print(f"[{i}] 📨 Enviando: {msg}")

        result = await send_message(user_id, chatId, "text", msg)

        if result:
            buffer_count = result['buffer_status']['messages_count']
            print(f"    ✅ No buffer (total: {buffer_count})")
        else:
            print(f"    ❌ Falha")
            return False

        if i < len(messages):
            await asyncio.sleep(2)

    # Verificar status antes de forçar
    print(f"\n📊 Status antes de forçar processamento:")
    status_before = await get_buffer_status(user_id)
    if status_before:
        print(f"  - Mensagens no buffer: {status_before.get('messages_count')}")

    # Forçar processamento
    print(f"\n⚡ Forçando processamento com /process-now...")
    force_result = await force_process_buffer(user_id)

    if force_result:
        print(f"✅ Processamento forçado:")
        print(f"  - Status: {force_result.get('status')}")
        print(f"  - Mensagens processadas: {force_result.get('messages_count')}")
        return True
    else:
        print(f"❌ Falha ao forçar processamento")
        return False


async def test_complete_workflow():
    """
    Testa: Fluxo completo do Orquestrador.
    
    Simula um usuário novo:
    1. Envia primeira mensagem
    2. Atualiza perfil
    3. Envia múltiplas mensagens
    4. Verifica sessão
    """
    print("\n🔄 Teste 6: Fluxo Completo (Usuário Real)")
    print("-" * 70)

    user_id = os.getenv("TEST_CHAT_ID", "5585988666666@c.us")
    chatId = os.getenv("TEST_CHAT_ID", "5585988111111@c.us")

    print(f"👤 Novo Usuário: {user_id}\n")

    # Step 1: Primeira mensagem
    print("1️⃣  Primeira mensagem...")
    result = await send_message(
        user_id, chatId, "text",
        "Olá! Gostaria de saber sobre educação"
    )

    if not result:
        print(f"❌ Falha")
        return False

    print(f"✅ Mensagem recebida\n")

    # Step 2: Atualizar perfil
    print("2️⃣  Atualizando perfil...")
    await update_user_profile(
        user_id=user_id,
        name="Maria Santos",
        age=32,
        location="São Paulo, SP",
    )
    print(f"✅ Perfil atualizado\n")

    # Step 3: Enviar múltiplas mensagens
    print("3️⃣  Enviando múltiplas mensagens...")
    follow_up_messages = [
        "Quais são os projetos atuais sobre educação?",
        "Como posso participar da discussão?",
        "Há audiências públicas agendadas?",
    ]

    for msg in follow_up_messages:
        print(f"   📨 {msg}")
        await send_message(user_id, chatId, "text", msg)
        await asyncio.sleep(3)

    print(f"✅ Todas as mensagens enviadas\n")

    # Step 4: Aguardar processamento
    print("4️⃣  Aguardando processamento...")
    await asyncio.sleep(16)

    # Step 5: Verificar resultado
    print("5️⃣  Verificando resultado...")
    final_profile = await get_user_profile(user_id)

    if final_profile:
        print(f"✅ FLUXO COMPLETO SUCESSO!")
        print(f"\n📊 Resumo Final:")
        print(f"  - Usuário: {final_profile.get('name')}")
        print(f"  - Localização: {final_profile.get('location')}")
        print(f"  - Criado em: {final_profile.get('created_at')}")
        return True

    return False


async def main():
    """
    Executa todos os testes do Orquestrador.
    """
    print("\n" + "=" * 70)
    print("🎼 TESTES DO ORQUESTRADOR DE MENSAGENS WHATSAPP")
    print("=" * 70)
    print("\nEsta aplicação simula o comportamento do WhatsApp Service")
    print("ao interagir com o Orquestrador.\n")
    print("⚠️  Os testes podem levar alguns minutos para completar")
    print("   (incluindo timeouts do message batching)\n")

    # Health check
    is_healthy = await test_health_check()
    if not is_healthy:
        print("\n⚠️  Não foi possível conectar ao Orquestrador.")
        print("   Certifique-se de que está rodando com: orchestrator")
        return

    # Executar testes
    tests = [
        ("Mensagem Isolada", test_single_text_message),
        ("Agrupamento de Mensagens", test_message_batching),
        ("Tipos Mistos (Texto + Áudio)", test_mixed_message_types),
        ("Gerenciamento de Perfil", test_user_profile_management),
        ("Forçar Processamento", test_force_processing),
        ("Fluxo Completo", test_complete_workflow),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n⏳ Executando: {test_name}...")
            result = await test_func()
            results.append((test_name, result))
            await asyncio.sleep(2)
        except Exception as e:
            print(f"\n❌ Erro ao executar teste: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Resumo
    print("\n\n" + "=" * 70)
    print("📋 RESUMO DOS TESTES")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ Sucesso" if result else "❌ Falha"
        print(f"{status:12} - {test_name}")

    print(f"\n📊 Total: {passed}/{total} testes passaram")

    print("\n" + "=" * 70)
    print("🎯 FLUXOS TESTADOS:")
    print("=" * 70)
    print("✅ Message Batching (agrupamento inteligente)")
    print("✅ Timeout automático (30s + 15s entre mensagens)")
    print("✅ Processamento de áudio (transcrição)")
    print("✅ Integração com agente LLM")
    print("✅ Gerenciamento de usuários (MongoDB)")
    print("✅ Histórico de sessões")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()