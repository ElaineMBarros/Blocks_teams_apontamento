# 📦 Guia de Instalação - Bot Teams

Este guia explica como configurar e executar o bot localmente ou em produção.

---

## 🎯 Pré-requisitos

### Software Necessário

```yaml
Obrigatório:
  - Python 3.11 ou superior
  - pip (gerenciador de pacotes Python)
  - Git

Opcional (para desenvolvimento):
  - Visual Studio Code
  - Azure CLI
  - Teams Toolkit Extension
```

### Contas e Acessos

```yaml
Azure:
  - Conta Azure ativa
  - Permissões para criar recursos
  - Subscription válido

Microsoft Teams:
  - Acesso ao tenant
  - Permissões para instalar apps customizados

Microsoft Fabric:
  - Acesso ao Data Warehouse
  - Credentials de conexão
```

---

## 🚀 Instalação Local

### 1. Clonar Repositório

```bash
git clone https://github.com/ElaineMBarros/Blocks_teams_apontamento.git
cd Blocks_teams_apontamento
```

### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Editar .env com suas credenciais
# Use um editor de texto (notepad, VSCode, etc)
```

**Exemplo de `.env`:**
```env
BOT_APP_ID=sua-app-id-aqui
BOT_APP_PASSWORD=sua-senha-aqui
BOT_TENANT_ID=seu-tenant-id

FABRIC_ENDPOINT=endpoint.datawarehouse.fabric.microsoft.com
FABRIC_DATABASE=nome-do-banco

PORT=8000
DEBUG=True
ENVIRONMENT=development
```

### 5. Testar Localmente

```bash
# Rodar o bot
python -m bot.bot_api

# Ou usando uvicorn diretamente
uvicorn bot.bot_api:app --reload --port 8000
```

**Verificar se está funcionando:**
- Abra navegador em: http://localhost:8000
- Deve mostrar informações do bot
- Health check: http://localhost:8000/health

---

## ☁️ Deploy no Azure

### 1. Criar Azure Bot Service

```bash
# Login no Azure
az login

# Criar Resource Group
az group create --name rg-bot-apontamentos --location brazilsouth

# Criar Bot Channels Registration
az bot create \
  --resource-group rg-bot-apontamentos \
  --name bot-apontamentos \
  --location global \
  --sku F0 \
  --kind registration \
  --endpoint https://SEU-APP.azurewebsites.net/api/messages
```

### 2. Criar App Service

```bash
# Criar App Service Plan
az appservice plan create \
  --name plan-bot-apontamentos \
  --resource-group rg-bot-apontamentos \
  --sku B1 \
  --is-linux

# Criar Web App
az webapp create \
  --resource-group rg-bot-apontamentos \
  --plan plan-bot-apontamentos \
  --name app-bot-apontamentos \
  --runtime "PYTHON:3.11"
```

### 3. Configurar Variáveis de Ambiente no Azure

```bash
az webapp config appsettings set \
  --resource-group rg-bot-apontamentos \
  --name app-bot-apontamentos \
  --settings \
    BOT_APP_ID="..." \
    BOT_APP_PASSWORD="..." \
    FABRIC_ENDPOINT="..." \
    FABRIC_DATABASE="..." \
    PORT="8000" \
    DEBUG="False" \
    ENVIRONMENT="production"
```

### 4. Deploy do Código

```bash
# Configurar deployment
az webapp deployment source config-local-git \
  --name app-bot-apontamentos \
  --resource-group rg-bot-apontamentos

# Fazer push do código
git remote add azure <URL_DO_GIT_AZURE>
git push azure main
```

---

## 🔧 Configuração do Teams

### 1. Criar Manifest do App

O manifest já está em `manifest/manifest.json`. Você precisa:

1. Substituir `BOT_APP_ID` pelo seu App ID real
2. Substituir URLs pelo seu endpoint Azure
3. Adicionar ícones em `icons/`

### 2. Empacotar App

```bash
# Criar pasta temporária
mkdir appPackage
cd appPackage

# Copiar arquivos necessários
copy ..\manifest\manifest.json .
copy ..\icons\* .

# Criar arquivo .zip
# No Windows: selecionar todos, clicar com botão direito, "Enviar para" > "Pasta compactada"
# No Linux/Mac: zip -r app.zip *
```

### 3. Instalar no Teams

1. Abrir Microsoft Teams
2. Apps > Gerenciar seus apps
3. "Carregar um app customizado"
4. Selecionar o arquivo `.zip` criado
5. Adicionar ao Teams

---

## 🧪 Testes

### Testar Localmente com ngrok

```bash
# Instalar ngrok
# Windows: https://ngrok.com/download

# Executar ngrok
ngrok http 8000

# Copiar URL pública (exemplo: https://abc123.ngrok.io)
# Usar essa URL no Bot Framework Portal como endpoint
```

### Testar Comandos

No Teams, envie mensagens para o bot:
- `oi` - Mensagem de boas-vindas
- `média` - Estatísticas gerais
- `hoje` - Apontamentos do dia
- `ranking` - Top funcionários
- `ajuda` - Lista de comandos

---

## 🐛 Troubleshooting

### Bot não responde

```bash
# Verificar logs
# Azure:
az webapp log tail --name app-bot-apontamentos --resource-group rg-bot-apontamentos

# Local:
# Verificar console onde está rodando o bot
```

### Erro de autenticação

- Verificar se `BOT_APP_ID` e `BOT_APP_PASSWORD` estão corretos
- Confirmar que o endpoint está acessível publicamente
- Verificar se o webhook no Bot Framework Portal está configurado

### Agente não carrega dados

- Verificar se `agente_apontamentos.py` está na raiz do projeto
- Confirmar que dados estão em `resultados/dados_com_duracao_*.csv`
- Testar conexão com Fabric Data Warehouse

---

## 📚 Recursos Adicionais

- [Documentação Bot Framework](https://docs.microsoft.com/bot-framework/)
- [Azure Bot Service Docs](https://docs.microsoft.com/azure/bot-service/)
- [Teams Platform Docs](https://docs.microsoft.com/microsoftteams/platform/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 💡 Dicas

### Desenvolvimento

```bash
# Recarregar automaticamente ao fazer mudanças
uvicorn bot.bot_api:app --reload

# Ver logs detalhados
# Configurar DEBUG=True no .env
```

### Produção

```bash
# Usar workers para performance
gunicorn bot.bot_api:app -w 4 -k uvicorn.workers.UvicornWorker

# Configurar Application Insights para monitoramento
# Adicionar APPLICATIONINSIGHTS_CONNECTION_STRING no Azure
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verificar documentação em `ANALISE_VIABILIDADE_TEAMS.md`
2. Consultar guia técnico em `INTEGRACAO_TEAMS.md`
3. Abrir issue no GitHub

---

**Última atualização:** 09/11/2025
