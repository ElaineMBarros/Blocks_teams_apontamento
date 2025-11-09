# 🤖 Guia de Integração - Agente de Apontamentos no Microsoft Teams

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura da Solução](#arquitetura-da-solução)
3. [Requisitos](#requisitos)
4. [Implementação Passo a Passo](#implementação-passo-a-passo)
5. [Exemplos de Uso](#exemplos-de-uso)
6. [Manutenção e Atualização](#manutenção-e-atualização)

---

## 🎯 Visão Geral

Este guia explica como integrar o **Agente Inteligente de Apontamentos** ao Microsoft Teams, permitindo que os funcionários consultem seus dados de apontamento através de um chat conversacional.

### Funcionalidades Principais

✅ Consultas em linguagem natural  
✅ Estatísticas personalizadas por usuário  
✅ Rankings e comparações  
✅ Detecção automática de outliers  
✅ Resumos temporais (dia, semana, mês)  
✅ Integração com autenticação do Teams  

---

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────┐
│                     MICROSOFT TEAMS                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Bot App (Teams Bot Framework)              │   │
│  │  • Recebe mensagens dos usuários                    │   │
│  │  • Obtém contexto do usuário (nome, email)          │   │
│  │  • Formata respostas em Adaptive Cards              │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │
                      │ HTTPS/REST API
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              AZURE FUNCTION APP / WEB APP                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         API Flask/FastAPI                            │   │
│  │  • Endpoint: /api/chat                              │   │
│  │  • Autentica usuário                                │   │
│  │  • Processa mensagem                                │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              AGENTE APONTAMENTOS (Python)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    agente_apontamentos.py                            │   │
│  │  • Interpreta pergunta                              │   │
│  │  • Consulta dados                                   │   │
│  │  • Gera resposta                                    │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              MICROSOFT FABRIC DATA WAREHOUSE                │
│  • Tabela: gold_999_portal_outsourcing_apontamento_...     │
│  • Dados atualizados automaticamente                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Requisitos

### 1. Registro do Bot no Azure

```bash
# Criar App Registration no Azure AD
az ad app create \
  --display-name "Agente Apontamentos Bot" \
  --available-to-other-tenants false
```

### 2. Dependências Python

```bash
pip install -r requirements_teams.txt
```

**requirements_teams.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
botbuilder-core==4.15.0
botbuilder-schema==4.15.0
aiohttp==3.9.0
pandas==2.1.3
numpy==1.26.2
python-dotenv==1.0.0
```

### 3. Credenciais e Configuração

Criar arquivo `.env`:
```env
# Azure Bot Service
BOT_APP_ID=seu-app-id
BOT_APP_PASSWORD=seu-app-password
BOT_TENANT_ID=3a78b0cd-7c8e-4929-83d5-190a6cc01365

# Microsoft Fabric
FABRIC_ENDPOINT=seu-endpoint.datawarehouse.fabric.microsoft.com
FABRIC_DATABASE=seu-database

# Configurações
PORT=8000
DEBUG=False
```

---

## 🚀 Implementação Passo a Passo

### Passo 1: Criar API REST (FastAPI)

**bot_api.py:**
```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from agente_apontamentos import AgenteApontamentos
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar FastAPI
app = FastAPI(title="Agente Apontamentos API")

# Configurar Bot Framework
bot_settings = BotFrameworkAdapterSettings(
    app_id=os.getenv("BOT_APP_ID"),
    app_password=os.getenv("BOT_APP_PASSWORD")
)
adapter = BotFrameworkAdapter(bot_settings)

# Instanciar agente
agente = AgenteApontamentos()

@app.post("/api/messages")
async def messages(request: Request):
    """
    Endpoint que recebe mensagens do Teams
    """
    try:
        body = await request.json()
        activity = Activity().deserialize(body)
        
        # Processar mensagem
        auth_header = request.headers.get("Authorization", "")
        
        async def bot_logic(turn_context):
            # Obter informações do usuário
            user_name = turn_context.activity.from_property.name
            user_message = turn_context.activity.text
            
            # Consultar agente
            resposta = agente.responder_pergunta(user_message, user_name)
            
            # Enviar resposta
            await turn_context.send_activity(resposta['resposta'])
        
        await adapter.process_activity(activity, auth_header, bot_logic)
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    """Health check"""
    return {"status": "healthy", "agente": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
```

### Passo 2: Criar Adaptive Cards (Respostas Formatadas)

**adaptive_cards.py:**
```python
def criar_card_estatistica(dados):
    """Cria Adaptive Card para estatísticas"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "📊 Estatísticas de Apontamento"
            },
            {
                "type": "FactSet",
                "facts": [
                    {
                        "title": "Duração Média:",
                        "value": dados.get('formatado', 'N/A')
                    },
                    {
                        "title": "Total de Horas:",
                        "value": f"{dados.get('media_horas', 0):.2f}h"
                    }
                ]
            }
        ]
    }

def criar_card_ranking(ranking_data):
    """Cria Adaptive Card para ranking"""
    items = []
    for i, (nome, dados) in enumerate(ranking_data.items(), 1):
        items.append({
            "type": "TextBlock",
            "text": f"{i}. **{nome}**: {dados['sum']:.2f}h",
            "wrap": True
        })
    
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "🏆 Ranking de Horas Trabalhadas"
            },
            {
                "type": "Container",
                "items": items
            }
        ]
    }
```

### Passo 3: Configurar Atualização Automática de Dados

**scheduler.py:**
```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import subprocess

def atualizar_dados():
    """Executa script de atualização de dados"""
    print(f"[{datetime.now()}] Atualizando dados...")
    try:
        subprocess.run(["python", "analise_duracao_trabalho.py"], check=True)
        print("✅ Dados atualizados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao atualizar dados: {e}")

# Configurar scheduler
scheduler = BackgroundScheduler()

# Atualizar a cada 1 hora
scheduler.add_job(
    atualizar_dados,
    'interval',
    hours=1,
    id='atualizar_dados'
)

# Iniciar scheduler
scheduler.start()
```

### Passo 4: Deployment no Azure

**1. Criar Azure Web App:**
```bash
az webapp create \
  --resource-group meu-grupo \
  --plan meu-plan \
  --name agente-apontamentos-bot \
  --runtime "PYTHON:3.11"
```

**2. Configurar variáveis de ambiente:**
```bash
az webapp config appsettings set \
  --resource-group meu-grupo \
  --name agente-apontamentos-bot \
  --settings BOT_APP_ID="..." BOT_APP_PASSWORD="..."
```

**3. Deploy do código:**
```bash
az webapp up \
  --resource-group meu-grupo \
  --name agente-apontamentos-bot
```

### Passo 5: Configurar Bot no Teams

**manifest.json:**
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.14/MicrosoftTeams.schema.json",
  "manifestVersion": "1.14",
  "version": "1.0.0",
  "id": "SEU-BOT-APP-ID",
  "packageName": "com.empresa.agente.apontamentos",
  "developer": {
    "name": "Sua Empresa",
    "websiteUrl": "https://www.empresa.com",
    "privacyUrl": "https://www.empresa.com/privacy",
    "termsOfUseUrl": "https://www.empresa.com/terms"
  },
  "name": {
    "short": "Agente Apontamentos",
    "full": "Agente Inteligente de Apontamentos"
  },
  "description": {
    "short": "Consulte seus apontamentos via chat",
    "full": "Bot inteligente para consultar estatísticas e dados de apontamento de trabalho"
  },
  "icons": {
    "outline": "icon-outline.png",
    "color": "icon-color.png"
  },
  "accentColor": "#0078D4",
  "bots": [
    {
      "botId": "SEU-BOT-APP-ID",
      "scopes": ["personal", "team"],
      "supportsFiles": false,
      "isNotificationOnly": false,
      "commandLists": [
        {
          "scopes": ["personal", "team"],
          "commands": [
            {
              "title": "ajuda",
              "description": "Mostrar comandos disponíveis"
            },
            {
              "title": "média",
              "description": "Ver duração média de trabalho"
            },
            {
              "title": "hoje",
              "description": "Ver apontamentos de hoje"
            },
            {
              "title": "ranking",
              "description": "Ver ranking de horas"
            }
          ]
        }
      ]
    }
  ],
  "permissions": ["identity", "messageTeamMembers"],
  "validDomains": [
    "SEU-DOMINIO.azurewebsites.net"
  ]
}
```

---

## 💬 Exemplos de Uso

### Consultas Básicas

```
👤 Usuário: "Quanto tempo trabalhei hoje?"
🤖 Bot:
