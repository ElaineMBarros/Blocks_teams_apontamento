# 🚀 ROTEIRO COMPLETO - DEPLOY BOT TEAMS NO AZURE (2025)

> **Status do Bot**: ✅ Testado localmente e funcionando perfeitamente  
> **Data**: 20/11/2025  
> **Recursos já prontos**: Web App `bot-apontamentos-dj` no Azure

---

## 📋 PRÉ-REQUISITOS

### ✅ O que você já tem:
- ✅ Código funcionando localmente
- ✅ Bot testado com Bot Framework Emulator
- ✅ Azure Web App criado: `bot-apontamentos-dj.azurewebsites.net`
- ✅ Resource Group: `rg-bot-apontamentos` (Brazil South)
- ✅ Repositório GitHub: `ElaineMBarros/Blocks_teams_apontamento`

### 🔑 Credenciais necessárias:
- ✅ Azure: `DJTECHNOLOGYLTDA@DJTECHNOLOGYLTDA.onmicrosoft.com`
- ✅ OpenAI API Key (já configurada no .env local)
- ⚠️ **IMPORTANTE**: Não suba o arquivo `.env` para o GitHub!

---

## 🎯 MÉTODO RECOMENDADO: GitHub Actions (CI/CD Automático)

Este é o método **MAIS PROFISSIONAL** e **MAIS FÁCIL DE MANTER**.

### VANTAGENS:
- ✅ Deploy automático a cada push no GitHub
- ✅ Controle de versão integrado
- ✅ Rollback fácil se algo der errado
- ✅ Logs centralizados
- ✅ Não precisa ZIP manual

---

## 📝 PASSO A PASSO

### **ETAPA 1: Preparar Arquivos para Azure**

#### 1.1. Criar arquivo `startup.sh` (se não existir)

```bash
#!/bin/bash
echo "🚀 Iniciando Bot de Apontamentos..."
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependências instaladas!"
echo "🤖 Iniciando aplicação..."
python -m uvicorn bot.bot_api:app --host 0.0.0.0 --port 8000
```

#### 1.2. Verificar `requirements.txt` atualizado

```bash
# Execute na raiz do projeto
pip freeze > requirements.txt
```

#### 1.3. Criar `.deployment` (na raiz do projeto)

```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

#### 1.4. Atualizar `.gitignore`

```
# Environment
.env
*.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/

# Azure
.azure/

# VS Code
.vscode/

# Data (não subir CSV para produção)
resultados/*.csv
!resultados/.gitkeep
```

---

### **ETAPA 2: Configurar Deploy via GitHub**

#### 2.1. Acessar Portal Azure

1. Abra: https://portal.azure.com
2. Login: `DJTECHNOLOGYLTDA@DJTECHNOLOGYLTDA.onmicrosoft.com`

#### 2.2. Configurar Deployment Center

1. Na busca, digite: `bot-apontamentos-dj`
2. Clique no Web App
3. Menu lateral → **Deployment Center**
4. Escolha **Source**: `GitHub`
5. Autorize acesso (se solicitado)
6. Configure:
   - **Organization**: `ElaineMBarros`
   - **Repository**: `Blocks_teams_apontamento`
   - **Branch**: `main`
7. Clique em **Save**

✅ **Pronto!** Azure criará automaticamente um GitHub Actions workflow.

#### 2.3. Verificar GitHub Actions

1. Vá para: https://github.com/ElaineMBarros/Blocks_teams_apontamento
2. Clique na aba **Actions**
3. Você verá um workflow executando o deploy

---

### **ETAPA 3: Upload do Arquivo CSV para Azure**

**IMPORTANTE**: O arquivo `dados_anonimizados_decupado_20251118_211544.csv` não deve ir para o GitHub (é muito grande).

#### Opção A: Upload via Azure Portal (RECOMENDADO)

1. Portal Azure → `bot-apontamentos-dj`
2. Menu lateral → **Advanced Tools** (Kudu)
3. Clique em **Go →**
4. No menu Kudu: **Debug console** → **CMD**
5. Navegue até: `site/wwwroot/`
6. Crie pasta: `resultados`
7. Arraste o arquivo CSV para upload

#### Opção B: Upload via Azure CLI

```powershell
# Fazer upload do CSV
az webapp deployment source config-zip `
  --resource-group rg-bot-apontamentos `
  --name bot-apontamentos-dj `
  --src resultados.zip
```

---

### **ETAPA 4: Configurar Variáveis de Ambiente no Azure**

#### 4.1. Definir configurações do App

```bash
az webapp config appsettings set `
  --name bot-apontamentos-dj `
  --resource-group rg-bot-apontamentos `
  --settings `
    OPENAI_API_KEY="sk-proj-..." `
    OPENAI_MODEL="gpt-4o-mini" `
    PORT="8000" `
    PYTHON_VERSION="3.11"
```

#### 4.2. Configurar Startup Command

```bash
az webapp config set `
  --name bot-apontamentos-dj `
  --resource-group rg-bot-apontamentos `
  --startup-file "startup.sh"
```

---

### **ETAPA 5: Registrar Bot no Azure Bot Service**

#### 5.1. Criar Bot Registration

```bash
az bot create `
  --resource-group rg-bot-apontamentos `
  --name bot-apontamentos-teams-dj `
  --kind registration `
  --endpoint "https://bot-apontamentos-dj.azurewebsites.net/api/messages" `
  --app-type MultiTenant `
  --sku F0
```

#### 5.2. Obter App ID

```bash
az bot show `
  --name bot-apontamentos-teams-dj `
  --resource-group rg-bot-apontamentos `
  --query microsoftAppId -o tsv
```

**Salve o App ID retornado!**

---

### **ETAPA 6: Criar App Password no Portal**

#### 6.1. Acessar App Registration

1. Portal Azure → Pesquise: **Microsoft Entra ID** (antigo Azure AD)
2. Menu lateral → **App registrations**
3. Clique em: `bot-apontamentos-teams-dj`

#### 6.2. Criar Secret

1. Menu lateral → **Certificates & secrets**
2. Clique em **New client secret**
3. Description: `Bot Password Prod`
4. Expires: `24 months`
5. Clique em **Add**
6. **COPIE O VALUE IMEDIATAMENTE** (só aparece uma vez!)

---

### **ETAPA 7: Atualizar Variáveis com Credenciais do Bot**

```bash
az webapp config appsettings set `
  --name bot-apontamentos-dj `
  --resource-group rg-bot-apontamentos `
  --settings `
    MicrosoftAppId="<APP_ID_COPIADO>" `
    MicrosoftAppPassword="<SECRET_COPIADO>"
```

---

### **ETAPA 8: Reiniciar e Testar**

#### 8.1. Reiniciar Web App

```bash
az webapp restart `
  --name bot-apontamentos-dj `
  --resource-group rg-bot-apontamentos
```

#### 8.2. Verificar Logs

```bash
az webapp log tail `
  --name bot-apontamentos-dj `
  --resource-group rg-bot-apontamentos
```

#### 8.3. Testar Endpoint

```powershell
curl https://bot-apontamentos-dj.azurewebsites.net
```

**Esperado**: Retornar algo (não erro 404)

---

### **ETAPA 9: Conectar ao Microsoft Teams**

#### 9.1. Configurar Canal Teams

1. Portal Azure → Pesquise: `bot-apontamentos-teams-dj`
2. Menu lateral → **Channels**
3. Clique no ícone **Microsoft Teams**
4. Aceite os termos
5. Clique em **Save**
6. Clique em **Open in Teams**

#### 9.2. Testar no Teams

1. Teams abrirá automaticamente
2. Digite: `olá`
3. Bot deve responder com mensagem de boas-vindas

---

## 🧪 TESTES DE VALIDAÇÃO

Execute estas consultas no Teams para validar:

1. ✅ **"olá"** → Deve cumprimentar
2. ✅ **"quantos apontamentos temos em outubro de 2025?"** → Deve retornar resumo
3. ✅ **"quantas pessoas apontaram no contrato 7873?"** → Deve listar recursos
4. ✅ **"abra os apontamentos do recurso RECURSO_1709652440 por dia?"** → Deve detalhar dia a dia

---

## 📊 MONITORAMENTO

### Ver logs em tempo real:

```bash
az webapp log tail --name bot-apontamentos-dj --resource-group rg-bot-apontamentos
```

### Ver métricas no Portal:

1. Portal Azure → `bot-apontamentos-dj`
2. Menu lateral → **Monitoring** → **Metrics**
3. Adicionar métricas:
   - HTTP requests
   - Response time
   - CPU usage
   - Memory usage

---

## 🔒 SEGURANÇA

### ✅ Checklist de Segurança:

- [ ] `.env` não está no GitHub
- [ ] `MicrosoftAppPassword` configurado como Application Setting (não no código)
- [ ] `OPENAI_API_KEY` configurado como Application Setting
- [ ] CSV com dados sensíveis não está no GitHub
- [ ] Bot responde apenas a consultas sobre apontamentos
- [ ] Prompt de segurança com 10 camadas ativo

---

## 🚨 SOLUÇÃO DE PROBLEMAS

### ❌ Bot não responde no Teams

**Diagnóstico:**
```bash
# Ver logs
az webapp log tail --name bot-apontamentos-dj --resource-group rg-bot-apontamentos
```

**Possíveis causas:**
1. Endpoint incorreto → Verificar URL em Bot Registration
2. Credenciais erradas → Re-validar AppId e Password
3. CSV não encontrado → Fazer upload via Kudu
4. Timeout → Aumentar timeout no Azure (Settings → Configuration)

### ❌ Deploy falha no GitHub Actions

**Solução:**
1. GitHub → Actions → Clicar no workflow com erro
2. Ver logs detalhados
3. Problemas comuns:
   - `requirements.txt` incompleto → `pip freeze > requirements.txt`
   - Versão Python errada → Especificar 3.11 no workflow

### ❌ Bot retorna erro 500

**Diagnóstico:**
```bash
# Ver logs de aplicação
az webapp log download --name bot-apontamentos-dj --resource-group rg-bot-apontamentos --log-file logs.zip
```

**Possíveis causas:**
1. Variável de ambiente faltando (OPENAI_API_KEY, etc)
2. CSV não encontrado
3. Erro no código → Verificar logs

---

## 📈 PRÓXIMOS PASSOS (OPCIONAL)

### 1. Configurar Scaling Automático

```bash
az appservice plan update `
  --name plan-bot-apontamentos `
  --resource-group rg-bot-apontamentos `
  --sku B1  # Upgrade para Basic tier
```

### 2. Configurar Application Insights

```bash
az monitor app-insights component create `
  --app bot-insights `
  --location brazilsouth `
  --resource-group rg-bot-apontamentos
```

### 3. Criar Ambiente de Staging

```bash
az webapp deployment slot create `
  --name bot-apontamentos-dj `
  --resource-group rg-bot-apontamentos `
  --slot staging
```

---

## 📚 RECURSOS ÚTEIS

- **Portal Azure**: https://portal.azure.com
- **Bot Framework Documentation**: https://docs.microsoft.com/bot-framework/
- **Azure App Service Docs**: https://docs.microsoft.com/azure/app-service/
- **Teams Bot Samples**: https://github.com/microsoft/BotBuilder-Samples

---

## ✅ CHECKLIST FINAL

### Deploy:
- [ ] Código no GitHub atualizado
- [ ] GitHub Actions configurado e executado com sucesso
- [ ] CSV uploadado para Azure
- [ ] Variáveis de ambiente configuradas

### Bot Registration:
- [ ] Bot criado no Azure Bot Service
- [ ] App ID obtido
- [ ] App Password criado
- [ ] Credenciais configuradas no Web App

### Teams:
- [ ] Canal Teams habilitado
- [ ] Bot testado no Teams
- [ ] Consultas básicas funcionando

### Segurança:
- [ ] `.env` não está no repositório público
- [ ] Secrets armazenados como Application Settings
- [ ] Prompt de segurança ativo

---

**🎉 Seu bot está pronto para produção!**

> **Dúvidas?** Consulte os logs: `az webapp log tail --name bot-apontamentos-dj --resource-group rg-bot-apontamentos`

---

**Autor**: GitHub Copilot  
**Data**: 20/11/2025  
**Versão do Bot**: v2.0 (com detalhamento por dia, contratos INTERNOS/EXTERNOS)
