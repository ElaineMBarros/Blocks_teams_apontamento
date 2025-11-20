# 🤖 Como Testar o Bot no Bot Framework Emulator

## ✅ Bot Está Rodando!

**Status:** ✅ Ativo
**Servidor:** `http://0.0.0.0:8000`
**Dados carregados:** 200 registros
**IA:** ✅ OpenAI configurada

---

## 📍 Endereço para Bot Framework Emulator

### Configuração no Emulator:

**Endpoint URL:**
```
http://localhost:8000/api/messages
```

**Ou use (caso localhost não funcione):**
```
http://127.0.0.1:8000/api/messages
```

**Microsoft App ID:** *(deixe vazio)*

**Microsoft App Password:** *(deixe vazio)*

---

## 🧪 Perguntas para Testar as 3 Novas Funcionalidades

### 1️⃣ Contar Dias Úteis
```
Quantos dias úteis tem no período de 01/09 a 30/09?
```
**Resposta Esperada:** 22 dias úteis

---

### 2️⃣ Calcular Horas Esperadas
```
Quantas horas o colaborador deveria fazer no período de 01/09 a 30/09?
```
**Resposta Esperada:** 154 horas líquidas (176h brutas - 22h almoço)

---

### 3️⃣ Identificar Dias Não Apontados

**Consulta Geral (todos os colaboradores):**
```
Quem não apontou horas no período de 01/09 a 30/09?
```

**Consulta Individual:**
```
Quais dias Rosiane não apontou em setembro?
```

**Consulta Detalhada:**
```
Quem não apontou horas no período de 01/09 a 30/09, considerando os dias úteis? (mostrar quais dias não foram apontados)
```

---

## 📊 Outras Perguntas para Testar

### Consultas Básicas:
- "Qual a média de horas?"
- "Mostrar ranking"
- "Quantas horas apontei esta semana?"
- "Comparar semanas"

### Consultas com Período:
- "Consultar período de 01/09 a 15/09"
- "Mostrar dados de setembro"

### Análise de Outliers:
- "Mostrar apontamentos fora do padrão"
- "Identificar outliers"

---

## 🎯 Passos para Testar

### 1. Abrir Bot Framework Emulator
- Inicie o Bot Framework Emulator

### 2. Conectar ao Bot
- Clique em "Open Bot"
- Cole o endpoint: `http://localhost:8000/api/messages`
- Deixe App ID e Password vazios
- Clique em "Connect"

### 3. Testar Conversação
- Digite qualquer pergunta no chat
- A IA vai interpretar e chamar a função apropriada
- Você verá a resposta formatada com emojis e dados

### 4. Ver Logs
- No terminal, você verá os logs de cada requisição
- Confirme que mostra "✅ Processado com IA conversacional"

---

## 🔍 O Que Observar nos Logs

```
📨 Mensagem de User: [sua pergunta]
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
✅ Processado com IA conversacional
127.0.0.1 - "POST /api/messages HTTP/1.1" 200 OK
```

---

## ⚠️ Troubleshooting

### Problema: "Connection refused"
**Solução:** Use `http://127.0.0.1:8000/api/messages` ao invés de localhost

### Problema: "Desculpe, não tenho essa informação"
**Solução:** 
- Verifique se a OpenAI está configurada (arquivo .env)
- Verifique os logs no terminal
- A IA pode não ter entendido a pergunta - reformule

### Problema: Bot não responde
**Solução:**
- Verifique se o bot está rodando (terminal ativo)
- Confirme que o endpoint está correto (`/api/messages` no final)
- Reinicie o Bot Framework Emulator

---

## 📝 Resultados Esperados

### Teste 1: Dias Úteis ✅
```
📅 Período: 2025-09-01 a 2025-09-30

📊 Dias Úteis: 22 dias
🏖️ Fins de Semana: 8 dias
📆 Total de Dias: 30 dias
```

### Teste 2: Horas Esperadas ✅
```
📅 Período: 2025-09-01 a 2025-09-30

📊 Dias Úteis: 22 dias
⏱️ Horas por Dia: 8.0h

📈 Horas Esperadas (Brutas): 176.0h
🍽️ Desconto Almoço: 22.0h
✅ Horas Esperadas (Líquidas): 154.0h
```

### Teste 3: Dias Não Apontados ✅
```
📅 Período: 2025-09-01 a 2025-09-30

👥 Análise de 17 colaboradores

⚠️ 17 colaborador(es) com dias não apontados:

• Elisangela de Santana Silva: 20 dia(s) não apontado(s)
  Dias: 01/09/2025, 04/09/2025, 05/09/2025...
• Camilly do Carmo Davalos: 20 dia(s) não apontado(s)
...
```

---

## 🚀 Versão Publicada

**Repositório GitHub:** https://github.com/ElaineMBarros/Blocks_teams_apontamento

**Commit:** `fea7aca` - feat: Adiciona 3 novas funcionalidades de análise de período

✅ Código publicado e pronto para uso!
