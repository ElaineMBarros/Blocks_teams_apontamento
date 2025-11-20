# 📋 PLANEJAMENTO: AGENTE MULTISESSÃO + PUBLICAÇÃO WEB

## 🎯 Objetivos

1. **Agente Multisessão**: Suportar múltiplos usuários simultâneos
2. **Publicação Bot Framework**: Criar recurso no Azure
3. **Canal Web**: Disponibilizar via Web Chat (sem frontend customizado)
4. **Sem Autenticação**: Por enquanto (só quando migrar para Teams)

---

## 📊 FASE 1: IMPLEMENTAR MULTISESSÃO

### 🔧 Atividades

#### 1.1 Gerenciamento de Estado (1-2 horas)
**Arquivo:** `bot/conversation_state_manager.py` (NOVO)

**O que fazer:**
- Implementar `ConversationState` e `UserState` do Bot Framework
- Criar storage em memória ou Azure Blob Storage
- Gerenciar contexto de cada conversa separadamente

**Código necessário:**
```python
from botbuilder.core import ConversationState, UserState, MemoryStorage

# Cada usuário terá seu próprio estado
storage = MemoryStorage()
conversation_state = ConversationState(storage)
user_state = UserState(storage)
```

**Esforço:** 1-2 horas
**Complexidade:** Média

---

#### 1.2 Sessões Isoladas por Usuário (1-2 horas)
**Arquivo:** `bot/bot_api.py` (MODIFICAR)

**O que fazer:**
- Modificar endpoint `/api/messages` para identificar cada conversa
- Usar `turn_context.activity.conversation.id` como chave única
- Criar histórico de conversa por sessão
- Isolar dados da IA por usuário

**Mudanças necessárias:**
```python
@app.post("/api/messages")
async def messages(request: Request):
    conversation_id = activity.conversation.id  # ID único por sessão
    
    # Buscar histórico desta conversa
    historico = obter_historico(conversation_id)
    
    # Processar com contexto isolado
    resposta = processar_com_contexto(mensagem, historico)
    
    # Salvar histórico
    salvar_historico(conversation_id, mensagem, resposta)
```

**Esforço:** 1-2 horas
**Complexidade:** Média

---

#### 1.3 Cache e Performance (30min - 1 hora)
**Arquivo:** `agente_apontamentos.py` (MODIFICAR)

**O que fazer:**
- Implementar cache de consultas frequentes
- Evitar recarregar CSV a cada requisição
- Singleton do agente (já está parcialmente implementado)

**Esforço:** 30min - 1 hora
**Complexidade:** Baixa

---

#### 1.4 Testes de Multisessão (1 hora)
**Arquivo:** `teste_multisessao.py` (NOVO)

**O que fazer:**
- Simular múltiplos usuários simultâneos
- Verificar isolamento de contexto
- Testar carga (10-50 usuários simultâneos)

**Esforço:** 1 hora
**Complexidade:** Média

---

### ⏱️ TOTAL FASE 1: 3,5 - 6 horas

---

## 📊 FASE 2: PUBLICAR NO AZURE BOT SERVICE

### 🔧 Atividades

#### 2.1 Criar Bot Resource no Azure (30min)
**Portal:** Azure Portal

**O que fazer:**
1. Criar recurso "Azure Bot"
2. Configurar:
   - **Nome:** bot-apontamentos-web
   - **Resource Group:** (existente ou novo)
   - **Pricing Tier:** F0 (gratuito) para testes, depois S1
   - **Bot Handle:** nome único global
   - **App Type:** Multi-Tenant

3. Obter credenciais:
   - **Microsoft App ID**
   - **Microsoft App Password**

**Esforço:** 30 minutos
**Complexidade:** Baixa
**Custo:** Gratuito (F0) ou ~R$ 25/mês (S1 para produção)

---

#### 2.2 Configurar App Registration (30min)
**Portal:** Azure Active Directory

**O que fazer:**
1. Já criado automaticamente com o Bot
2. Anotar:
   - **Application (client) ID**
   - **Client Secret** (criar se necessário)
3. Sem configurar permissões de usuário (ainda)

**Esforço:** 30 minutos
**Complexidade:** Baixa

---

#### 2.3 Atualizar Código com Credenciais (30min)
**Arquivo:** `.env` e `bot/config.py`

**O que fazer:**
- Adicionar credenciais do Azure Bot ao `.env`:
```env
MICROSOFT_APP_ID=seu-app-id
MICROSOFT_APP_PASSWORD=seu-app-password
MICROSOFT_APP_TYPE=MultiTenant
```

- Atualizar `bot_api.py` para usar credenciais
- Remover modo dev (usar BotFrameworkAdapter com credenciais)

**Esforço:** 30 minutos
**Complexidade:** Baixa

---

#### 2.4 Deploy da Aplicação (1-2 horas)
**Opções:**

##### Opção A: Azure App Service (Recomendado)
**O que fazer:**
1. Criar Azure App Service (Linux, Python 3.11)
2. Configurar deployment:
   - Via GitHub Actions (automático)
   - Ou via Azure CLI / VS Code
3. Configurar variáveis de ambiente
4. Instalar dependências (`requirements.txt`)

**Esforço:** 1-2 horas
**Complexidade:** Média
**Custo:** ~R$ 50-150/mês (Basic tier)

##### Opção B: Azure Container Instances
**Esforço:** 1,5-2 horas
**Complexidade:** Média-Alta
**Custo:** ~R$ 30-80/mês

##### Opção C: Servidor Próprio (ngrok temporário)
**O que fazer:**
- Usar ngrok para expor localhost
- Configurar endpoint público no Azure Bot

**Esforço:** 15-30 minutos
**Complexidade:** Baixa
**Custo:** Gratuito (temporário) ou ~$10/mês (ngrok pago)

---

#### 2.5 Configurar Messaging Endpoint (15min)
**Portal:** Azure Bot Resource

**O que fazer:**
- Apontar para URL pública:
  - `https://seu-app.azurewebsites.net/api/messages` (App Service)
  - `https://seu-dominio.ngrok.io/api/messages` (ngrok)
- Testar conexão no portal

**Esforço:** 15 minutos
**Complexidade:** Baixa

---

#### 2.6 Testar com Bot Framework Emulator (30min)
**Ferramenta:** Bot Framework Emulator

**O que fazer:**
- Conectar com credenciais reais
- Testar autenticação
- Verificar logs do Azure

**Esforço:** 30 minutos
**Complexidade:** Baixa

---

### ⏱️ TOTAL FASE 2: 3,5 - 5 horas

---

## 📊 FASE 3: ATIVAR CANAL WEB CHAT

### 🔧 Atividades

#### 3.1 Ativar Canal Web Chat (5min)
**Portal:** Azure Bot → Channels

**O que fazer:**
1. Clicar em "Web Chat"
2. Copiar **Secret Keys**
3. Canais já vêm habilitados por padrão

**Esforço:** 5 minutos
**Complexidade:** Baixa (automático)

---

#### 3.2 Obter Código de Integração (10min)
**Portal:** Azure Bot → Web Chat Channel

**O que fazer:**
- Copiar iframe ou script de integração:

**Opção 1 - Iframe (mais simples):**
```html
<iframe 
  src='https://webchat.botframework.com/embed/bot-apontamentos-web?s=SEU_SECRET'
  style='min-width: 400px; width: 100%; min-height: 500px;'>
</iframe>
```

**Opção 2 - Widget customizável:**
```html
<div id="webchat" role="main"></div>
<script src="https://cdn.botframework.com/botframework-webchat/latest/webchat.js"></script>
<script>
  window.WebChat.renderWebChat({
    directLine: window.WebChat.createDirectLine({
      secret: 'SEU_SECRET'
    }),
    userID: 'USER_' + Math.random()
  }, document.getElementById('webchat'));
</script>
```

**Esforço:** 10 minutos
**Complexidade:** Baixa

---

#### 3.3 Criar Página HTML Simples (30min - 1 hora)
**Arquivo:** `public/index.html` (NOVO)

**O que fazer:**
- Criar página HTML básica
- Incorporar Web Chat
- Adicionar estilo (opcional)
- Hospedar em Azure Static Web Apps (gratuito) ou GitHub Pages

**Exemplo básico:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Bot de Apontamentos</title>
  <style>
    body { margin: 0; font-family: Arial; }
    #webchat { height: 100vh; width: 100%; }
  </style>
</head>
<body>
  <div id="webchat"></div>
  <script src="https://cdn.botframework.com/botframework-webchat/latest/webchat.js"></script>
  <script>
    window.WebChat.renderWebChat({
      directLine: window.WebChat.createDirectLine({
        secret: 'SEU_SECRET_AQUI'
      }),
      userID: 'User_' + Math.random().toString(36).substring(7)
    }, document.getElementById('webchat'));
  </script>
</body>
</html>
```

**Esforço:** 30min - 1 hora
**Complexidade:** Baixa

---

#### 3.4 Hospedar Página (30min - 1 hora)

##### Opção A: Azure Static Web Apps (Recomendado)
**O que fazer:**
- Criar Static Web App (gratuito)
- Deploy via GitHub
- URL: `https://seu-bot.azurestaticapps.net`

**Esforço:** 30 minutos
**Complexidade:** Baixa
**Custo:** Gratuito

##### Opção B: GitHub Pages
**Esforço:** 15 minutos
**Complexidade:** Baixa
**Custo:** Gratuito

##### Opção C: No próprio App Service
**Esforço:** 15 minutos (adicionar rota estática)
**Complexidade:** Baixa

---

#### 3.5 Configurar Domínio Customizado (Opcional) (1 hora)
**O que fazer:**
- Comprar domínio (ex: bot-apontamentos.com.br)
- Configurar DNS
- Adicionar certificado SSL (gratuito via Azure)

**Esforço:** 1 hora
**Complexidade:** Média
**Custo:** ~R$ 40/ano (domínio)

---

#### 3.6 Testes Finais (1 hora)
**O que fazer:**
- Testar todas as funcionalidades via Web Chat
- Testar múltiplas sessões (abas diferentes)
- Verificar isolamento de contexto
- Testar em mobile

**Esforço:** 1 hora
**Complexidade:** Baixa

---

### ⏱️ TOTAL FASE 3: 2,5 - 4,5 horas

---

## 📊 RESUMO GERAL

### ⏱️ Estimativa de Tempo

| Fase | Atividade | Tempo Mínimo | Tempo Máximo |
|------|-----------|--------------|--------------|
| **FASE 1** | Multisessão | 3,5h | 6h |
| **FASE 2** | Publicação Azure | 3,5h | 5h |
| **FASE 3** | Canal Web Chat | 2,5h | 4,5h |
| **TOTAL** | | **9,5 horas** | **15,5 horas** |

### ⏱️ Estimativa Realista: 12-14 horas (1,5 a 2 dias úteis)

---

## 💰 Custos Mensais Estimados

### Opção Econômica (Teste/Demo):
- Azure Bot Service: **F0** = Gratuito
- Azure App Service: **B1** = ~R$ 50/mês
- Azure OpenAI: ~R$ 50-100/mês (já em uso)
- Static Web App: Gratuito
- **TOTAL:** ~R$ 100-150/mês

### Opção Produção (Recomendado):
- Azure Bot Service: **S1** = ~R$ 25/mês (10k msgs)
- Azure App Service: **S1** = ~R$ 150/mês
- Azure OpenAI: ~R$ 100-200/mês
- Azure Blob Storage: ~R$ 10/mês (logs/cache)
- **TOTAL:** ~R$ 285-385/mês

---

## 🎯 Ordem de Execução Recomendada

### Dia 1 (6-8 horas):
1. ✅ Implementar multisessão (3-4h)
2. ✅ Criar recurso Azure Bot (30min)
3. ✅ Configurar credenciais (30min)
4. ✅ Deploy inicial (1-2h)
5. ✅ Testar endpoint (30min-1h)

### Dia 2 (4-6 horas):
1. ✅ Ativar Web Chat (15min)
2. ✅ Criar página HTML (1h)
3. ✅ Hospedar página (30min-1h)
4. ✅ Testes completos (2-3h)
5. ✅ Ajustes finais (1h)

---

## 🚨 Pontos de Atenção

### Multisessão:
- ⚠️ **Memory leak**: Limpar sessões antigas (timeout 30min)
- ⚠️ **Performance**: Cache de consultas frequentes
- ⚠️ **Escalabilidade**: Considerar Redis se >100 usuários simultâneos

### Azure:
- ⚠️ **Credenciais**: Guardar secrets no Azure Key Vault (produção)
- ⚠️ **Custos**: Monitorar uso (alertas de budget)
- ⚠️ **Region**: Usar mesma região do OpenAI (Brazil South)

### Web Chat:
- ⚠️ **Secret Key**: Não expor diretamente (usar token service em prod)
- ⚠️ **CORS**: Configurar no App Service
- ⚠️ **Rate Limit**: Proteger contra abuso

---

## 📚 Arquivos que serão Criados/Modificados

### Novos:
- `bot/conversation_state_manager.py`
- `bot/session_manager.py`
- `teste_multisessao.py`
- `public/index.html`
- `.github/workflows/azure-deploy.yml` (CI/CD opcional)

### Modificados:
- `bot/bot_api.py` (multisessão + credenciais)
- `bot/config.py` (novas configs)
- `.env` (credenciais Azure)
- `requirements.txt` (novas dependências)

---

## ✅ Próximos Passos (APÓS APROVAÇÃO)

1. Confirmar opções:
   - Hosting: App Service, Container ou ngrok?
   - Storage: Memória, Blob ou Redis?
   - Domínio customizado: Sim ou usar Azure URL?

2. Verificar recursos Azure:
   - Subscription ativa?
   - Permissões de admin?
   - Budget disponível?

3. Iniciar Fase 1: Multisessão

---

**📅 Início planejado:** Após aprovação
**🎯 Conclusão estimada:** 1,5 a 2 dias úteis
**💰 Investimento:** R$ 100-400/mês (dependendo do plano)
