"""
API FastAPI para Bot do Microsoft Teams
Endpoint principal para receber e processar mensagens
Versão: 1.0.3 - Single Tenant com permissões configuradas
"""
import sys
import os
from pathlib import Path

# Adicionar path do projeto ao PYTHONPATH para importar agente_apontamentos
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, Attachment
import logging

from bot.config import config
from bot.adaptive_cards import (
    create_welcome_card,
    create_statistics_card,
    create_ranking_card,
    create_user_summary_card,
    create_error_card,
    create_text_card,
    create_outliers_card,
    create_daily_summary_card,
    create_weekly_summary_card,
    create_comparison_card,
    create_help_card
)

# Validar configurações obrigatórias no início
try:
    config.validate()
    print("✅ Configurações validadas com sucesso")
    print(f"   - App ID: {config.BOT_APP_ID[:8]}...")
    print(f"   - Tenant ID: {config.BOT_TENANT_ID[:8]}...")
except ValueError as e:
    print(f"❌ ERRO DE CONFIGURAÇÃO: {e}")
    print("⚠️ Bot não iniciará corretamente sem as variáveis obrigatórias!")

# Importar o agente (módulo já existente)
try:
    from agente_apontamentos import AgenteApontamentos
except ImportError:
    print("⚠️ Aviso: agente_apontamentos.py não encontrado. Bot funcionará em modo limitado.")
    AgenteApontamentos = None

# Importar módulo de conversação com IA
try:
    from bot.ai_conversation import ConversacaoIA
    IA_DISPONIVEL = True
except ImportError:
    print("⚠️ Módulo de IA não disponível")
    ConversacaoIA = None
    IA_DISPONIVEL = False

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variável global para o adapter (será inicializada no lifespan)
adapter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    Inicializa o adapter quando o worker inicia.
    """
    global adapter
    
    logger.info("🚀 Worker iniciando - criando Bot Framework Adapter...")
    logger.info(f"   - Process ID: {os.getpid()}")
    
    try:
        # Configuração básica (funciona com Single e Multi-Tenant)
        # O Tenant ID é configurado no Azure Bot Service, não no código
        bot_settings = BotFrameworkAdapterSettings(
            app_id=config.BOT_APP_ID,
            app_password=config.BOT_APP_PASSWORD
        )
        adapter = BotFrameworkAdapter(bot_settings)
        
        logger.info(f"✅ Bot Framework Adapter criado com sucesso")
        logger.info(f"   - App ID: {config.BOT_APP_ID[:8]}...")
        logger.info(f"   - Worker PID: {os.getpid()}")
    except Exception as e:
        logger.error(f"❌ ERRO ao criar adapter: {e}", exc_info=True)
        adapter = None
    
    yield  # Aplicação roda aqui
    
    # Cleanup ao encerrar
    logger.info(f"🛑 Worker {os.getpid()} encerrando")

# Inicializar FastAPI com lifespan
app = FastAPI(
    title="Agente de Apontamentos Bot API",
    description="API para bot do Microsoft Teams",
    version="0.1.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Agente (será recarregado a cada hot-reload)
def get_agente():
    """Retorna uma instância do agente (para hot-reload)"""
    agente_inst = AgenteApontamentos() if AgenteApontamentos else None
    if agente_inst and agente_inst.df is not None:
        logger.info(f"✅ Agente inicializado com {len(agente_inst.df)} registros")
    elif agente_inst:
        logger.warning("⚠️ Agente inicializado mas sem dados")
    else:
        logger.warning("⚠️ Agente não disponível")
    return agente_inst

agente = get_agente()

# Inicializar módulo de conversação com IA
conversacao_ia = None
if IA_DISPONIVEL and agente:
    try:
        conversacao_ia = ConversacaoIA(agente)
        logger.info("✅ Módulo de conversação IA inicializado")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao inicializar conversação IA: {e}")


async def process_message(turn_context: TurnContext):
    """
    Processa mensagens recebidas do Teams
    """
    try:
        # Obter informações do usuário e conversação
        user_name = turn_context.activity.from_property.name
        conversation_id = turn_context.activity.conversation.id
        
        # Log da sessão
        logger.info(f"🔐 Sessão: {conversation_id[:30]}... | Usuário: {user_name}")
        
        # Obter mensagem do texto ou do botão (value)
        user_message = None
        if turn_context.activity.text:
            user_message = turn_context.activity.text.strip()
        elif turn_context.activity.value and isinstance(turn_context.activity.value, dict):
            # Botão foi clicado - extrair comando do value
            user_message = turn_context.activity.value.get('command', '')
        
        # Se não há mensagem, ignorar (conversationUpdate, etc)
        if not user_message:
            logger.info(f"📨 Evento sem mensagem de {user_name} (tipo: {turn_context.activity.type})")
            return
        
        logger.info(f"📨 Mensagem de {user_name}: {user_message}")
        
        # Mensagens especiais
        if user_message.lower() in ["oi", "olá", "ola", "hello", "hi", "start", "começar", "iniciar"]:
            # Card de boas-vindas
            try:
                card = create_welcome_card()
                attachment = Attachment(
                    content_type="application/vnd.microsoft.card.adaptive",
                    content=card
                )
                reply = Activity(
                    type=ActivityTypes.message,
                    attachments=[attachment]
                )
                await turn_context.send_activity(reply)
                logger.info("✅ Card de boas-vindas enviado")
            except Exception as e:
                logger.error(f"❌ Erro ao enviar card de boas-vindas: {e}")
                # Fallback para mensagem simples
                await turn_context.send_activity("Olá! Bem-vindo ao Bot de Apontamentos. Digite 'ajuda' para ver os comandos disponíveis.")
            return
        
        # Comando de ajuda
        if user_message.lower() in ["ajuda", "help", "comandos", "?"]:
            card = create_help_card()
            attachment = Attachment(
                content_type="application/vnd.microsoft.card.adaptive",
                content=card
            )
            reply = Activity(
                type=ActivityTypes.message,
                attachments=[attachment]
            )
            await turn_context.send_activity(reply)
            return
        
        # Processar com agente (com IA se disponível)
        if agente:
            # Usar IA conversacional se disponível
            if conversacao_ia:
                try:
                    resultado = conversacao_ia.processar_mensagem(user_message, user_name, conversation_id)
                    logger.info(f"✅ Processado com IA conversacional (sessão isolada)")
                except Exception as e:
                    logger.error(f"❌ Erro na IA, usando fallback: {e}")
                    resultado = agente.responder_pergunta(user_message, user_name)
            else:
                resultado = agente.responder_pergunta(user_message, user_name)
            
            # Determinar tipo de card baseado no resultado
            card = None
            tipo = resultado.get('tipo')
            dados = resultado.get('dados', {})
            
            # Tentar detectar tipo baseado nos dados (útil quando IA responde)
            if tipo == 'ia_conversacao' and dados:
                # Identificar tipo pelos dados retornados
                if 'media_horas' in dados:
                    tipo = 'estatistica_geral'
                elif isinstance(dados, dict) and len(dados) > 5 and all(isinstance(v, dict) for v in dados.values()):
                    tipo = 'ranking'
                elif 'total_horas' in dados:
                    tipo = 'total'
                elif 'diferenca' in dados and 'total_atual' in dados:
                    tipo = 'comparacao'
                elif isinstance(dados, list) and len(dados) > 0:
                    tipo = 'outliers'
            
            if tipo == 'estatistica_geral' or tipo == 'estatistica':
                card = create_statistics_card(dados)
            
            elif tipo == 'ranking':
                card = create_ranking_card(dados)
            
            elif tipo == 'usuario_individual':
                card = create_user_summary_card(user_name, dados)
            
            elif tipo == 'dia_atual':
                card = create_daily_summary_card(dados)
            
            elif tipo == 'resumo_semanal':
                card = create_weekly_summary_card(dados)
            
            elif tipo == 'comparacao':
                # Adaptar dados para o card de comparação
                dados_comparacao = {
                    'atual': dados.get('total_atual', 0),
                    'anterior': dados.get('total_anterior', 0),
                    'diferenca': dados.get('diferenca', 0)
                }
                card = create_comparison_card(dados_comparacao)
            
            elif tipo == 'outliers':
                outliers = dados if isinstance(dados, list) else []
                card = create_outliers_card(outliers)
            
            elif tipo == 'periodo':
                # Exibir card de texto com resumo do período
                card = create_text_card("📅 Consulta por Período", resultado.get('resposta', 'Sem resposta'))
            
            elif tipo == 'ajuda':
                card = create_help_card()
            
            elif tipo == 'erro' or tipo == 'info':
                card = create_error_card(resultado.get('resposta', 'Erro desconhecido'))
            
            elif tipo in ['total', 'total_geral']:
                card = create_text_card("⏱️ Total de Horas", resultado.get('resposta', 'Sem resposta'))
            
            else:
                # Card de texto genérico MAS com botões de ação rápida
                resposta = resultado.get('resposta', 'Sem resposta')
                card = create_text_card("💬 Resposta", resposta)
            
            if card:
                attachment = Attachment(
                    content_type="application/vnd.microsoft.card.adaptive",
                    content=card
                )
                reply = Activity(
                    type=ActivityTypes.message,
                    attachments=[attachment]
                )
                await turn_context.send_activity(reply)
            else:
                # Resposta em texto simples
                await turn_context.send_activity(resultado.get('resposta', 'Sem resposta'))
        else:
            # Modo limitado - sem agente
            await turn_context.send_activity(
                "⚠️ Agente temporariamente indisponível. Por favor, tente novamente mais tarde."
            )
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}", exc_info=True)
        
        try:
            # Tentar enviar card de erro
            error_card = create_error_card(
                f"Desculpe, ocorreu um erro ao processar sua solicitação."
            )
            attachment = Attachment(
                content_type="application/vnd.microsoft.card.adaptive",
                content=error_card
            )
            reply = Activity(
                type=ActivityTypes.message,
                attachments=[attachment]
            )
            await turn_context.send_activity(reply)
        except Exception as inner_e:
            logger.error(f"❌ Erro ao enviar mensagem de erro: {inner_e}")
            # Fallback final - mensagem de texto simples
            try:
                await turn_context.send_activity("Desculpe, ocorreu um erro ao processar sua mensagem.")
            except:
                pass  # Se nem isso funcionar, apenas loga


@app.post("/api/messages")
async def messages(request: Request):
    """
    Endpoint principal que recebe mensagens do Microsoft Teams
    """
    if not adapter:
        logger.error("❌ Bot adapter não está configurado")
        raise HTTPException(status_code=500, detail="Bot adapter não configurado")
    
    try:
        # Obter o body da requisição
        body = await request.json()
        logger.debug(f"📥 Recebido body: {body.get('type', 'unknown')}")
        
        # Obter header de autorização
        auth_header = request.headers.get("Authorization", "")
        
        # Criar atividade a partir do body
        activity = Activity().deserialize(body)
        
        # Processar atividade
        async def call_process_message(turn_context: TurnContext):
            await process_message(turn_context)
        
        await adapter.process_activity(activity, auth_header, call_process_message)
        
        return JSONResponse(content={"status": "ok"}, status_code=200)
    
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /api/messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """
    Endpoint raiz - health check
    """
    return {
        "name": config.BOT_NAME,
        "description": config.BOT_DESCRIPTION,
        "version": "0.1.0",
        "status": "running",
        "agente_disponivel": agente is not None,
        "ia_conversacional": conversacao_ia is not None
    }


@app.get("/health")
async def health():
    """
    Health check detalhado
    """
    return {
        "status": "healthy",
        "bot_configured": adapter is not None,
        "agente_available": agente is not None,
        "ia_conversacional_available": conversacao_ia is not None,
        "environment": config.ENVIRONMENT
    }


@app.get("/sessions")
async def get_sessions():
    """
    Endpoint de monitoramento de sessões ativas
    """
    if conversacao_ia and hasattr(conversacao_ia, 'session_manager'):
        sessions_info = conversacao_ia.session_manager.get_all_sessions_info()
        return sessions_info
    return {
        "total_sessions": 0,
        "sessions": [],
        "message": "Session manager não disponível"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Validar configurações antes de iniciar
    try:
        if config.BOT_APP_ID and config.BOT_APP_PASSWORD:
            config.validate()
            logger.info("✅ Configurações validadas")
        else:
            logger.warning("⚠️ Bot rodando sem credenciais - apenas para desenvolvimento")
    except ValueError as e:
        logger.error(f"❌ Erro de configuração: {e}")
        sys.exit(1)
    
    # Iniciar servidor
    logger.info(f"🚀 Iniciando bot na porta {config.PORT}...")
    uvicorn.run(
        "bot_api:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.DEBUG
    )
