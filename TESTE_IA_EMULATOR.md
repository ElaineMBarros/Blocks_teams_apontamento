# 🧪 TESTE DE IA NO BOT FRAMEWORK EMULATOR

## ✅ Checklist - O que você precisa

### 1. **Biblioteca OpenAI**
```bash
pip install openai>=1.10.0
```

### 2. **Chave de API configurada**

Opção A - OpenAI (mais fácil para teste):
```bash
# No .env
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
```

Opção B - Azure OpenAI:
```bash
# No .env
AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com/
AZURE_OPENAI_KEY=sua-chave
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### 3. **Dados de apontamentos**

```bash
# Verificar se existe arquivo de dados
dir resultados\dados_com_duracao_*.csv
```

Se não existir, você precisa gerar os dados primeiro (execute o script de análise).

---

## 🚀 PASSO A PASSO - Teste Completo

### Passo 1: Instalar dependências

```bash
pip install openai>=1.10.0
```

### Passo 2: Configurar chave de API

**Para OpenAI (recomendado para teste)**:

1. Acesse https://platform.openai.com/api-keys
2. Crie uma API key
3. Adicione no arquivo `.env`:

```env
OPENAI_API_KEY=sk-proj-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
```

**IMPORTANTE**: Não precisa configurar Azure OpenAI para teste. Use OpenAI direto que é mais simples!

### Passo 3: Verificar configuração

Execute o teste:

```bash
python teste_ia_conversacional.py
```

Você deve ver:
- ✅ `IA configurada e pronta!`
- ✅ `Modelo: gpt-4o-mini`

Se aparecer "⚠️ IA não configurada", verifique o .env

### Passo 4: Iniciar o bot

```bash
python bot/bot_api.py
```

Verifique nos logs:
```
✅ Agente inicializado com XXX registros
✅ Módulo de conversação IA inicializado
🚀 Iniciando bot na porta 8000...
```

### Passo 5: Abrir Bot Framework Emulator

1. Abra o **Bot Framework Emulator**
2. Clique em **"Open Bot"**
3. Configure:
   - **Bot URL**: `http://localhost:8000/api/messages`
   - **Microsoft App ID**: deixe vazio
   - **Microsoft App Password**: deixe vazio
4. Clique em **"Connect"**

### Passo 6: Testar conversação com IA

Digite no emulator:

```
oi
```

O bot deve responder com um card de boas-vindas.

Agora teste perguntas em linguagem natural:

**Perguntas simples**:
```
qual é a média de horas?
quantas horas no total?
```

**Perguntas contextuais** (a IA vai lembrar da conversa anterior):
```
e hoje?
e de ontem?
quem trabalhou mais?
```

**Perguntas variadas** (IA entende variações):
```
tem algo estranho nos dados?
mostre o ranking
quanto tempo em média?
```

---

## 🔍 Verificando se a IA está funcionando

### No terminal do bot, você deve ver:

```
INFO - 📨 Mensagem de User: qual é a média de horas?
INFO - ✅ Processado com IA conversacional
```

Se aparecer "✅ Processado com IA conversacional", a IA está ativa! 🎉

### Sem IA (modo fallback):

Se não configurou a API key ou deu erro, vai aparecer:
```
INFO - ⚠️ Erro na IA, usando fallback
```

O bot ainda funciona, mas sem interpretação inteligente.

---

## 🎯 Diferença - Com IA vs Sem IA

### **SEM IA** (modo fallback):
Você precisa usar comandos específicos:
- "média de horas" ✅
- "qual é a média?" ❌

### **COM IA**:
Entende variações naturais:
- "média de horas" ✅
- "qual é a média?" ✅
- "quanto tempo em média?" ✅
- "me mostra a média" ✅

E mantém contexto:
```
Você: "qual a média?"
Bot: "A média é 8,5 horas"

Você: "e o ranking?"
Bot: "Aqui está o top 10..."

Você: "quem é o primeiro?"
Bot: "João Silva com 45 horas"
```

---

## ❌ Troubleshooting

### Erro: "openai não instalado"

**Solução**:
```bash
pip install openai>=1.10.0
```

### Erro: "API key inválida"

**Verificar**:
1. A chave está correta no `.env`?
2. Para OpenAI, a chave começa com `sk-`
3. Você tem créditos na conta OpenAI?

**Testar chave**:
```bash
curl https://api.openai.com/v1/models ^
  -H "Authorization: Bearer SEU_API_KEY"
```

### Erro: "Dados não disponíveis"

**Solução**:
```bash
# Verifique se existe arquivo de dados
dir resultados\dados_com_duracao_*.csv

# Se não existir, precisa gerar os dados primeiro
```

### Bot funciona mas não usa IA

**Verificar logs**:
- ⚠️ "OpenAI não disponível - modo fallback"

**Possíveis causas**:
1. `.env` não foi carregado (reinicie o bot)
2. Variáveis mal configuradas
3. Erro ao conectar com OpenAI

**Solução**:
```bash
# Verificar se .env existe
type .env

# Deve ter a linha:
# OPENAI_API_KEY=sk-...

# Reiniciar bot
python bot/bot_api.py
```

---

## 💡 DICA: Teste Rápido sem Emulator

### Teste 1: Biblioteca instalada?

```bash
python -c "import openai; print('✅ OpenAI instalado')"
```

### Teste 2: IA configurada?

```bash
python teste_ia_conversacional.py
```

### Teste 3: Modo interativo

```bash
python teste_ia_conversacional.py interativo
```

Digite perguntas e veja as respostas diretamente no terminal!

---

## 📊 Exemplo de Conversa Completa

```
Você: oi
Bot: [Card de boas-vindas]

Você: qual é a média de horas?
Bot: 📊 A duração média de trabalho é de 8h30min (8.5 horas)
     [Processado com IA conversacional]

Você: e eu, quanto trabalhei?
Bot: 👤 João Silva
     📊 Duração média: 9h15min
     📋 Total de apontamentos: 42

Você: tem algo estranho?
Bot: ⚠️ Identifiquei 2 apontamentos fora do padrão:
     - José: 15h (muito acima da média)
     - Ana: 1h (muito abaixo)

Você: mostre o ranking
Bot: 🏆 Top 10 - Horas Trabalhadas
     1. João Silva: 45.2h
     2. Maria Santos: 42.8h
     ...
```

---

## 🎓 Próximos Passos

1. ✅ Configure OPENAI_API_KEY no .env
2. ✅ Instale `pip install openai`
3. ✅ Execute `python teste_ia_conversacional.py`
4. ✅ Inicie o bot `python bot/bot_api.py`
5. ✅ Teste no Bot Framework Emulator
6. ✅ Veja os logs em tempo real

**Tudo funcionando?** 🎉
- Faça deploy no Azure
- Configure Azure OpenAI para produção
- Publique no Teams

---

## 📞 Precisa de ajuda?

Verifique:
- `IA_CONVERSACIONAL.md` - Documentação completa
- Logs do bot em tempo real
- Execute o teste automatizado

**Status da IA**:
```bash
curl http://localhost:8000/health
```

Resposta deve incluir:
```json
{
  "ia_conversacional_available": true
}
