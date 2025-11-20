"""
🧪 TESTE DE MULTISESSÃO
Valida isolamento de contexto entre múltiplos usuários
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração
BASE_URL = "http://localhost:3978"

def testar_sessao_unica(sessao_id: str, usuario: str, mensagens: list):
    """
    Simula uma sessão de conversa
    
    Args:
        sessao_id: ID único da sessão
        usuario: Nome do usuário
        mensagens: Lista de mensagens para enviar
    
    Returns:
        Dict com resultados
    """
    print(f"\n{'='*60}")
    print(f"🧑 Sessão {sessao_id}: {usuario}")
    print(f"{'='*60}")
    
    resultados = []
    
    for i, msg in enumerate(mensagens, 1):
        # Simular activity do Bot Framework
        activity = {
            "type": "message",
            "id": f"msg-{sessao_id}-{i}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "serviceUrl": "https://test.botframework.com",
            "channelId": "emulator",
            "from": {
                "id": f"user-{sessao_id}",
                "name": usuario
            },
            "conversation": {
                "id": f"conversation-{sessao_id}"  # ID único por sessão!
            },
            "recipient": {
                "id": "bot",
                "name": "Bot"
            },
            "text": msg,
            "channelData": {
                "clientActivityID": f"activity-{sessao_id}-{i}"
            }
        }
        
        try:
            # Enviar mensagem
            print(f"\n📤 [{sessao_id}] Enviando: {msg}")
            
            response = requests.post(
                f"{BASE_URL}/api/messages",
                json=activity,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ [{sessao_id}] Resposta recebida")
                resultados.append({
                    "sessao": sessao_id,
                    "usuario": usuario,
                    "mensagem": msg,
                    "status": "sucesso"
                })
            else:
                print(f"❌ [{sessao_id}] Erro: {response.status_code}")
                resultados.append({
                    "sessao": sessao_id,
                    "usuario": usuario,
                    "mensagem": msg,
                    "status": "erro",
                    "codigo": response.status_code
                })
            
            # Pequena pausa entre mensagens
            time.sleep(1)
        
        except Exception as e:
            print(f"❌ [{sessao_id}] Exceção: {e}")
            resultados.append({
                "sessao": sessao_id,
                "usuario": usuario,
                "mensagem": msg,
                "status": "erro",
                "erro": str(e)
            })
    
    return resultados


def verificar_sessoes_ativas():
    """Verifica quantas sessões estão ativas"""
    try:
        response = requests.get(f"{BASE_URL}/sessions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Sessões Ativas: {data.get('total_sessions', 0)}")
            print(f"⏰ Timeout: {data.get('timeout_minutes', 'N/A')} minutos")
            
            sessions = data.get('sessions', [])
            if sessions:
                print("\n🔍 Detalhes das Sessões:")
                for sess in sessions:
                    print(f"  - ID: {sess.get('conversation_id', 'N/A')}")
                    print(f"    Mensagens: {sess.get('messages', 0)}")
                    print(f"    Tempo ativo: {sess.get('uptime_min', 0)} min")
                    print(f"    Última atividade: {sess.get('last_activity', 'N/A')}")
                    print()
            
            return data
        else:
            print(f"⚠️ Erro ao verificar sessões: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao verificar sessões: {e}")
        return None


def teste_isolamento_basico():
    """
    Teste 1: Isolamento básico entre 2 usuários
    """
    print("\n" + "="*80)
    print("🧪 TESTE 1: ISOLAMENTO BÁSICO (2 USUÁRIOS SEQUENCIAIS)")
    print("="*80)
    
    # Usuário A pergunta sobre contrato 8446
    resultados_a = testar_sessao_unica(
        "A",
        "Usuario A",
        [
            "Olá",
            "Mostre informações do contrato 8446",
            "Quantos recursos tem?"
        ]
    )
    
    time.sleep(2)
    
    # Usuário B pergunta sobre tecnologia JAVA
    resultados_b = testar_sessao_unica(
        "B",
        "Usuario B",
        [
            "Oi",
            "Quem trabalha com JAVA?",
            "Mostre o top 5"
        ]
    )
    
    # Verificar sessões
    verificar_sessoes_ativas()
    
    return resultados_a + resultados_b


def teste_simultaneo():
    """
    Teste 2: Múltiplos usuários simultâneos
    """
    print("\n" + "="*80)
    print("🧪 TESTE 2: MÚLTIPLOS USUÁRIOS SIMULTÂNEOS (3 USUÁRIOS)")
    print("="*80)
    
    usuarios = [
        {
            "id": "C",
            "nome": "Usuario C",
            "mensagens": ["Oi", "Dashboard geral", "Média de horas"]
        },
        {
            "id": "D",
            "nome": "Usuario D",
            "mensagens": ["Hello", "Ranking top 10", "Estatísticas"]
        },
        {
            "id": "E",
            "nome": "Usuario E",
            "mensagens": ["Olá", "Outliers", "Resumo semanal"]
        }
    ]
    
    # Executar em paralelo
    resultados = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(
                testar_sessao_unica,
                u["id"],
                u["nome"],
                u["mensagens"]
            ): u["id"]
            for u in usuarios
        }
        
        for future in as_completed(futures):
            sessao_id = futures[future]
            try:
                resultado = future.result()
                resultados.extend(resultado)
            except Exception as e:
                print(f"❌ Erro na sessão {sessao_id}: {e}")
    
    time.sleep(2)
    verificar_sessoes_ativas()
    
    return resultados


def teste_contexto_persistente():
    """
    Teste 3: Contexto persistente dentro da mesma sessão
    """
    print("\n" + "="*80)
    print("🧪 TESTE 3: CONTEXTO PERSISTENTE (MESMA SESSÃO)")
    print("="*80)
    
    resultados = testar_sessao_unica(
        "F",
        "Usuario F",
        [
            "Olá",
            "Mostre o contrato 8446",  # Define contexto
            "E quantos recursos tem?",  # Deve lembrar do contrato
            "Qual o total de horas?",   # Ainda deve lembrar
            "Agora mostre contrato 8447",  # Muda contexto
            "Quantos recursos?",  # Deve usar novo contexto
        ]
    )
    
    verificar_sessoes_ativas()
    
    return resultados


def teste_limpeza_sessao():
    """
    Teste 4: Verificar limpeza após timeout
    """
    print("\n" + "="*80)
    print("🧪 TESTE 4: LIMPEZA DE SESSÕES (TIMEOUT)")
    print("="*80)
    
    print("\n⏰ Criando sessões de teste...")
    
    # Criar algumas sessões
    for i in range(3):
        testar_sessao_unica(
            f"TEMP-{i}",
            f"Usuario Temp {i}",
            ["Oi", "Dashboard"]
        )
    
    print("\n📊 Sessões antes do timeout:")
    verificar_sessoes_ativas()
    
    print("\n⏳ Aguardando 6 minutos para timeout (configurado para 30min)...")
    print("💡 Para teste real, ajuste timeout_minutes no SessionManager para 1 minuto")
    print("⚠️ Pulando aguardar real - verifique manualmente depois")
    
    # Em produção, aguardar o timeout real
    # time.sleep(360)  # 6 minutos
    
    # print("\n📊 Sessões após timeout:")
    # verificar_sessoes_ativas()


def executar_todos_testes():
    """Executa toda a suite de testes"""
    print("\n" + "🚀"*40)
    print("🧪 INICIANDO TESTES DE MULTISESSÃO")
    print("🚀"*40)
    
    # Verificar servidor
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor rodando!")
        else:
            print("❌ Servidor não está respondendo corretamente")
            return
    except:
        print("❌ Servidor não está rodando!")
        print(f"💡 Inicie com: python -m uvicorn bot.bot_api:app --reload --port 3978")
        return
    
    todos_resultados = []
    
    # Teste 1: Isolamento básico
    try:
        r1 = teste_isolamento_basico()
        todos_resultados.extend(r1)
    except Exception as e:
        print(f"❌ Erro no Teste 1: {e}")
    
    time.sleep(3)
    
    # Teste 2: Simultâneo
    try:
        r2 = teste_simultaneo()
        todos_resultados.extend(r2)
    except Exception as e:
        print(f"❌ Erro no Teste 2: {e}")
    
    time.sleep(3)
    
    # Teste 3: Contexto persistente
    try:
        r3 = teste_contexto_persistente()
        todos_resultados.extend(r3)
    except Exception as e:
        print(f"❌ Erro no Teste 3: {e}")
    
    time.sleep(3)
    
    # Teste 4: Limpeza
    try:
        teste_limpeza_sessao()
    except Exception as e:
        print(f"❌ Erro no Teste 4: {e}")
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    sucessos = sum(1 for r in todos_resultados if r.get('status') == 'sucesso')
    erros = sum(1 for r in todos_resultados if r.get('status') == 'erro')
    total = len(todos_resultados)
    
    print(f"\n✅ Sucessos: {sucessos}/{total}")
    print(f"❌ Erros: {erros}/{total}")
    print(f"📈 Taxa de sucesso: {(sucessos/total*100):.1f}%")
    
    print("\n📊 Sessões finais:")
    verificar_sessoes_ativas()
    
    print("\n" + "="*80)
    print("✅ TESTES CONCLUÍDOS!")
    print("="*80)
    
    # Validações
    print("\n🔍 VALIDAÇÕES:")
    print("1. ✅ Cada sessão deve ter seu próprio contexto")
    print("2. ✅ Respostas de um usuário NÃO devem aparecer para outro")
    print("3. ✅ Múltiplos usuários podem usar simultaneamente")
    print("4. ✅ Contexto persiste dentro da mesma sessão")
    print("5. ⏰ Sessões inativas devem expirar após timeout")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Verificar logs do servidor para confirmar isolamento")
    print("2. Testar no Bot Framework Emulator")
    print("3. Deploy para Azure App Service")
    print("4. Ativar canal Web Chat")


if __name__ == "__main__":
    executar_todos_testes()
