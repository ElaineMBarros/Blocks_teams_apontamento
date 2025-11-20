# 🧪 GUIA DE TESTE - BOT FRAMEWORK EMULATOR (VERSÃO 2)

## 🎯 Novas Funcionalidades para Testar

### ✅ 1. STATUS DE VALIDAÇÃO
**Perguntas para testar:**
- "Quantos apontamentos não foram validados?"
- "Mostre os pendentes"
- "Status de validação"
- "Apontamentos validados"

**Resultado esperado:**
- ✅ Validados: 203.014 (95.8%)
- ⏳ Pendentes: 8.849 (4.2%)
- Lista dos mais antigos pendentes

---

### 📋 2. CONSULTAS POR CONTRATO
**Perguntas para testar:**
- "Mostre o contrato 8446"
- "Contrato 7874"
- "Quais contratos temos?"

**Resultado esperado:**
- Tecnologia do contrato
- Total de apontamentos
- Recursos únicos
- Top perfis

---

### 💻 3. CONSULTAS POR TECNOLOGIA
**Perguntas para testar:**
- "Quem trabalha com JAVA?"
- "Mostre AZURE"
- "Tecnologia DOT NET"
- "Quais tecnologias disponíveis?"

**Resultado esperado:**
- Total de apontamentos
- Quantidade de recursos
- Contratos associados

---

### 👔 4. CONSULTAS POR PERFIL
**Perguntas para testar:**
- "Analistas Desenvolvedores"
- "Gerentes de Projetos"
- "Arquitetos"
- "Quais perfis temos?"

**Resultado esperado:**
- Total de apontamentos
- Quantidade de profissionais
- Top tecnologias para o perfil

---

### 📈 5. CONSULTAS POR NÍVEL
**Perguntas para testar:**
- "Profissionais Sênior"
- "Nível 3"
- "Pleno"
- "Quais níveis disponíveis?"

**Resultado esperado:**
- Total de apontamentos
- Quantidade de profissionais
- Top perfis por nível

---

### 🔍 6. CONSULTAS COMBINADAS
**Perguntas para testar:**
- "Desenvolvedores JAVA Sênior"
- "Analistas DOT NET Pleno"
- "Gerentes AZURE Nível 3"

**Resultado esperado:**
- Filtros aplicados
- Total de apontamentos
- Recursos encontrados

---

### 👤 7. ANÁLISE DE VALIDADORES
**Perguntas para testar:**
- "Quem são os validadores?"
- "Validadores mais ativos"
- "Ranking de validadores"

**Resultado esperado:**
- Total de validadores
- Top 10 validadores
- Percentual de cada um

---

### 📊 8. DASHBOARD EXECUTIVO
**Perguntas para testar:**
- "Dashboard"
- "Visão geral"
- "Resumo executivo"

**Resultado esperado:**
- Total de apontamentos
- Recursos
- Top contratos
- Top tecnologias
- Status de validação

---

## 🚀 COMO INICIAR O TESTE

### 1. Iniciar o Servidor do Bot
```bash
# No terminal
python -m uvicorn bot.bot_api:app --reload --port 3978
```

### 2. Abrir Bot Framework Emulator
- Endpoint: `http://localhost:3978/api/messages`
- App ID: (deixar vazio para dev)
- App Password: (deixar vazio para dev)

### 3. Testar Comandos Básicos Primeiro
1. Digite: **"oi"** - Deve mostrar card de boas-vindas
2. Digite: **"ajuda"** - Deve mostrar comandos disponíveis

### 4. Testar Novas Funcionalidades
Execute as perguntas listadas acima e verifique os resultados!

---

## ✅ CHECKLIST DE TESTES

### Testes Básicos
- [ ] Card de boas-vindas funciona
- [ ] Card de ajuda funciona
- [ ] Bot responde mensagens

### Testes de Validação
- [ ] Consulta de pendentes funciona
- [ ] Consulta de validados funciona
- [ ] Lista validadores funciona

### Testes de Estrutura
- [ ] Consulta por contrato funciona
- [ ] Consulta por tecnologia funciona
- [ ] Consulta por perfil funciona
- [ ] Consulta por nível funciona

### Testes Avançados
- [ ] Consultas combinadas funcionam
- [ ] Dashboard executivo funciona
- [ ] Listar opções funciona

### Testes de Performance
- [ ] Respostas são rápidas (< 2s)
- [ ] Cards são formatados corretamente
- [ ] Dados estão corretos

---

## 📝 NOTA IMPORTANTE

**O bot ainda está usando `agente_apontamentos.py` (versão antiga).**

Para usar as novas funcionalidades do `agente_apontamentos_v2.py`, você tem 2 opções:

### Opção 1: Renomear arquivos (mais simples)
```bash
# Fazer backup do antigo
move agente_apontamentos.py agente_apontamentos_old.py

# Usar o V2 como principal
copy agente_apontamentos_v2.py agente_apontamentos.py
```

### Opção 2: Modificar bot_api.py
Alterar linha 21 de:
```python
from agente_apontamentos import AgenteApontamentos
```
Para:
```python
from agente_apontamentos_v2 import AgenteApontamentosV2 as AgenteApontamentos
```

---

## 🎉 RESULTADOS ESPERADOS

Se tudo funcionar:
- ✅ 10 novas funcionalidades operacionais
- ✅ 211.863 registros disponíveis
- ✅ 2.949 recursos identificados
- ✅ 26 tecnologias catalogadas
- ✅ 45 perfis profissionais
- ✅ 19 contratos fornecedor

**Boa sorte nos testes! 🚀**
