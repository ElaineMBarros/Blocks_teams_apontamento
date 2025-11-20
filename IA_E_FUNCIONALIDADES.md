# 🤖 IA CONVERSACIONAL E FUNCIONALIDADES DO BOT

## 📚 Como Funciona a IA

### 🔄 Fluxo de Processamento

O bot usa um **sistema híbrido em 2 camadas**:

```
Pergunta do Usuário
       ↓
[1ª Camada] Agente Estruturado (agente_apontamentos.py)
       ↓ (se não encontrar)
[2ª Camada] IA Conversacional (Azure OpenAI GPT-4)
       ↓
Resposta Humanizada
```

### 1️⃣ Primeira Camada: Agente Estruturado

**Arquivo:** `agente_apontamentos.py`
**Função:** `responder_pergunta()`

Reconhece **padrões específicos** e chama funções diretas:
- ✅ "contrato 8446" → `consultar_por_contrato(8446)`
- ✅ "tecnologia JAVA" → `consultar_por_tecnologia('JAVA')`
- ✅ "com abatimento" → `consultar_abatimento('com')`

**Vantagem:** Resposta rápida e precisa para consultas estruturadas

### 2️⃣ Segunda Camada: IA Conversacional (GPT-4)

**Arquivo:** `bot/ai_conversation.py`
**Quando ativa:** Se a 1ª camada não encontrar resposta

**Capacidades:**
- 🧠 **Interpreta intenções** variadas:
  - "Mostre os profissionais de Java" 
  - "Quem trabalha com Java?"
  - "Lista de desenvolvedores Java"
  - → Todas levam à mesma consulta!

- 💬 **Humaniza respostas**:
  - Transforma dados técnicos em linguagem natural
  - Adapta o tom de acordo com o contexto
  - Explica resultados de forma clara

- 🔍 **Contexto inteligente**:
  - Lembra de perguntas anteriores
  - Relaciona informações
  - Faz inferências

## 📋 13 FUNCIONALIDADES DISPONÍVEIS

### 1. 📊 Status de Validação
**Comandos:**
- "Apontamentos pendentes"
- "Quantos foram validados?"
- "Status de validação"

**Resposta:**
```
✅ APONTAMENTOS VALIDADOS
✅ Validados: 203,014 (95.8%)
⏳ Pendentes: 8,849 (4.2%)
📊 Total: 211,863
```

---

### 2. 📋 Consulta por Contrato
**Comandos:**
- "Contrato 8446"
- "Mostre o contrato 7874"
- "Dados do contrato 8446.0"

**Resposta:**
```
📋 CONTRATO 8446
💻 Tecnologia: JAVA
📊 Total: 32,549
👥 Recursos: 512

📋 Top 3 Perfis:
1. ANALISTA DESENVOLVEDOR: 14,430
2. ANALISTA DE REQUISITOS: 6,017
3. ANALISTA DE ETL/BI: 3,463

👥 Top 10 Recursos: ...
```

---

### 3. 📑 Consulta por Item de Contrato
**Comandos:**
- "Item de contrato 001"
- "Item 010"

---

### 4. 💻 Consulta por Tecnologia
**Comandos:**
- "Quem trabalha com JAVA?"
- "Tecnologia AZURE"
- "Desenvolvedores DOT NET"

**Lista Top 10 Profissionais!**

---

### 5. 👔 Consulta por Perfil
**Comandos:**
- "Analistas Desenvolvedores"
- "Perfil Gerente"

---

### 6. 📈 Consulta por Nível
**Comandos:**
- "Profissionais Sênior"
- "Nível Pleno"

---

### 7. 🔍 Consultas Combinadas
**Filtros múltiplos:**
- Contrato + Tecnologia
- Perfil + Nível
- Validação + Tecnologia

---

### 8. 👤 Análise de Validadores
**Comandos:**
- "Análise de validadores"
- "Top validadores"
- "Quem valida mais?"

---

### 9. 📊 Dashboard Executivo
**Comandos:**
- "Dashboard"
- "Resumo geral"
- "Visão geral"

---

### 10. 💰 Análise de Abatimentos (NOVA!)
**Comandos:**
- "Apontamentos com abatimento"
- "Quantos têm abatimento?"
- "Análise de abatimentos"

**Resposta:**
```
💰 APONTAMENTOS COM ABATIMENTO
💰 Com abatimento: 15,234 (7.2%)
📊 Sem abatimento: 196,629 (92.8%)
📈 Total: 211,863

📋 Top 5 Contratos com Abatimento:
1. Contrato 8446: 8,500
2. Contrato 7874: 4,200
...
```

---

### 11. 👤 Consulta de Recursos
**Comandos:**
- "Recurso RECURSO_2296069147"
- "O que o recurso XXXX fez?"

**Mostra:**
- Perfil, Nível, Tecnologias
- Contratos, Divisões, Jornadas
- Clientes Atendidos

---

### 12. 📋 Listar Opções
**Comandos:**
- "Listar contratos"
- "Quais tecnologias?"

---

### 13. 🔎 Busca do Jaime
**Implementado e funcional!**

---

## 🎯 Exemplos de IA em Ação

### Pergunta Variada 1:
**User:** "Mostra pra mim os caras que mexem com Java"
**Bot (IA):** Entendi! Vou buscar os profissionais que trabalham com Java...
→ Chama `consultar_por_tecnologia('JAVA')`
→ Retorna lista de profissionais

### Pergunta Variada 2:
**User:** "Tem muito apontamento sem validar?"
**Bot (IA):** Vou verificar os apontamentos pendentes de validação...
→ Chama `consultar_por_validacao('pendente')`
→ Retorna estatísticas

### Pergunta Variada 3:
**User:** "Quais apontamentos têm desconto?"
**Bot (IA):** Você quer saber sobre abatimentos? Vou consultar...
→ Chama `consultar_abatimento('com')`
→ Retorna análise de abatimentos

---

## 🔧 Configuração da IA

**Arquivo:** `.env`
```env
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_KEY=sua_chave
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Modelo:** GPT-4 (Azure OpenAI)
**Modo:** Conversacional com contexto
**Integração:** Automática via `bot_api.py`

---

## 📊 Estatísticas Atuais

- ✅ **211.863 registros** processados
- ✅ **2.949 recursos** anonimizados
- ✅ **13 funcionalidades** operacionais
- ✅ **IA GPT-4** integrada
- ✅ **100% funcional** em produção

---

## 🚀 Como Testar

### No Bot Framework Emulator:
```
http://127.0.0.1:3978/api/messages
```

### Exemplos de Perguntas:
1. "Olá" - Card de boas-vindas
2. "Dashboard" - Visão geral
3. "Contrato 8446" - Detalhes do contrato
4. "Quem trabalha com JAVA?" - Lista profissionais
5. "Apontamentos com abatimento" - Análise de abatimentos
6. "Recurso RECURSO_2296069147" - Detalhes do recurso
7. "Quantos foram validados?" - Status de validação

---

## 💡 Dicas de Uso

### ✅ Perguntas Aceitas:
- Diretas: "Contrato 8446"
- Naturais: "Mostre o contrato 8446"
- Variadas: "Quero ver dados do contrato 8446"

### 🤖 A IA Entende:
- Sinônimos: "profissionais", "recursos", "pessoas"
- Variações: "apontamento", "registro", "entrada"
- Contexto: "e o contrato anterior?" (lembra do contexto)

### ⚡ Resposta Rápida:
- Use comandos diretos para respostas instantâneas
- Ex: "dashboard", "contrato 8446", "tecnologia JAVA"

---

**Sistema Desenvolvido por: Bot de Apontamentos v2.0**
**Data: Novembro 2025**
**Status: ✅ 100% Operacional**
