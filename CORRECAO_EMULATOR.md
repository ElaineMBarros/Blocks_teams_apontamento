# 🔧 Correção - Bot Framework Emulator

## ❌ Problema Identificado

O Emulator está tentando conectar em `http://localhost:8000/` mas o endpoint correto é `http://localhost:8000/api/messages`.

**Logs do erro:**
```
POST 400 directline/conversations/<conversationId>/activities
```

---

## ✅ Solução

### Passo a Passo para Configurar Corretamente

1. **Fechar a conexão atual** no Emulator (se estiver aberta)

2. **Clicar em "Open Bot"** ou "New Bot Configuration"

3. **Configurar EXATAMENTE assim:**

```
Bot URL: http://localhost:8000/api/messages
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         IMPORTANTE: Incluir /api/messages no final!

Microsoft App ID: [deixar vazio]
Microsoft App password: [deixar vazio]
```

4. **Clicar em "Connect"**

5. **Testar enviando:** `oi`

---

## 🎯 Endpoints Corretos

| Endpoint | Uso |
|----------|-----|
| `http://localhost:8000/` | Health check (navegador) |
| `http://localhost:8000/health` | Status detalhado |
| `http://localhost:8000/api/messages` | **Bot Framework Emulator** ← Use este! |

---

## 🔍 Verificação

Se configurado corretamente, você verá:

1. **No Emulator:**
   - Status: "Connected"
   - Mensagens enviadas aparecem
   - Bot responde com Adaptive Cards

2. **No Terminal do Bot:**
   ```
   INFO: 127.0.0.1:xxxxx - "POST /api/messages HTTP/1.1" 200 OK
   📨 Mensagem de [seu nome]: oi
   ```

---

## 📱 Teste Rápido

Após conectar corretamente:

```
Você: oi
Bot: [Card de Boas-vindas com botões]

Você: ajuda
Bot: [Card de Ajuda com comandos]

Você: média
Bot: [Card de Erro - "Dados não disponíveis"]
```

---

## 🐛 Se Ainda Não Funcionar

### Opção 1: Verificar se o bot está rodando

```bash
# Em outro terminal
curl http://localhost:8000/health
```

Deve retornar:
```json
{"status":"healthy","bot_configured":true, ...}
```

### Opção 2: Ver logs do bot

No terminal onde o bot está rodando, você deve ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Opção 3: Reiniciar tudo

```bash
# 1. Para o bot (CTRL+C no terminal)
# 2. Reinicia
uvicorn bot.bot_api:app --host 0.0.0.0 --port 8000 --reload
# 3. Fecha e reabre o Emulator
# 4. Conecta novamente em http://localhost:8000/api/messages
```

---

## 📸 Exemplo de Configuração Correta

```
┌─────────────────────────────────────────┐
│  Bot Framework Emulator                 │
├─────────────────────────────────────────┤
│  Bot URL:                               │
│  http://localhost:8000/api/messages     │
│                                         │
│  Microsoft App ID:                      │
│  [vazio - deixe em branco]              │
│                                         │
│  Microsoft App password:                │
│  [vazio - deixe em branco]              │
│                                         │
│  [Connect]                              │
└─────────────────────────────────────────┘
```

---

## ✅ Sucesso Esperado

Quando conectar corretamente:

1. **Status muda para "Connected"**
2. **Você pode enviar mensagens**
3. **Bot responde com Adaptive Cards bonitos**
4. **Logs aparecem no terminal do bot**

---

## 💡 Dica

Se quiser testar sem o Emulator, pode usar `curl`:

```bash
# Teste o endpoint
curl -X POST http://localhost:8000/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "text": "oi",
    "from": {"id": "user1", "name": "Test User"},
    "recipient": {"id": "bot1", "name": "Bot"}
  }'
```

Mas o Emulator é muito melhor para visualizar os Adaptive Cards!

---

**🔄 Tente novamente com a URL correta: `http://localhost:8000/api/messages`**
