# 🧪 TESTE DE MULTISESSÃO COM MÚLTIPLAS INSTÂNCIAS DO BOT FRAMEWORK EMULATOR

## ✅ SIM! VOCÊ PODE TESTAR COM MÚLTIPLOS EMULADORES

É possível abrir várias instâncias do Bot Framework Emulator simultaneamente para testar o isolamento de sessões!

---

## 📋 COMO TESTAR

### **Passo 1: Inicie o Bot**
```bash
python -m uvicorn bot.bot_api:app --reload --port 3978
```

### **Passo 2: Abra Múltiplas Instâncias do Emulator**

**Opção A - Abrir Múltiplas Janelas:**
1. Abra o Bot Framework Emulator normalmente
2. No menu: **File → New Bot Configuration** ou **Ctrl+N**
3. Conecte ao endpoint: `http://localhost:3978/api/messages`
4. Repita para abrir mais conversas (cada aba/janela é uma sessão diferente)

**Opção B - Executar Múltiplas Instâncias do Emulator:**
1. Abra o primeiro Bot Framework Emulator
2. Conecte ao bot: `http://localhost:3978/api/messages`
3. Abra uma NOVA instância do executável do Bot Framework Emulator
4. Conecte novamente ao mesmo endpoint
5. Repita quantas vezes quiser!

---

## 🔍 O QUE TESTAR

### **Teste 1: Isolamento de Conversas**

**No Emulator 1:**
```
Você: Meu nome é João e meu CPF é 123.456.789-00
Bot: [salva na sessão 1]
Você: Qual é meu nome?
Bot: Seu nome é João
```

**No Emulator 2 (simultaneamente):**
```
Você: Meu nome é Maria e meu CPF é 987.654.321-00
Bot: [salva na sessão 2]
Você: Qual é meu nome?
Bot: Seu nome é Maria
```

**Volte ao Emulator 1:**
```
Você: Qual é meu nome?
Bot: Seu nome é João ✅ (não deve retornar "Maria")
```

---

### **Teste 2: Contextos Independentes**

**Emulator 1:**
```
Você: Quais são meus apontamentos em outubro?
Bot: [retorna dados de João]
```

**Emulator 2:**
```
Você: Quais são meus apontamentos em outubro?
Bot: [retorna dados de Maria]
```

Cada sessão deve manter seus próprios dados!

---

### **Teste 3: Sessões Simultâneas**

Faça perguntas alternadamente nos emuladores para verificar:
- ✅ As respostas não se misturam
- ✅ Cada conversa mantém seu próprio contexto
- ✅ O bot processa múltiplas requisições simultâneas

---

## 🔎 VERIFICAR LOGS

### **No Terminal do Bot:**
Você verá logs diferentes para cada conversation_id:

```
INFO: Mensagem recebida - Conversation ID: conversation-abc123
INFO: Mensagem recebida - Conversation ID: conversation-xyz789
INFO: Processando para usuário: João (conversation-abc123)
INFO: Processando para usuário: Maria (conversation-xyz789)
```

### **No Arquivo de Log (session_debug.log):**
```python
# Cada sessão terá entradas separadas:
[2025-11-19 10:00:00] SESSION: conversation-abc123 | USER: João
[2025-11-19 10:00:05] SESSION: conversation-xyz789 | USER: Maria
[2025-11-19 10:00:10] SESSION: conversation-abc123 | QUERY: apontamentos
[2025-11-19 10:00:15] SESSION: conversation-xyz789 | QUERY: apontamentos
```

---

## 📊 IDENTIFICADORES DE SESSÃO

Cada instância do emulator gera automaticamente:

```python
{
    "conversation": {
        "id": "unique-conversation-id"  # Diferente para cada emulator
    },
    "from": {
        "id": "user-id",
        "name": "User"
    },
    "channelId": "emulator"
}
```

**O bot usa `conversation.id` como chave para isolar sessões!**

---

## ✅ CHECKLIST DE TESTE

- [ ] Abrir 2-3 instâncias do Bot Framework Emulator
- [ ] Conectar todas ao mesmo endpoint (localhost:3978)
- [ ] Registrar usuários diferentes em cada emulator
- [ ] Fazer perguntas específicas em cada sessão
- [ ] Verificar que as respostas são isoladas
- [ ] Conferir logs no terminal para conversation_id diferentes
- [ ] Testar consultas simultâneas
- [ ] Verificar que dados não vazam entre sessões

---

## 🎯 EXEMPLO DE TESTE COMPLETO

### **Setup:**
```bash
# Terminal 1 - Rodar o bot
python -m uvicorn bot.bot_api:app --reload --port 3978
```

### **Emulator 1 - Usuário João:**
```
1. Abrir Bot Framework Emulator
2. Conectar: http://localhost:3978/api/messages
3. Digitar: "Olá, meu nome é João"
4. Digitar: "Meu CPF é 123.456.789-00"
5. Digitar: "Mostre meus apontamentos em outubro"
6. Digitar: "Qual é meu nome?" → Deve responder "João"
```

### **Emulator 2 - Usuário Maria:**
```
1. Abrir NOVA instância do Bot Framework Emulator
2. Conectar: http://localhost:3978/api/messages
3. Digitar: "Olá, sou Maria"
4. Digitar: "CPF: 987.654.321-00"
5. Digitar: "Quero ver meus apontamentos"
6. Digitar: "Qual é meu nome?" → Deve responder "Maria"
```

### **Voltar ao Emulator 1:**
```
7. Digitar: "Qual é meu nome?" → Ainda deve responder "João" ✅
8. Digitar: "Quantas horas trabalhei?" → Dados de João, não Maria ✅
```

---

## 🐛 PROBLEMAS COMUNS

### **Problema: Sessões se misturam**
**Solução:** Verifique se `session_manager.py` está usando `conversation_id` corretamente

### **Problema: Bot responde lento com múltiplas sessões**
**Solução:** Normal em ambiente de desenvolvimento. Em produção, usar cache e otimizações

### **Problema: Emulator não abre segunda instância**
**Solução:** Executar o .exe diretamente do diretório de instalação

---

## 📁 ARQUIVOS RELACIONADOS

- `bot/session_manager.py` - Gerencia isolamento de sessões
- `bot/ai_conversation.py` - Processa contexto por sessão
- `bot/bot_api.py` - Recebe mensagens e identifica conversation_id

---

## 🎉 RESULTADO ESPERADO

✅ **Cada emulator mantém sua própria sessão independente**  
✅ **Dados não vazam entre conversas**  
✅ **Bot processa múltiplas requisições simultâneas**  
✅ **Conversation IDs diferentes para cada instância**  
✅ **Contexto isolado por usuário**

---

## 📝 NOTAS IMPORTANTES

1. **Cada aba/janela do emulator = Nova conversa**
2. **Conversation ID é gerado automaticamente pelo emulator**
3. **O bot guarda sessões em memória (SessionManager)**
4. **Teste com 2-5 emulators é suficiente para validar multisessão**
5. **Em produção (Teams), cada usuário tem seu próprio conversation ID**

---

🚀 **PRONTO PARA TESTAR! Abra múltiplos emulators e valide o isolamento de sessões!**
