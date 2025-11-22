# 🚀 GUIA DE DEPLOY - Railway + HostGator

## 📦 PARTE 1: Deploy da API no Railway (Back-end)

### Passo 1: Preparar o repositório GitHub
1. Commite os arquivos atualizados:
```bash
git add .
git commit -m "Preparar para deploy Railway - API independente"
git push origin main
```

### Passo 2: Criar conta no Railway
1. Acesse: https://railway.app
2. Clique em **"Login"**
3. Escolha **"Login with GitHub"**
4. Autorize o Railway a acessar sua conta GitHub

### Passo 3: Criar novo projeto
1. No dashboard do Railway, clique **"New Project"**
2. Escolha **"Deploy from GitHub repo"**
3. Selecione o repositório: **Blocks_teams_apontamento**
4. Railway vai detectar automaticamente que é Python

### Passo 4: Configurar variáveis de ambiente
1. Na tela do projeto, clique na aba **"Variables"**
2. Adicione:
   - `PORT` = `8001` (Railway vai usar automaticamente)
   - `PYTHON_VERSION` = `3.11`

### Passo 5: Configurar build
1. Clique em **"Settings"**
2. Em **"Build Command"**, deixe vazio (Railway usa railway.json)
3. Em **"Start Command"**, deixe vazio (Railway usa railway.json)
4. Verifique se o arquivo `railway.json` está no repositório

### Passo 6: Deploy automático
1. Railway vai fazer deploy automático
2. Aguarde 3-5 minutos
3. Quando aparecer ✅ **"Success"**, clique em **"Generate Domain"**
4. Copie a URL gerada (ex: `blocks-api-production.up.railway.app`)

### Passo 7: Testar a API
Acesse no navegador:
```
https://SUA-URL-RAILWAY.up.railway.app/
```

Deve aparecer: `{"message":"Bot de Apontamentos API - Rodando!"}`

---

## 🌐 PARTE 2: Deploy do Front-end na HostGator

### Passo 1: Atualizar URL da API no HTML
1. Abra o arquivo `webchat_direto.html`
2. Procure a linha (aproximadamente linha 474):
```javascript
const API_URL = 'http://localhost:8001';
```
3. Substitua por:
```javascript
const API_URL = 'https://SUA-URL-RAILWAY.up.railway.app';
```
4. Salve o arquivo

### Passo 2: Acessar cPanel da HostGator
1. Acesse: `https://seudominio.com.br/cpanel`
2. Entre com usuário e senha

### Passo 3: Upload do arquivo
1. No cPanel, procure **"Gerenciador de Arquivos"** (File Manager)
2. Navegue até a pasta **"public_html"**
3. Clique em **"Upload"**
4. Selecione o arquivo `webchat_direto.html`
5. Aguarde o upload completar

### Passo 4: Testar o site
Acesse no navegador:
```
https://seudominio.com.br/webchat_direto.html
```

---

## ✅ Verificações Finais

### API (Railway):
- [ ] Deploy com sucesso (status verde)
- [ ] URL gerada está acessível
- [ ] Endpoint `/` retorna mensagem JSON
- [ ] Logs não mostram erros

### Front-end (HostGator):
- [ ] Arquivo uploaded com sucesso
- [ ] Página carrega no navegador
- [ ] Chat aparece corretamente
- [ ] Consegue enviar mensagens
- [ ] Bot responde às perguntas

---

## 🐛 Troubleshooting

### Problema: Railway não encontra requirements
**Solução:** Renomeie `requirements_railway.txt` para `requirements.txt` no commit

### Problema: CORS error no front-end
**Solução:** Verifique se `allow_origins=["*"]` está no `api_simples.py`

### Problema: Bot não responde
**Solução:** 
1. Verifique os logs no Railway
2. Confirme se o CSV foi carregado
3. Teste o endpoint `/chat` com Postman

### Problema: CSV não foi carregado
**Solução:** 
1. Certifique-se que `dados_anonimizados_decupado_20251118_211544.csv` está no repositório
2. Verifique o caminho no `api_simples.py`

---

## 📊 Arquivos necessários no repositório

```
Blocks_teams_apontamento/
├── api_simples.py              ✅ (API principal)
├── agente_apontamentos.py      ✅ (Lógica do agente)
├── bot/
│   ├── __init__.py             ✅
│   ├── ai_conversation.py      ✅
│   ├── session_manager.py      ✅
│   └── config.py               ✅
├── resultados/
│   └── dados_anonimizados_decupado_20251118_211544.csv ✅
├── requirements_railway.txt    ✅ (Dependências mínimas)
├── railway.json                ✅ (Config Railway)
└── webchat_direto.html        ✅ (Para HostGator)
```

---

## 🎯 Resumo do que vai acontecer:

1. **Railway detecta Python** → Instala dependências
2. **Railway roda** → `uvicorn api_simples:app --host 0.0.0.0 --port $PORT`
3. **API fica disponível** → URL gerada pelo Railway
4. **HostGator serve HTML** → Faz requisições para Railway
5. **Usuário acessa** → `seudominio.com.br/webchat_direto.html`

---

## 💰 Custos:

- **Railway**: Gratuito (500h/mês)
- **HostGator**: Você já paga

**Total adicional**: R$ 0,00 🎉

---

Qualquer dúvida, estou aqui! 🚀
