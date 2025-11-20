# 🚀 PRÓXIMOS PASSOS - DEPLOY AZURE

## ✅ JÁ CONCLUÍDO (70%):
1. ✅ Azure CLI configurado
2. ✅ Login realizado
3. ✅ Grupo de recursos criado (rg-bot-apontamentos)
4. ✅ App Service Plan criado (plan-bot-apontamentos)
5. ✅ Web App criado (bot-apontamentos-dj)
6. ✅ Configuração Python 3.11 aplicada
7. ✅ Startup script configurado

**URL:** https://bot-apontamentos-dj.azurewebsites.net

---

## 📋 FALTA FAZER (30%):

### PASSO 8: Deploy do Código via ZIP

```bash
# 1. Criar arquivo ZIP com o código
Compress-Archive -Path bot/,resultados/,requirements.txt,startup.sh,.env -DestinationPath deploy.zip -Force

# 2. Fazer deploy
az webapp deployment source config-zip --resource-group rg-bot-apontamentos --name bot-apontamentos-dj --src deploy.zip
```

### PASSO 9: Registrar Bot no Azure Bot Service

```bash
# Criar Bot Service
az bot create --resource-group rg-bot-apontamentos --name bot-apontamentos-dj --kind registration --endpoint "https://bot-apontamentos-dj.azurewebsites.net/api/messages" --app-type MultiTenant
```

### PASSO 10: Obter credenciais e configurar

```bash
# Obter App ID
az bot show --name bot-apontamentos-dj --resource-group rg-bot-apontamentos --query microsoftAppId -o tsv

# Criar App Password (no portal Azure)
# Configurar variáveis de ambiente
az webapp config appsettings set --name bot-apontamentos-dj --resource-group rg-bot-apontamentos --settings MicrosoftAppId="APP_ID_AQUI" MicrosoftAppPassword="PASSWORD_AQUI"
```

### PASSO 11: Conectar ao Teams

1. Ir ao Portal Azure
2. Abrir o Bot Service (bot-apontamentos-dj)
3. Configurar canal Microsoft Teams
4. Instalar no Teams

---

## 🎯 EXECUTE AGORA:

```powershell
# Passo 8a: Criar ZIP
Compress-Archive -Path bot/,resultados/,requirements.txt,startup.sh,.env -DestinationPath deploy.zip -Force

# Passo 8b: Deploy
az webapp deployment source config-zip --resource-group rg-bot-apontamentos --name bot-apontamentos-dj --src deploy.zip
```

Aguarde resultado e me avise!
