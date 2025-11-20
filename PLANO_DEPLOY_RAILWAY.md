# 🚂 PLANO DE DEPLOY - RAILWAY
**Bot de Apontamentos para Microsoft Teams**

---

## 📋 FASE 1: PREPARAÇÃO DE ARQUIVOS (30 minutos)

### 1.1 Criar `railway.json` ✅
**Objetivo**: Configurar como o Railway deve fazer o deploy

**Conteúdo**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": null,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Por quê**: Define que usaremos Docker, qual o endpoint de health check e políticas de restart.

---

### 1.2 Criar `requirements_minimal.txt` ✅ (BACKUP)
**Objetivo**: Ter uma versão enxuta caso o build demore muito

**Dependências essenciais**:
```
# Bot Framework
botbuilder-core==4.17.0
botbuilder-schema==4.17.0
botbuilder-integration-aiohttp==4.17.0

# Web Framework
fastapi==0.121.1
uvicorn[standard]==0.38.0
gunicorn==23.0.0

# Data Processing
pandas==2.3.3
numpy==1.26.4

# AI
openai==1.97.1

# Utilities
python-dotenv==1.0.1
aiohttp>=3.9.1
```

**Por quê**: Se o `requirements.txt` completo (200+ pacotes) for muito pesado, usamos este.

---

### 1.3 Atualizar `.gitignore` ✅
**Objetivo**: Garantir que CSV e secrets não vão pro Railway via Git

**Adicionar**:
```
# Dados sensíveis
resultados/*.csv
*.env
.env.local
.env.production

# Azure (não precisamos mais)
.azure/
.deployment
startup.sh
```

**Por quê**: CSV de 90MB será enviado via Railway CLI separadamente, não pelo Git.

---

### 1.4 Criar `.env.example` ✅
**Objetivo**: Documentar variáveis de ambiente necessárias

**Conteúdo**:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Microsoft Bot Framework (para Teams)
BOT_APP_ID=your-app-id-here
BOT_APP_PASSWORD=your-app-password-here
BOT_TENANT_ID=your-tenant-id-here

# Application Settings
PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production

# Optional: Se usar Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string-here
```

**Por quê**: Facilita a configuração das variáveis no Railway.

---

### 1.5 Ajustar `Dockerfile` (OPCIONAL) ✅
**Verificar se está otimizado**:

**Pontos a conferir**:
- ✅ Multi-stage build? (Não necessário por enquanto, mas pode otimizar)
- ✅ Cache de pip está habilitado? (Sim, `--no-cache-dir` é intencional)
- ✅ Healthcheck incluído? (Railway usa endpoint `/health`)

**Possível otimização** (OPCIONAL):
```dockerfile
# Adicionar healthcheck no próprio Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
```

---

### 1.6 Criar `Procfile` (BACKUP) ✅
**Objetivo**: Alternativa caso Railway não use Dockerfile

**Conteúdo**:
```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT --timeout 600 bot.bot_api:app
```

**Por quê**: Railway pode preferir Procfile em alguns casos.

---

### 1.7 Commitar Mudanças ✅
**Comandos**:
```bash
git add railway.json .env.example .gitignore Procfile
git commit -m "Add: Configurações para deploy no Railway"
git push origin main
```

**Por quê**: Railway precisa acessar o repositório GitHub.

---

## 📋 FASE 2: CONFIGURAÇÃO DA CONTA RAILWAY (15 minutos)

### 2.1 Criar Conta no Railway ✅
**Passos**:
1. Acessar: https://railway.app
2. Clicar em "Start a New Project"
3. Fazer login com **GitHub** (recomendado)
4. Autorizar Railway a acessar seus repositórios

**Por quê**: Railway usa GitHub OAuth para deploy automático.

---

### 2.2 Adicionar Método de Pagamento (OPCIONAL) ✅
**Opções**:
- **Plano Hobby** (gratuito): $5 de crédito/mês
- **Plano Developer** (pago): $5/mês + uso (~$10-15 total)

**Recomendação**: Começar no plano gratuito, depois migrar se necessário.

**Por quê**: Plano gratuito pode ser suficiente para testes iniciais.

---

### 2.3 Instalar Railway CLI (OPCIONAL mas RECOMENDADO) ✅
**Windows (PowerShell)**:
```powershell
iwr https://railway.app/install.ps1 -useb | iex
```

**Verificar instalação**:
```bash
railway --version
```

**Por quê**: Facilita envio do CSV e debugging via terminal.

---

## 📋 FASE 3: CRIAR PROJETO NO RAILWAY (20 minutos)

### 3.1 Criar Novo Projeto ✅
**Passos**:
1. No dashboard Railway: "New Project"
2. Escolher: "Deploy from GitHub repo"
3. Selecionar: `ElaineMBarros/Blocks_teams_apontamento`
4. Branch: `main`
5. Clicar em "Deploy Now"

**Por quê**: Railway vai clonar o repo e detectar automaticamente o Dockerfile.

---

### 3.2 Configurar Variáveis de Ambiente ✅
**No Railway Dashboard → Settings → Variables**

**Adicionar uma por uma**:
```
OPENAI_API_KEY = sk-proj-...
OPENAI_MODEL = gpt-4o-mini
PORT = 8000
LOG_LEVEL = INFO
ENVIRONMENT = production
```

**⚠️ IMPORTANTE**: Deixe `BOT_APP_ID`, `BOT_APP_PASSWORD` e `BOT_TENANT_ID` **vazios** por enquanto (vamos pegar depois no Azure Bot Service).

**Por quê**: Railway injeta essas variáveis no container Docker.

---

### 3.3 Aguardar Primeiro Build ✅
**O que vai acontecer**:
1. Railway clona o repositório
2. Detecta `Dockerfile`
3. Faz build da imagem Docker (~5-10 minutos)
4. Inicia o container
5. Expõe URL pública: `https://seu-projeto.railway.app`

**Como acompanhar**:
- Dashboard Railway → "Deployments" → Ver logs em tempo real

**Possíveis erros**:
- ❌ CSV não encontrado (normal, vamos enviar na próxima fase)
- ❌ OPENAI_API_KEY inválido (conferir variável)

---

## 📋 FASE 4: UPLOAD DO CSV (15 minutos)

### 4.1 Opção A: Via Railway CLI (RECOMENDADO) ✅
**Passo 1**: Fazer login
```bash
railway login
```

**Passo 2**: Linkar ao projeto
```bash
cd C:\Users\elain\Desktop\blocks_teams
railway link
# Selecionar o projeto criado
```

**Passo 3**: Acessar shell do container
```bash
railway run bash
```

**Passo 4**: Upload via scp/rsync (dentro do shell)
```bash
# No shell Railway
mkdir -p /app/resultados
exit

# No PowerShell local
railway run --service web bash -c "cat > /app/resultados/dados_anonimizados_decupado_20251118_211544.csv" < resultados/dados_anonimizados_decupado_20251118_211544.csv
```

**Por quê**: Railway CLI permite acesso direto ao container.

---

### 4.2 Opção B: Via Volume Persistente (MELHOR PARA PRODUÇÃO) ✅
**Passo 1**: No Railway Dashboard
1. Ir em "Settings" → "Volumes"
2. Criar novo volume: `/app/resultados`
3. Mount path: `/app/resultados`

**Passo 2**: Upload via Railway Dashboard
1. Clicar no volume criado
2. "Upload Files"
3. Selecionar `dados_anonimizados_decupado_20251118_211544.csv`

**Por quê**: Volume persiste entre deploys e restarts.

---

### 4.3 Opção C: Hospedar CSV Externamente (ALTERNATIVA) ✅
**Serviços**:
- Azure Blob Storage (já tem conta Azure)
- AWS S3
- Google Cloud Storage
- Cloudflare R2 (gratuito até 10GB)

**Modificar código**:
```python
# Em agente_apontamentos.py
import requests

def carregar_dados_remoto(self):
    url = "https://seu-storage.blob.core.windows.net/data/dados.csv"
    response = requests.get(url)
    self.df = pd.read_csv(io.StringIO(response.text))
```

**Por quê**: CSV não fica no Git nem no container.

---

## 📋 FASE 5: TESTES E VALIDAÇÃO (20 minutos)

### 5.1 Testar Health Check ✅
**Comando**:
```powershell
curl https://seu-projeto.railway.app/health
```

**Resposta esperada**:
```json
{
  "status": "healthy",
  "service": "Bot Apontamentos API",
  "version": "1.0.0",
  "timestamp": "2025-11-20T21:00:00Z",
  "agente_loaded": true,
  "total_registros": 207228
}
```

**Se falhar**: Ver logs no Railway Dashboard.

---

### 5.2 Testar Endpoint Root ✅
**Comando**:
```powershell
curl https://seu-projeto.railway.app/
```

**Resposta esperada**:
```json
{
  "message": "Bot de Apontamentos - API Ativa",
  "status": "online",
  "endpoints": [
    "/health",
    "/api/messages",
    "/docs"
  ]
}
```

---

### 5.3 Testar API de Mensagens (Bot Endpoint) ✅
**Comando** (via Bot Framework Emulator local):
```
URL: https://seu-projeto.railway.app/api/messages
Method: POST
Headers: 
  Content-Type: application/json
Body:
{
  "type": "message",
  "text": "qual a média de horas?",
  "from": {"id": "user123", "name": "Teste"},
  "conversation": {"id": "conv123"}
}
```

**Resposta esperada**: Bot responde com estatísticas.

---

### 5.4 Verificar Logs em Tempo Real ✅
**Via Railway Dashboard**:
1. Ir em "Deployments"
2. Clicar no deploy ativo
3. Ver logs streaming

**Via CLI**:
```bash
railway logs
```

**O que procurar**:
- ✅ `📁 Carregando: resultados/dados_anonimizados_decupado_20251118_211544.csv`
- ✅ `✅ Dados carregados: 207228 registros`
- ✅ `Uvicorn running on http://0.0.0.0:8000`

---

## 📋 FASE 6: REGISTRO NO AZURE BOT SERVICE (40 minutos)

### 6.1 Criar Azure Bot Resource ✅
**Portal Azure**:
1. "Create a resource" → "Azure Bot"
2. **Bot handle**: `bot-apontamentos-railway`
3. **Subscription**: Sua subscription
4. **Resource group**: `rg-bot-apontamentos` (mesmo do anterior)
5. **Pricing tier**: F0 (Free)
6. **Microsoft App ID**: "Create new Microsoft App ID"
7. **Type of App**: "Multi Tenant"

**Por quê**: Registra o bot no Microsoft Bot Framework.

---

### 6.2 Obter Credenciais ✅
**Após criação**:
1. Ir em "Configuration" → "Manage Microsoft App ID"
2. Copiar **Application (client) ID**
3. Ir em "Certificates & secrets" → "New client secret"
4. Criar secret com nome: "RailwayBot"
5. **COPIAR O SECRET AGORA** (não aparece depois!)
6. Copiar também o **Tenant ID** (Overview)

**Guardar**:
```
BOT_APP_ID = [Application ID]
BOT_APP_PASSWORD = [Client Secret]
BOT_TENANT_ID = [Tenant ID]
```

---

### 6.3 Configurar Messaging Endpoint ✅
**No Azure Bot → Configuration**:
1. **Messaging endpoint**: `https://seu-projeto.railway.app/api/messages`
2. Salvar

**Por quê**: Teams vai enviar mensagens para essa URL.

---

### 6.4 Adicionar Credenciais no Railway ✅
**Railway Dashboard → Settings → Variables**:

**Adicionar**:
```
BOT_APP_ID = [copiar do Azure]
BOT_APP_PASSWORD = [copiar do Azure]
BOT_TENANT_ID = [copiar do Azure]
```

**Reiniciar deploy**: Railway vai redeployar automaticamente.

---

## 📋 FASE 7: CONECTAR AO TEAMS (30 minutos)

### 7.1 Ativar Canal do Teams ✅
**Azure Bot → Channels**:
1. Clicar em "Microsoft Teams"
2. "Microsoft Teams Commercial (most common)" → Enable
3. Aceitar os termos
4. Salvar

**Por quê**: Habilita o bot a receber mensagens do Teams.

---

### 7.2 Testar no Teams via "Open in Teams" ✅
**Azure Bot → Channels → Microsoft Teams**:
1. Clicar em "Open in Teams"
2. Teams vai abrir com uma conversa com seu bot
3. Enviar mensagem: "qual a média de horas?"

**Resposta esperada**: Bot responde com estatísticas.

---

### 7.3 Criar Manifest do Teams (Para distribuição) ✅
**Pasta `manifest/` já existe no projeto**

**Atualizar `manifest.json`**:
```json
{
  "bots": [
    {
      "botId": "[BOT_APP_ID aqui]",
      "scopes": ["personal", "team"],
      "commandLists": [...]
    }
  ],
  "validDomains": [
    "seu-projeto.railway.app"
  ]
}
```

**Zipar**:
```powershell
Compress-Archive -Path manifest/* -DestinationPath bot-apontamentos-teams.zip
```

---

### 7.4 Instalar no Teams (Sideload) ✅
**Teams → Apps → Upload a custom app**:
1. Selecionar `bot-apontamentos-teams.zip`
2. Clicar em "Add"
3. Bot aparece na lista de apps

**Ou instalar em um Team**:
1. Ir no Team desejado
2. Apps → Upload custom app
3. Selecionar o ZIP

---

## 📋 FASE 8: MONITORAMENTO E AJUSTES (Contínuo)

### 8.1 Configurar Alertas no Railway ✅
**Settings → Notifications**:
- Deploy failures
- High memory usage (>80%)
- Crash alerts

**Por quê**: Ser notificado se algo der errado.

---

### 8.2 Configurar Auto-scaling (OPCIONAL) ✅
**Settings → Autoscaling**:
- Min replicas: 1
- Max replicas: 3
- Scale up at: 80% CPU

**Por quê**: Se muitos usuários usarem simultaneamente.

---

### 8.3 Adicionar Domain Customizado (OPCIONAL) ✅
**Settings → Domains → Custom Domain**:
```
bot-apontamentos.seudominio.com.br
```

**Requer**: DNS CNAME apontando para Railway.

---

### 8.4 Configurar CI/CD ✅
**Já está automático!**
- Qualquer push em `main` → Railway faz rebuild
- Para desabilitar: Settings → "Disable auto-deploy"

---

## 📋 CHECKLIST FINAL

### ✅ Antes de Começar
- [ ] Código local funcionando 100%
- [ ] CSV de 90MB disponível
- [ ] Chave OpenAI válida
- [ ] Conta GitHub ativa
- [ ] Cartão de crédito (se usar plano pago)

### ✅ Arquivos Criados
- [ ] `railway.json`
- [ ] `.env.example`
- [ ] `.gitignore` atualizado
- [ ] `Procfile` (backup)
- [ ] `Dockerfile` conferido
- [ ] Tudo commitado no GitHub

### ✅ Railway Configurado
- [ ] Projeto criado
- [ ] Variáveis de ambiente configuradas
- [ ] Primeiro deploy concluído
- [ ] CSV enviado (via CLI ou Volume)
- [ ] Health check respondendo

### ✅ Azure Bot Service
- [ ] Bot registrado
- [ ] App ID/Password obtidos
- [ ] Messaging endpoint configurado
- [ ] Credenciais no Railway

### ✅ Teams Conectado
- [ ] Canal Teams habilitado
- [ ] Teste via "Open in Teams" OK
- [ ] Manifest atualizado (se aplicar)
- [ ] App instalado no Teams

---

## 💰 CUSTOS ESTIMADOS

### Railway
| Item | Custo Mensal |
|------|--------------|
| Plano Developer | $5 (fixo) |
| CPU (média) | $3-5 |
| RAM (média) | $3-5 |
| Network | $0-2 |
| **TOTAL** | **$11-17/mês** |
| **Em Reais** | **R$ 55-85/mês** |

### Azure Bot Service
| Item | Custo |
|------|-------|
| F0 (Free tier) | R$ 0 |
| Standard (se necessário) | R$ 2,50/1000 msgs |

### Comparação
- ❌ Azure App Service P1v2: **R$ 400/mês**
- ✅ Railway + Bot Service: **R$ 55-85/mês**
- **Economia**: **~R$ 320/mês** (80%)

---

## 🆘 TROUBLESHOOTING

### Problema: Build falha no Railway
**Solução**:
1. Ver logs no Railway Dashboard
2. Conferir se `Dockerfile` está no root
3. Tentar usar `requirements_minimal.txt`

### Problema: CSV não carregado
**Solução**:
1. Verificar volume no Railway
2. Conferir path no código: `resultados/dados_...csv`
3. Ver logs: procurar por "Nenhum dado encontrado"

### Problema: Bot não responde no Teams
**Solução**:
1. Testar endpoint `/api/messages` via curl
2. Conferir BOT_APP_ID/PASSWORD no Railway
3. Ver logs: procurar por "Unauthorized" ou "401"

### Problema: OPENAI_API_KEY inválida
**Solução**:
1. Testar key: https://platform.openai.com/api-keys
2. Verificar se não expirou
3. Gerar nova key se necessário

---

## 📞 SUPORTE

### Railway
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Microsoft Bot Framework
- Docs: https://learn.microsoft.com/azure/bot-service/
- Samples: https://github.com/microsoft/botbuilder-samples

---

**Última atualização**: 20/11/2025 - 21:30
**Tempo estimado total**: 2h30min - 3h
**Complexidade**: Média
**Pré-requisitos**: Conta GitHub, Conta Azure (para Bot Service), Cartão de crédito (Railway)
