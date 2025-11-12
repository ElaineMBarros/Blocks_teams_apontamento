# 🚀 Guia de Início Rápido - Bot de Apontamentos Teams

**Comece a usar o bot em 5 minutos!**

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Python 3.11+ instalado
- ✅ Dados de apontamentos processados (arquivo CSV em `resultados/`)
- ✅ Git (opcional, para controle de versão)

---

## ⚡ Início Rápido (Teste Local)

### Passo 1: Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# OU instalar apenas o essencial para teste local
pip install -r requirements_minimal.txt
```

### Passo 2: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o `.env` (para teste local, pode deixar vazio):

```env
# Para teste local SEM Teams, deixe vazio
BOT_APP_ID=
BOT_APP_PASSWORD=

# Configurações da aplicação
PORT=8000
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO

# Nome do bot
BOT_NAME=Agente de Apontamentos
BOT_DESCRIPTION=Bot inteligente para consultas de apontamentos
```

### Passo 3: Testar o Agente Localmente

Antes de rodar o bot, teste o agente para garantir que os dados estão carregando:

```bash
python agente_apontamentos.py
```

Você deve ver:
```
✅ Dados carregados: XXX registros
✅ Agente inicializado com sucesso!
```

### Passo 4: Iniciar o Bot (Modo Desenvolvimento)

```bash
# Opção 1: Rodar diretamente
python -m bot.bot_api

# Opção 2: Usar uvicorn diretamente
uvicorn bot.bot_api:app --reload --port 8000
```

Você verá:
```
✅ Bot Framework Adapter configurado
✅ Agente de Apontamentos inicializado
🚀 Iniciando bot na porta 8000...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Passo 5: Testar os Endpoints

Abra seu navegador em:

**Health Check:**
```
http://localhost:8000/
```

Você deve ver:
```json
{
  "name": "Agente de Apontamentos",
  "description": "Bot inteligente para consultas de apontamentos",
  "version": "0.1.0",
  "status": "running",
  "agente_disponivel": true
}
```

**Health Check Detalhado:**
```
http://localhost:8000/health
```

---

## 🧪 Testando o Agente (Sem Teams)

Para testar a lógica do agente sem precisar do Teams:

```python
# Teste interativo
python agente_apontamentos.py

# OU criar um script de teste
python
>>> from agente_apontamentos import AgenteApontamentos
>>> agente = AgenteApontamentos()
>>> resultado = agente.responder_pergunta("Qual a média?")
>>> print(resultado['resposta'])
```

### Exemplos de Perguntas para Testar:

```python
# Estatísticas gerais
agente.responder_pergunta("Qual a média de horas?")
agente.responder_pergunta("Total de horas")

# Com nome de usuário (substitua por um nome real dos seus dados)
agente.responder_pergunta("Quanto trabalhei hoje?", "João Silva")
agente.responder_pergunta("Meu resumo semanal", "Maria Santos")

# Rankings e análises
agente.responder_pergunta("Mostrar ranking")
agente.responder_pergunta("Identificar outliers")
agente.responder_pergunta("Comparar semanas")
```

---

## 🔧 Teste com Bot Emulator (Recomendado)

Para testar a integração com Teams sem precisar fazer deploy:

### 1. Instalar Bot Framework Emulator

Download: https://github.com/Microsoft/BotFramework-Emulator/releases

### 2. Configurar no Emulator

1. Abra o Bot Framework Emulator
2. Clique em "Open Bot"
3. Configure:
   - **Bot URL:** `http://localhost:8000/api/messages`
   - **Microsoft App ID:** (deixe vazio para teste local)
   - **Microsoft App Password:** (deixe vazio para teste local)

### 3. Testar Mensagens

Envie mensagens no emulator:
- "oi" → Card de boas-vindas
- "ajuda" → Lista de comandos
- "média" → Estatísticas
- "ranking" → Top 10
- "outliers" → Apontamentos fora do padrão

---

## 📊 Verificando os Dados

Se o agente não estiver encontrando dados:

```bash
# Verificar se existe pasta resultados
ls resultados/

# Deve ter arquivo como:
# dados_com_duracao_YYYYMMDD_HHMMSS.csv
```

Se não tiver dados, você precisa gerar primeiro. Consulte a documentação do seu sistema de análise de apontamentos.

---

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'botbuilder'"

```bash
pip install botbuilder-core botbuilder-schema
```

### Erro: "Dados não disponíveis"

1. Verifique se existe a pasta `resultados/`
2. Verifique se há arquivos CSV na pasta
3. Execute o script que gera os dados primeiro

### Erro: "Port 8000 already in use"

```bash
# Mudar a porta no .env
PORT=8001

# Ou matar o processo na porta 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Bot não responde no Emulator

1. Verifique se o bot está rodando (`http://localhost:8000/`)
2. Verifique os logs no terminal
3. Certifique-se que a URL no emulator está correta
4. Tente reiniciar o bot e o emulator

---

## 📝 Próximos Passos

Após testar localmente com sucesso:

1. ✅ **[Você está aqui]** Teste local funcionando
2. 📱 [SETUP_LOCAL_BOT.md](SETUP_LOCAL_BOT.md) - Teste com Bot Emulator
3. ☁️ [DEPLOY_AZURE.md](DEPLOY_AZURE.md) - Deploy no Azure
4. 🎯 [INTEGRACAO_TEAMS.md](INTEGRACAO_TEAMS.md) - Integração final com Teams

---

## 🎯 Comandos Rápidos (Cheat Sheet)

```bash
# Instalar
pip install -r requirements.txt

# Testar agente
python agente_apontamentos.py

# Rodar bot
python -m bot.bot_api

# Testar health
curl http://localhost:8000/health

# Ver logs com mais detalhes
LOG_LEVEL=DEBUG python -m bot.bot_api
```

---

## 📚 Recursos Adicionais

- **Adaptive Cards Designer:** https://adaptivecards.io/designer/
- **Bot Framework Docs:** https://docs.microsoft.com/bot-framework/
- **Teams Platform Docs:** https://docs.microsoft.com/microsoftteams/platform/

---

## ✅ Checklist de Validação

Antes de prosseguir para o deploy:

- [ ] Bot inicia sem erros
- [ ] Health check retorna status "healthy"
- [ ] Agente carrega dados corretamente
- [ ] Teste no Bot Emulator funciona
- [ ] Cards são exibidos corretamente
- [ ] Comandos básicos respondem (média, ranking, etc.)
- [ ] Logs aparecem quando mensagens são processadas

---

## 🆘 Precisa de Ajuda?

1. Verifique os logs no terminal
2. Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Revise a [documentação oficial](https://docs.microsoft.com/bot-framework/)

---

**🎉 Parabéns!** Se chegou até aqui, seu bot está funcionando localmente!

Próximo passo: Testar com Bot Framework Emulator → [SETUP_LOCAL_BOT.md](SETUP_LOCAL_BOT.md)
