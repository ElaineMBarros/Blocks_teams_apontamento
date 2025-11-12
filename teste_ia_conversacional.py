"""
🧪 TESTE DA IA CONVERSACIONAL
Script para testar o módulo de conversação com IA
"""

import sys
import os
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from agente_apontamentos import AgenteApontamentos
from bot.ai_conversation import ConversacaoIA


def testar_conversacao():
    """Testa conversação com IA"""
    
    print("\n" + "="*80)
    print("🧪 TESTE DE IA CONVERSACIONAL")
    print("="*80 + "\n")
    
    # Inicializar agente
    print("📊 Inicializando agente...")
    agente = AgenteApontamentos()
    
    if agente.df is None:
        print("❌ Erro: Dados não disponíveis")
        print("Execute: python analise_duracao_trabalho.py")
        return
    
    print(f"✅ Agente inicializado com {len(agente.df)} registros\n")
    
    # Inicializar módulo de conversação
    print("🤖 Inicializando módulo de IA...")
    conversacao = ConversacaoIA(agente)
    
    if conversacao.client:
        print("✅ IA configurada e pronta!")
        print(f"📝 Modelo: {conversacao.model}\n")
    else:
        print("⚠️ IA não configurada - usando modo fallback\n")
    
    # Perguntas de teste
    perguntas_teste = [
        "qual é a média de horas?",
        "quantas horas eu trabalhei no total?",
        "mostre o ranking dos funcionários",
        "tem algum apontamento fora do padrão?",
        "e hoje, quanto já apontei?"
    ]
    
    usuario_teste = "João Silva"
    
    print("="*80)
    print(f"👤 SIMULANDO CONVERSAÇÃO COM: {usuario_teste}")
    print("="*80 + "\n")
    
    for i, pergunta in enumerate(perguntas_teste, 1):
        print(f"{'─'*80}")
        print(f"❓ Pergunta {i}: {pergunta}")
        print(f"{'─'*80}")
        
        try:
            resultado = conversacao.processar_mensagem(pergunta, usuario_teste)
            
            print(f"\n🤖 Resposta:")
            print(resultado.get('resposta', 'Sem resposta'))
            
            if resultado.get('usa_ia'):
                print("\n✨ Processado com IA conversacional")
            else:
                print("\n⚙️ Processado com lógica simples (fallback)")
            
            if resultado.get('dados'):
                print(f"\n📊 Dados retornados: {list(resultado['dados'].keys())}")
            
            print()
            
        except Exception as e:
            print(f"\n❌ Erro: {e}\n")
    
    print("="*80)
    print("✅ TESTE CONCLUÍDO")
    print("="*80 + "\n")
    
    # Mostrar histórico
    if usuario_teste in conversacao.historico_conversas:
        historico = conversacao.historico_conversas[usuario_teste]
        print(f"📝 Histórico mantido: {len(historico)} mensagens")
    
    print("\n💡 DICAS:")
    print("   1. Configure AZURE_OPENAI_* ou OPENAI_API_KEY no .env para ativar IA")
    print("   2. Sem IA configurada, o bot usa processamento de linguagem simples")
    print("   3. Veja IA_CONVERSACIONAL.md para mais detalhes\n")


def testar_modo_interativo():
    """Modo interativo para testar conversação"""
    
    print("\n" + "="*80)
    print("💬 MODO INTERATIVO - IA CONVERSACIONAL")
    print("="*80 + "\n")
    
    # Inicializar
    agente = AgenteApontamentos()
    if agente.df is None:
        print("❌ Dados não disponíveis")
        return
    
    conversacao = ConversacaoIA(agente)
    
    if conversacao.client:
        print("✅ IA ativada!")
    else:
        print("⚠️ IA não configurada - modo fallback")
    
    usuario = input("\n👤 Seu nome: ").strip() or "Usuário Teste"
    
    print(f"\n💬 Olá {usuario}! Faça suas perguntas sobre apontamentos.")
    print("   Digite 'sair' para encerrar\n")
    
    while True:
        try:
            pergunta = input(f"\n{usuario}: ").strip()
            
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Até logo!")
                break
            
            if not pergunta:
                continue
            
            resultado = conversacao.processar_mensagem(pergunta, usuario)
            print(f"\n🤖 Bot: {resultado.get('resposta', 'Sem resposta')}")
            
            if resultado.get('usa_ia'):
                print("   [IA conversacional]")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interativo":
        testar_modo_interativo()
    else:
        testar_conversacao()
        
        print("\n💡 Para modo interativo, execute:")
        print("   python teste_ia_conversacional.py interativo\n")
