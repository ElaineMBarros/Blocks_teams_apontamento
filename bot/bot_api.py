"""
API FastAPI para Bot do Microsoft Teams
Endpoint principal para receber e processar mensagens
"""
import sys
import os
from pathlib import Path

# Adicionar path do projeto ao PYTHONPATH para importar agente_apontamentos
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
    create_outliers_card
)

# Importar o agente (módulo já existente)
try:
    from agente_apontamentos import AgenteApontamentos
except ImportError:
    print("⚠️ Aviso: agente_apontamentos.py não encontrado. Bot funcionará em modo limitado.")
    AgenteApontamentos = None

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Agente de Apontamentos Bot API",
    description="API para bot do Microsoft Teams",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Bot Framework Adapter
try:
    bot_settings = BotFrameworkAdapterSettings(
        app_id=config.BOT_APP_ID,
        app_password=config.BOT_APP_PASSWORD
    )
    adapter = BotFrameworkAdapter(bot_settings)
    logger.info("✅ Bot Framework Adapter configurado")
except Exception as e:
    logger.error(f"❌ Erro ao configurar Bot Adapter: {e}")
    adapter = None

# Inicializar Agente
agente = AgenteApontamentos() if AgenteApontamentos else None
if agente:
    logger.info("✅ Agente de Apontamentos inicializado")
else:
    logger.warning("⚠️ Agente não disponível - modo limitado")


async def process_message(turn_context: TurnContext):
    """
    Processa mensagens recebidas do Teams
    """
    try:
        # Obter informações do usuário
        user_name = turn_context.activity.from_property.name
        user_message = turn_context.activity.text.strip()
        
        logger.info(f"📨 Mensagem de {user_name}: {user_message}")
        
        # Mensagens especiais
        if user_message.lower() in ["oi", "olá", "ola", "hello", "hi"]:
            # Card de boas-vindas
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
            return
        
        # Processar com agente se disponível
        if agente:
            resultado = agente.responder_pergunta(user_message, user_name)
            
            # Determinar tipo de card baseado no resultado
            card = None
            if resultado.get('tipo') == 'estatistica_geral':
                card = create_statistics_card(resultado.get('dados', {}))
            elif resultado.get('tipo') == 'ranking':
                card = create_ranking_card(resultado.get('dados', {}))
            elif resultado.get('tipo') == 'usuario_individual':
                card = create_user_summary_card(user_name, resultado.get('dados', {}))
            elif resultado.get('tipo') == 'outliers':
                outliers = resultado.get('dados', [])
                card = create_outliers_card(outliers)
            elif resultado.get('tipo') == 'erro':
                card = create_error_card(resultado.get('resposta', 'Erro desconhecido'))
            else:
                # Card de texto genérico
                card = create_text_card("📊 Resultado", resultado.get('resposta', 'Sem resposta'))
            
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
        
        error_card = create_error_card(
            f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"
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


@app.post("/api/messages")
async def messages(request: Request):
    """
    Endpoint principal que recebe mensagens do Microsoft Teams
    """
    if not adapter:
        raise HTTPException(status_code=500, detail="Bot adapter não configurado")
    
    try:
        # Obter o body da requisição
        body = await request.json()
        
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
        "agente_disponivel": agente is not None
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
        "environment": config.ENVIRONMENT
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
