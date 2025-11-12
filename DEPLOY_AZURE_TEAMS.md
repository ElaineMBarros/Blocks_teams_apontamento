# 🚀 Deploy no Azure e Publicação no Microsoft Teams

**Guia completo para colocar o bot em produção**

---

## 📋 Visão Geral

Você tem **3 opções** para usar o bot:

1. **🔧 Ngrok** - Teste temporário (rápido, grátis)
2. **☁️ Azure** - Produção completa (recomendado)
3. **🌐 Bot Framework Web** - Teste online (limitado)

---

## 🔧 OPÇÃO 1: Ngrok (Teste Rápido)

### Vantagens
- ✅ Rápido (5 minutos)
- ✅ Grátis
- ✅ Sem precisar Azure
- ❌ Temporário (URL muda cada execução)

### Passos

#### 1. Instalar Ngrok
```bash
# Download: https://ngrok.com/download
# Ou via Chocolatey (Windows):
choco install ngrok
```

#### 2. Iniciar o Bot Local
```bash
# Se ainda não estiver rodando:
uvicorn bot.bot_api:app --host 0.0.0.0 --port 8000
```

#### 3. Expor com Ngrok
```bash
# Em outro terminal:
ngrok http 8000
```

Você verá:
```
Forwarding   https://xxxx-xx-xx-xx.ngrok.io -> http://localhost:8000
```

#### 4. Usar no Bot Framework Emulator
```
URL: https://xxxx-xx-xx-xx.ngrok.io/api/messages
```

#### ⚠️ Limitações
- URL muda cada vez que reinicia ngrok
- Conexão pode cair
- Plano grátis tem limites
- **NÃO recomendado para produção!**

---

## ☁️ OPÇÃO 2: Deploy no Azure (PRODUÇÃO)

### Pré-requisitos

- ✅ Conta Azure ativa
- ✅ Azure CLI instalado
- ✅ Git instalado
- ✅ Código do bot pronto
- ✅ Aprovação para custos (~R$ 2.450/mês)

---

## 📝 Passo a Passo - Deploy Azure

### FASE 1: Preparação (5 min)

#### 1.1 Instalar Azure CLI
```bash
# Windows:
winget install Microsoft.AzureCLI

# Ou download: https://aka.ms/installazurecliwindows
```

#### 1.2 Login no Azure
```bash
az login
```

#### 1.3 Criar requirements.txt para produção
```bash
# Já existe! Use:
requirements.txt
```

---

### FASE 2: Criar Recursos Azure (15 min)

#### 2.1 Definir Variáveis
```bash
# Defina essas variáveis:
$RESOURCE_GROUP = "rg-bot-apontamentos"
$LOCATION = "brazilsouth"
$APP_SERVICE_PLAN = "asp-bot-apontamentos"
$APP_NAME = "bot-apontamentos-teams"
$BOT_NAME = "bot-apontamentos"
```

#### 2.2 Criar Resource Group
```bash
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION
```

#### 2.3 Criar App Service Plan
```bash
az appservice plan create `
  --name $APP_SERVICE_PLAN `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku B1 `
  --is-linux
```

#### 2.4 Criar Web App
```bash
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan $APP_SERVICE_PLAN `
  --name $APP_NAME `
  --runtime "PYTHON:3.11"
```

#### 2.5 Configurar Startup Command
```bash
az webapp config set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --startup-file "gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 bot.bot_api:app"
```

---

### FASE 3: Registrar Bot no Azure (10 min)

#### 3.1 Criar Bot Service Identity
```bash
az ad app create `
  --display-name $BOT_NAME
```

**Salve o `appId` que aparece!**

#### 3.2 Criar Secret para o Bot
```bash
$APP_ID = "cole-aqui-o-appId"

az ad app credential reset `
  --id $APP_ID `
  --append
```

**Salve o `password` que aparece!**

#### 3.3 Criar Azure Bot Service
```bash
$BOT_ENDPOINT = "https://$APP_NAME.azurewebsites.net/api/messages"

az bot create `
  --resource-group $RESOURCE_GROUP `
  --name $BOT_NAME `
  --appid $APP_ID `
  --password "<senha-do-passo-anterior>" `
  --endpoint $BOT_ENDPOINT `
  --kind webapp `
  --location global
```

---

### FASE 4: Configurar Variáveis de Ambiente (5 min)

#### 4.1 Adicionar Configurações ao App Service
```bash
az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings `
    BOT_APP_ID="$APP_ID" `
    BOT_APP_PASSWORD="<senha>" `
    PORT="8000" `
    DEBUG="False" `
    ENVIRONMENT="production"
```

---

### FASE 5: Deploy do Código (10 min)

#### 5.1 Adicionar gunicorn ao requirements.txt
```bash
# Adicione ao final de requirements.txt:
echo "gunicorn==21.2.0" >> requirements.txt
```

#### 5.2 Criar .deployment (configuração deploy)
```bash
# Criar arquivo .deployment na raiz:
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

#### 5.3 Deploy via Git (Recomendado)
```bash
# Inicializar git se ainda não tiver:
git init
git add .
git commit -m "Deploy bot to Azure"

# Configurar deployment:
az webapp deployment source config-local-git `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP

# Git vai retornar uma URL, adicione como remote:
git remote add azure <URL-do-comando-acima>

# Deploy!
git push azure main
```

#### OU 5.3 Deploy via ZIP
```bash
# Criar ZIP do projeto:
Compress-Archive -Path * -DestinationPath deploy.zip

# Deploy:
az webapp deployment source config-zip `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --src deploy.zip
```

---

### FASE 6: Conectar ao Teams (5 min)

#### 6.1 Habilitar Teams Channel
```bash
# No Portal Azure:
# 1. Vá para o Azure Bot Service
# 2. Channels > Microsoft Teams
# 3. Click "Save"
```

#### 6.2 Ou via CLI:
```bash
az bot msteams create `
  --resource-group $RESOURCE_GROUP `
  --name $BOT_NAME
```

---

### FASE 7: Criar App Teams (10 min)

#### 7.1 Criar manifest.json
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
  "manifestVersion": "1.16",
  "version": "1.0.0",
  "id": "SEU-APP-ID-AQUI",
  "packageName": "com.empresa.bot.apontamentos",
  "developer": {
    "name": "Sua Empresa",
    "websiteUrl": "https://www.empresa.com",
    "privacyUrl": "https://www.empresa.com/privacy",
    "termsOfUseUrl": "https://www.empresa.com/terms"
  },
  "name": {
    "short": "Agente Apontamentos",
    "full": "Agente de Apontamentos Teams"
  },
  "description": {
    "short": "Bot para consultar apontamentos",
    "full": "Bot inteligente para consultas de apontamentos de horas trabalhadas"
  },
  "icons": {
    "outline": "outline.png",
    "color": "color.png"
  },
  "accentColor": "#FFFFFF",
  "bots": [
    {
      "botId": "SEU-APP-ID-AQUI",
      "scopes": [
        "personal",
        "team"
      ],
      "supportsFiles": false,
      "isNotificationOnly": false,
      "commandLists": [
        {
          "scopes": [
            "personal",
            "team"
          ],
          "commands": [
            {
              "title": "média",
              "description": "Ver duração média de trabalho"
            },
            {
              "title": "ranking",
              "description": "Top 10 funcionários"
            },
            {
              "title": "hoje",
              "description": "Apontamentos de hoje"
            }
          ]
        }
      ]
    }
  ],
  "permissions": [
    "identity",
    "messageTeamMembers"
  ],
  "validDomains": [
    "*.botframework.com",
    "*.azurewebsites.net"
  ]
}
```

#### 7.2 Criar Ícones
- `color.png` - 192x192 px
- `outline.png` - 32x32 px (transparente)

#### 7.3 Criar ZIP do App
```bash
# Estrutura:
manifest/
  - manifest.json
  - color.png
  - outline.png

# Zipar:
Compress-Archive -Path manifest/* -DestinationPath ApontamentosBot.zip
```

---

### FASE 8: Publicar no Teams (5 min)

#### 8.1 Via Teams Admin Center
1. Acesse: https://admin.teams.microsoft.com
2. **Teams apps** > **Manage apps**
3. **Upload** > **Upload an app to your org's app catalog**
4. Selecione `ApontamentosBot.zip`
5. **Submit**

#### 8.2 Aprovar App
1. **Teams apps** > **Manage apps**
2. Encontre "Agente Apontamentos"
3. **Publish** > **Publish to org**

#### 8.3 Usar no Teams
1. Abra Microsoft Teams
2. **Apps** > **Built for your org**
3. Encontre "Agente Apontamentos"
4. **Add**
5. **Converse com o bot!** 🎉

---

## 🌐 OPÇÃO 3: Bot Framework Web (Limitado)

### Não Recomendado Porque:
- ❌ Não pode integrar com Teams diretamente
- ❌ Sem Adaptive Cards completos
- ❌ Interface limitada
- ✅ Útil apenas para testes básicos

---

## 💰 Custos Estimados Azure

### Mensal (Produção):
```
App Service (B1):       R$ 150/mês
Azure Bot Service:      R$ 250/mês
Storage:                R$ 50/mês
---------------------------------
TOTAL:                  R$ 450/mês
```

### Anual:
```
Primeiro ano:           R$ 5.400
Anos seguintes:         R$ 5.400/ano
```

**82% mais barato que on-premises!**

---

## ✅ Checklist de Deploy

### Antes do Deploy:
- [ ] Código testado localmente
- [ ] Dados funcionando
- [ ] Todos os comandos testados
- [ ] Conta Azure ativa
- [ ] Aprovação de custos

### Durante o Deploy:
- [ ] Resource Group criado
- [ ] App Service criado
- [ ] Bot Service registrado
- [ ] Variáveis configuradas
- [ ] Código deployado
- [ ] Logs verificados

### Depois do Deploy:
- [ ] Bot responde no endpoint Azure
- [ ] Teams channel habilitado
- [ ] Manifest criado
- [ ] App publicado no Teams
- [ ] Usuários conseguem usar

---

## 🐛 Troubleshooting

### Bot não responde no Azure:
```bash
# Ver logs:
az webapp log tail `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME
```

### Erro de autenticação:
- Verifique APP_ID e PASSWORD nas configurações
- Verifique endpoint no Bot Service

### Teams não encontra o bot:
- Verifique se o channel está habilitado
- Verifique o manifest.json (botId correto?)
- App foi publicado no catalog?

---

## 📚 Documentos de Referência

- **Infraestrutura detalhada:** `REL.xxxx.de2025v.1.0_demanda_corporativa_bot_apontamentos.docx`
- **Teste local:** `GUIA_INICIO_RAPIDO.md`
- **Migração completa:** `MIGRACAO_COMPLETA_TEAMS.md`

---

## 🎯 Resumo das Opções

| Opção | Tempo | Custo | Durabilidade | Recomendado |
|-------|-------|-------|--------------|-------------|
| **Ngrok** | 5 min | R$ 0 | Temporário | Teste rápido |
| **Azure** | 60 min | R$ 450/mês | Permanente | ✅ Produção |
| **Bot Web** | N/A | R$ 0 | N/A | ❌ Limitado |

---

## 🚀 Recomendação

Para **produção no Teams**:
1. ✅ Deploy no Azure (60 min setup)
2. ✅ Publicar app no catalog Teams
3. ✅ Usar na organização

Para **teste rápido**:
1. ✅ Ngrok (5 min setup)
2. ✅ Testar no Emulator
3. ⚠️ URL muda cada execução

---

**🎉 Escolha sua opção e siga os passos acima!**
