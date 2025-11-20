# 🚀 GUIA COMPLETO - PUBLICAR BOT NO AZURE

## ✅ PROGRESSO ATUAL: 70% COMPLETO

### O que já está pronto:
- ✅ Azure CLI configurado
- ✅ Login realizado (DJTECHNOLOGYLTDA@DJTECHNOLOGYLTDA.onmicrosoft.com)
- ✅ Grupo de recursos: `rg-bot-apontamentos` (Brazil South)
- ✅ App Service Plan: `plan-bot-apontamentos` (Free tier)
- ✅ Web App: `bot-apontamentos-dj`
- ✅ URL: https://bot-apontamentos-dj.azurewebsites.net

### Problema encontrado:
❌ Deploy via ZIP falhou - Precisa ajustar estrutura

---

## 🔧 SOLUÇÃO - DEPLOY ALTERNATIVO

### OPÇÃO 1: Deploy via Portal Azure (RECOMENDADO - Mais fácil!)

#### Passo 1: Acessar Portal Azure
1. Abra: https://portal.azure.com
2. Entre com: DJTECHNOLOGYLTDA@DJTECHNOLOGYLTDA.onmicrosoft.com

#### Passo 2: Localizar o Web App
1. No menu lateral, clique em "App Services"
2. Clique em "bot-apontamentos-dj"

#### Passo 3: Configurar Deployment Center
1. No menu lateral do App Service, procure por "Deployment Center"
2. Clique em "Deployment Center"
3. Escolha: **GitHub** (se seu código está no GitHub) ou **Local Git**

#### Passo 4a: Se escolher GitHub
1. Clique em "GitHub"
2. Autorize acesso
3. Escolha o repositório: ElaineMBarros/Blocks_teams_apontamento
4. Branch: main
5. Clique em "Save"
6. Azure automaticamente fará deploy do código

#### Passo 4b: Se escolher Local Git
```bash
# 1. Obter URL do Git remote
az webapp deployment source config-local-git --name bot-apontamentos-dj --resource-group rg-bot-apontamentos

# 2. Adicionar remote (vai retornar uma URL tipo https://...)
git remote add azure <URL_RETORNADA>

# 3. Push para Azure
git push azure main
```

---

### OPÇÃO 2: Deploy via VS Code (MAIS SIMPLES!)

#### Passo 1: Instalar Extensão Azure
1. Abra VS Code
2. Clique em Extensions (Ctrl+Shift+X)
3. Procure: "Azure App Service"
4. Instale a extensão oficial da Microsoft

#### Passo 2: Deploy direto do VS Code
1. Clique no ícone do Azure na barra lateral
2. Faça login com sua conta
3. Expanda "App Services"
4. Clique com botão direito em "bot-apontamentos-dj"
5. Clique em "Deploy to Web App"
6. Selecione a pasta do projeto
7. Confirme o deploy

---

### OPÇÃO 3: Ajustar e tentar ZIP novamente

#### Problema identificado:
O Azure precisa de um ponto de entrada claro. Vamos criar:

#### Arquivo: `main.py` (criar na raiz do projeto)
```python
from bot.bot_api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Atualizar startup.sh:
```bash
#!/bin/bash
pip install -r requirements.txt
python main.py
```

#### Recriar ZIP e tentar novamente:
```powershell
# Criar novo ZIP
Compress-Archive -Path bot/,resultados/,requirements.txt,startup.sh,main.py,.env -DestinationPath deploy.zip -Force

# Deploy
az webapp deployment source config-zip --resource-group rg-bot-apontamentos --name bot-apontamentos-dj --src deploy.zip
```

---

## 🤖 DEPOIS DO DEPLOY BEM-SUCEDIDO

### Passo 5: Registrar Bot no Azure Bot Service

```bash
# Criar Bot Registration
az bot create \
  --resource-group rg-bot-apontamentos \
  --name bot-apontamentos-teams \
  --kind registration \
  --endpoint "https://bot-apontamentos-dj.azurewebsites.net/api/messages" \
  --app-type MultiTenant
```

### Passo 6: Obter Credenciais

```bash
# Ver App ID
az bot show --name bot-apontamentos-teams --resource-group rg-bot-apontamentos --query microsoftAppId -o tsv
```

### Passo 7: Criar App Password

**IMPORTANTE: Faça isso no Portal Azure**

1. Vá para: https://portal.azure.com
2. Procure por "Azure Active Directory" ou "Microsoft Entra ID"
3. Clique em "App registrations"
4. Encontre o app do bot
5. Vá em "Certificates & secrets"
6. Clique em "New client secret"
7. Copie o valor (só aparece uma vez!)

### Passo 8: Configurar Variáveis de Ambiente

```bash
az webapp config appsettings set \
  --name bot-apontamentos-dj \
  --resource-group rg-bot-apontamentos \
  --settings \
    MicrosoftAppId="COLE_APP_ID_AQUI" \
    MicrosoftAppPassword="COLE_PASSWORD_AQUI" \
    OPENAI_API_KEY="sk-..." \
    AZURE_OPENAI_ENDPOINT="https://..." \
    AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

### Passo 9: Reiniciar App

```bash
az webapp restart --name bot-apontamentos-dj --resource-group rg-bot-apontamentos
```

### Passo 10: Conectar ao Teams

1. Vá para: https://portal.azure.com
2. Procure: "bot-apontamentos-teams"
3. No menu lateral, clique em "Channels"
4. Clique no ícone do Microsoft Teams
5. Clique em "Save"
6. Clique em "Open in Teams" para testar

---

## 🔍 VERIFICAR SE ESTÁ FUNCIONANDO

### Testar endpoint:
```bash
# Deve retornar algo
curl https://bot-apontamentos-dj.azurewebsites.net
```

### Ver logs em tempo real:
```bash
az webapp log tail --name bot-apontamentos-dj --resource-group rg-bot-apontamentos
```

---

## 📊 CHECKLIST FINAL

- [ ] Deploy realizado com sucesso
- [ ] Bot Registration criado
- [ ] App ID obtido
- [ ] App Password criado
- [ ] Variáveis de ambiente configuradas
- [ ] App reiniciado
- [ ] Canal Teams configurado
- [ ] Bot testado no Teams

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### Se o deploy continuar falhando:
1. Use a **Opção 1** (Deploy via Portal Azure + GitHub) - É a mais confiável
2. Ou use a **Opção 2** (VS Code Extension) - Muito simples

### Se o bot não responder:
1. Verifique logs: `az webapp log tail --name bot-apontamentos-dj --resource-group rg-bot-apontamentos`
2. Confirme que as variáveis de ambiente estão configuradas
3. Verifique se o endpoint está acessível

### Se não conseguir registrar no Bot Service:
- Problema comum: Nome já existe
- Solução: Use um nome diferente: `bot-apontamentos-teams-dj`

---

## 🎯 RECOMENDAÇÃO

**Use a OPÇÃO 1 (Deploy via Portal Azure com GitHub)**

É o método mais confiável e fácil:
1. Todo o código já está no GitHub
2. Azure automatiza tudo
3. Atualizações futuras são automáticas (push no GitHub = deploy automático)

---

**Criado em:** 19/11/2025 19:24  
**Status:** Web App criado, aguardando deploy do código  
**Próximo passo:** Escolher método de deploy e executar
