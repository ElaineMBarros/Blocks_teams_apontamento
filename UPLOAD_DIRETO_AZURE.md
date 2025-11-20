# 📤 UPLOAD DIRETO NO PORTAL AZURE

## Método 1: Via Kudu (Advanced Tools) - RECOMENDADO

### Passo 1: Acessar Kudu
1. Vá para: https://portal.azure.com
2. Login: DJTECHNOLOGYLTDA@DJTECHNOLOGYLTDA.onmicrosoft.com
3. Clique em "App Services"
4. Clique em "bot-apontamentos-dj"
5. No menu lateral, procure "Advanced Tools"
6. Clique em "Go →" (vai abrir em nova aba)

### Passo 2: Acessar o Console
1. Na página do Kudu, clique na aba "Debug console"
2. Escolha "CMD" ou "PowerShell"

### Passo 3: Navegar para a pasta
1. Você verá uma interface com pastas
2. Clique em: `site` > `wwwroot`
3. Esta é a pasta onde o código vai

### Passo 4: Fazer Upload
1. Na parte de cima da tela, você verá uma área de "Drag files here to upload"
2. **Arraste e solte** esses arquivos/pastas:
   - Pasta `bot/` (completa)
   - Arquivo `main.py`
   - Arquivo `requirements.txt`
   - Arquivo `startup.sh`
   - Arquivo `.env`

### Passo 5: Instalar Dependências
1. No console (parte de baixo), digite:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Passo 6: Reiniciar o App
Volte para o Portal Azure e:
1. Clique em "Overview"
2. Clique no botão "Restart" no topo

---

## Método 2: Via FTP (Alternativo)

### Obter Credenciais FTP
```bash
az webapp deployment list-publishing-credentials --name bot-apontamentos-dj --resource-group rg-bot-apontamentos
```

### Informações FTP:
- **Host:** Será algo como: ftps://waws-prod-cq1-xxx.ftp.azurewebsites.windows.net
- **Username:** bot-apontamentos-dj\$bot-apontamentos-dj
- **Password:** (será fornecida no comando acima)

### Usando FileZilla ou WinSCP:
1. Conecte-se ao FTP
2. Navegue até: `/site/wwwroot/`
3. Faça upload de todos os arquivos

---

## 📁 Arquivos para Upload:

### Estrutura Final no Azure:
```
/site/wwwroot/
├── bot/
│   ├── __init__.py
│   ├── bot_api.py
│   ├── ai_conversation.py
│   ├── adaptive_cards.py
│   ├── config.py
│   ├── models.py
│   └── session_manager.py
├── main.py
├── requirements.txt
├── startup.sh
└── .env
```

---

## ✅ Verificar se Funcionou

### Via Portal:
1. Vá para o App Service
2. Clique em "Log stream" (menu lateral)
3. Veja os logs em tempo real

### Via Navegador:
Abra: https://bot-apontamentos-dj.azurewebsites.net

---

## 🆘 Se Der Erro

### Ver logs:
```bash
az webapp log tail --name bot-apontamentos-dj --resource-group rg-bot-apontamentos
```

### Reiniciar:
```bash
az webapp restart --name bot-apontamentos-dj --resource-group rg-bot-apontamentos
```

---

## 🎯 PRÓXIMO PASSO APÓS UPLOAD

Quando os arquivos estiverem no Azure e o app funcionando:

1. **Registrar Bot Service**
2. **Configurar Credenciais**
3. **Conectar ao Teams**

Me avise quando terminar o upload!
