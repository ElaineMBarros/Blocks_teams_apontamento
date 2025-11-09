# 🤖 Setup Local - Bot Framework

## 📋 Guia Completo para Testar Bot Localmente

Este guia explica como configurar e testar o bot localmente antes do deploy.

---

## 🎯 O que você precisa

### 1. Visual C++ Build Tools (Windows)
**Necessário para:** Compilar dependências do aiohttp e Bot Framework

**Download:**
```
https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Instalação:**
1. Baixe o instalador
2. Execute e selecione:
   - ✅ Desenvolvimento para Desktop com C++
   - ✅ MSVC v143 - VS 2022 C++ x64/x86
   - ✅ Windows 10/11 SDK
3. Instale (pode demorar ~20 minutos)
4. Reinicie o computador

---

### 2. Bot Framework Emulator
**Para:** Testar o bot localmente sem Teams

**Download:**
```
https://github.com/Microsoft/BotFramework-Emulator/releases
```

**Versão Recomendada:** Bot-Framework-Emulator-4.14.1-windows-setup.exe

**Instalação:**
1. Baixe o instalador (.exe)
2. Execute e siga as instruções
3. Inicie o Bot Framework Emulator

---

### 3. ngrok (Opcional - para testes com Teams real)
**Para:** Expor bot local para internet (necessário para Teams)

**Download:**
```
https://ngrok.com/download
```

**Setup:**
```bash
# 1. Extrair ngrok.exe
# 2. Criar conta em https://ngrok.com (grátis)
# 3. Obter authtoken
# 4. Configurar
ngrok config add-authtoken SEU_TOKEN_AQUI
```

---

## 🚀 Passo a Passo - Configuração

### Etapa 1: Instalar Dependências Completas

Após instalar o Visual C++ Build Tools:

```bash
# 1. Ativar ambiente virtual
.\venv\Scripts\activate

# 2. Atualizar pip
python -m pip install --upgrade pip

# 3. Instalar dependências completas
pip install -r requirements.txt

# Isso vai instalar:
# - botbuilder-core
# - botbuilder-schema  
# - botbuilder-integration-aiohttp
# - aiohttp
# - Todas as outras dependências
```

**Verificar instalação:**
```bash
python -c "import aiohttp; print('aiohttp OK')"
python -c "from botbuilder.core import BotFrameworkAdapter; print('Bot Framework OK')"
```

---

### Etapa 2: Criar Arquivo .env

```bash
# Copiar exemplo
copy .env.example .env

# Editar .env
notepad .env
```

**Configuração para testes locais:**
```env
# Deixe vazio para testes sem autenticação
BOT_APP_ID=
BOT_APP_PASSWORD=
BOT_TENANT_ID=

# Dados do Fabric (seus dados reais)
FABRIC_ENDPOINT=seu-endpoint.datawarehouse.fabric.microsoft.com
FABRIC_DATABASE=seu-database

# Config local
PORT=3978
DEBUG=True
ENVIRONMENT=development
```

---

### Etapa 3: Rodar o Bot

```bash
# Opção A: Usando bot_api.py (Bot Framework completo)
python -m bot.bot_api

# Opção B: Usando test_api.py (simplificado)
python test_api.py
```

**Saída esperada:**
```
🚀 Iniciando bot na porta 3978...
✅ Bot Framework Adapter configurado
✅ Agente de Apontamentos inicializado
INFO: Uvicorn running on http://0.0.0.0:3978
```

---

## 🧪 Testes com Bot Framework Emulator

### 1. Abrir Bot Framework Emulator

### 2. Conectar ao Bot Local

**Configuração:**
```
Bot URL: http://localhost:3978/api/messages
Microsoft App ID: (deixe vazio)
Microsoft App Password: (deixe vazio)
```

**Clique em:** "Connect"

### 3. Testar Conversas

**Envie mensagens:**
```
Você: oi
Bot: [Card de boas-vindas]

Você: qual a média de horas?
Bot: [Resposta com estatísticas]

Você: ranking
Bot: [Ranking de funcionários]
```

### 4. Ver Logs

O emulador mostra:
- ✅ Mensagens enviadas
- ✅ Respostas do bot
- ✅ JSON completo
- ✅ Erros (se houver)

---

## 🌐 Testes com Teams Real (Local)

### Etapa 1: Expor Bot com ngrok

```bash
# Terminal 1: Iniciar bot
python -m bot.bot_api

# Terminal 2: Iniciar ngrok
ngrok http 3978
```

**ngrok mostrará:**
```
Forwarding: https://abc123.ngrok.io -> http://localhost:3978
```

### Etapa 2: Registrar Bot no Azure

```bash
# 1. Login
az login

# 2. Criar Bot Registration
az bot create \
  --resource-group rg-bot-test \
  --name bot-apontamentos-local \
  --kind registration \
  --endpoint https://abc123.ngrok.io/api/messages \
  --sku F0
```

### Etapa 3: Obter Credenciais

```bash
# Obter App ID e Password
az bot show --name bot-apontamentos-local --resource-group rg-bot-test
```

### Etapa 4: Atualizar .env

```env
BOT_APP_ID=seu-app-id-aqui
BOT_APP_PASSWORD=sua-senha-aqui
```

### Etapa 5: Reiniciar Bot

```bash
# Ctrl+C para parar
# Iniciar novamente
python -m bot.bot_api
```

### Etapa 6: Testar no Teams

1. Portal Azure > Bot Registration
2. Channels > Microsoft Teams > Configurar
3. Abrir bot no Teams
4. Enviar mensagens

---

## 🔧 Troubleshooting

### Erro: "Microsoft Visual C++ 14.0 or greater is required"

**Solução:**
```bash
# 1. Instalar Build Tools
https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. Reiniciar computador
# 3. Tentar instalar novamente
pip install -r requirements.txt
```

### Erro: "Bot adapter não configurado"

**Causa:** BOT_APP_ID e BOT_APP_PASSWORD não configurados

**Solução para testes locais:**
```python
# bot/config.py - permitir vazio
if not cls.BOT_APP_ID:
    print("⚠️ Rodando sem autenticação (apenas desenvolvimento)")
```

### Erro: "Cannot connect to bot"

**Checklist:**
- [ ] Bot está rodando?
- [ ] Porta correta (3978)?
- [ ] URL correta no emulador?
- [ ] Firewall bloqueando?

### Bot não responde no Teams

**Checklist:**
- [ ] ngrok está rodando?
- [ ] URL ngrok configurada no Azure?
- [ ] BOT_APP_ID e PASSWORD corretos?
- [ ] Canal Teams ativado no Azure?

---

## 📁 Estrutura de Arquivos

```
blocks_teams/
├── bot/
│   ├── __init__.py
│   ├── config.py           # Configurações
│   ├── bot_api.py          # Bot completo (use este)
│   ├── adaptive_cards.py   # Cards do Teams
│   └── models.py           # Modelos Pydantic
├── test_api.py             # API simplificada (testes)
├── .env                    # Suas credenciais
├── .env.example            # Template
└── requirements.txt        # Dependências completas
```

---

## 🎯 Fluxo de Desenvolvimento

### 1. Desenvolvimento Inicial
```bash
# Use test_api.py (sem Bot Framework)
python test_api.py
# Acesse: http://localhost:8000/docs
```

### 2. Testes com Emulador
```bash
# Use bot_api.py (Bot Framework completo)
python -m bot.bot_api
# Conecte Bot Framework Emulator
```

### 3. Testes com Teams Local
```bash
# Bot + ngrok
python -m bot.bot_api  # Terminal 1
ngrok http 3978        # Terminal 2
# Configure Azure + Teams
```

### 4. Deploy Produção
```bash
# Deploy no Azure
az webapp up --name bot-apontamentos
# Configure Teams Channel
```

---

## 📊 Comparação de Opções

| Opção | Pros | Contras | Uso |
|-------|------|---------|-----|
| **test_api.py** | ✅ Rápido<br>✅ Sem dependências C++<br>✅ Swagger | ❌ Sem Bot Framework<br>❌ Sem Teams | Desenvolvimento inicial |
| **Bot Emulator** | ✅ Testa Bot Framework<br>✅ Debug completo<br>✅ Sem internet | ❌ Precisa Build Tools<br>❌ Não é Teams real | Testes de integração |
| **ngrok + Teams** | ✅ Teams real<br>✅ Testa tudo | ❌ Precisa Azure<br>❌ Mais complexo | Testes finais |
| **Azure Deploy** | ✅ Produção<br>✅ Sem config local | ❌ Custo<br>❌ Deploy mais lento | Produção |
|

---

## 💡 Dicas

### Para Desenvolvimento Rápido

1. **Use test_api.py primeiro**
   - Desenvolva lógica de negócio
   - Teste com Swagger
   - Sem complicações

2. **Depois use Bot Emulator**
   - Teste Adaptive Cards
   - Valide conversas
   - Debug

3. **Por último, Teams real**
   - Validação final
   - UX completa

### Para Debug

```python
# Habilitar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Para Performance

```python
# Usar cache Redis (opcional)
import redis
r = redis.Redis(host='localhost', port=6379)
```

---

## 🔐 Segurança

### Local (Desenvolvimento)

```env
# .env (nunca commitar)
BOT_APP_ID=development-only
BOT_APP_PASSWORD=local-testing
```

### Produção

```bash
# Usar Azure Key Vault
az keyvault secret set \
  --vault-name meu-vault \
  --name bot-app-password \
  --value "senha-segura"

# Referenciar no código
from azure.keyvault.secrets import SecretClient
```

---

## 📚 Recursos

### Documentação
- **Bot Framework:** https://docs.microsoft.com/bot-framework/
- **Bot Emulator:** https://github.com/Microsoft/BotFramework-Emulator
- **ngrok:** https://ngrok.com/docs
- **FastAPI:** https://fastapi.tiangolo.com/

### Exemplos
- **Bot Samples:** https://github.com/microsoft/BotBuilder-Samples
- **Teams Samples:** https://github.com/OfficeDev/Microsoft-Teams-Samples

### Comunidade
- **Stack Overflow:** [botframework] tag
- **GitHub Discussions:** BotBuilder-Samples
- **Teams Developer:** https://developer.microsoft.com/microsoft-teams

---

## ✅ Checklist Final

### Antes de Começar
- [ ] Visual C++ Build Tools instalado
- [ ] Bot Framework Emulator instalado
- [ ] Python 3.11+ instalado
- [ ] Git configurado

### Setup Inicial
- [ ] Repositório clonado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] .env configurado

### Testes Locais
- [ ] test_api.py funcionando
- [ ] bot_api.py rodando
- [ ] Bot Emulator conectado
- [ ] Conversas testadas

### Deploy (Quando pronto)
- [ ] Azure configurado
- [ ] Bot registrado
- [ ] Teams channel ativado
- [ ] Usuários testando

---

## 🆘 Suporte

### Se tiver problemas:

1. **Verificar logs**
   ```bash
   # Console mostra erros detalhados
   ```

2. **Testar dependências**
   ```bash
   python -c "import aiohttp"
   python -c "from botbuilder.core import BotFrameworkAdapter"
   ```

3. **Reinstalar se necessário**
   ```bash
   pip uninstall aiohttp botbuilder-core
   pip install -r requirements.txt --force-reinstall
   ```

4. **Consultar documentação**
   - INSTALL.md
   - SWAGGER_API.md
   - TESTE_RESULTADO.md

---

**Última atualização:** 09/11/2025  
**Versão:** 1.0.0

**Próximo passo recomendado:** Instalar Visual C++ Build Tools e testar com Bot Framework Emulator! 🚀
