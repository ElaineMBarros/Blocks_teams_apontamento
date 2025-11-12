# 🤖 IA CONVERSACIONAL - Guia Completo

## Visão Geral

O bot agora suporta **conversação em linguagem natural** usando IA (GPT) para interpretar perguntas sobre apontamentos de forma mais inteligente e contextual.

## 🎯 Características

### ✅ Com IA Ativada
- **Linguagem natural fluida**: "quantas horas trabalhei essa semana?"
- **Contexto conversacional**: O bot lembra das mensagens anteriores
- **Respostas personalizadas**: Formatação amigável e concisa
- **Interpretação inteligente**: Entende variações de perguntas

### 🔄 Modo Fallback (Sem IA)
- Se a IA não estiver configurada, o bot usa processamento de linguagem simples
- Funciona com comandos específicos e palavras-chave

---

## 📋 Configuração

### Opção 1: Azure OpenAI (Recomendado para Empresas)

1. **Criar recurso no Azure**:
   - Acesse [Azure Portal](https://portal.azure.com)
   - Crie um recurso "Azure OpenAI"
   - Deploy um modelo (ex: gpt-4, gpt-35-turbo)

2. **Configurar variáveis de ambiente**:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=sua-chave-aqui
   AZURE_OPENAI_DEPLOYMENT=gpt-4
   ```

3. **Vantagens**:
   - ✅ Dados permanecem no Azure (compliance)
   - ✅ Integração com Azure AD
   - ✅ Controle de custos e limites

### Opção 2: OpenAI Direto

1. **Obter API Key**:
   - Acesse [platform.openai.com](https://platform.openai.com)
   - Crie uma API key

2. **Configurar variáveis de ambiente**:
   ```env
   OPENAI_API_KEY=sk-sua-chave-aqui
   OPENAI_MODEL=gpt-4o-mini
   ```

3. **Modelos disponíveis**:
   - `gpt-4o-mini`: Rápido e econômico (recomendado)
   - `gpt-4o`: Mais avançado
   - `gpt-4`: Versão anterior

---

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install openai>=1.10.0
```

Ou atualizar todas as dependências:

```bash
pip install -r requirements.txt
```

### 2. Configurar .env

Copie o arquivo de exemplo e configure suas chaves:

```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### 3. Iniciar o bot

```bash
python bot/bot_api.py
```

Verifique os logs:
- ✅ `Módulo de conversação IA inicializado` - IA ativa
- ⚠️ `OpenAI não disponível - modo fallback` - Sem IA

---

## 💬 Exemplos de Uso

### Perguntas em Linguagem Natural

```
Usuário: "quanto tempo eu trabalhei hoje?"
Bot: 📅 Hoje você trabalhou 7,5 horas em 3 apontamentos!

Usuário: "e ontem?"
Bot: 📅 Ontem foram 8 horas distribuídas em 4 apontamentos.

Usuário: "quem está trabalhando mais?"
Bot: 🏆 Top 5 colaboradores:
1. João Silva - 45,2h
2. Maria Santos - 42,8h
...

Usuário: "tem algo estranho nos dados?"
Bot: ⚠️ Identifiquei 2 apontamentos fora do padrão:
- José: 15h (muito acima da média)
- Ana: 1h (muito abaixo)
```

### Comparado com Modo Simples (Sem IA)

**Sem IA**: Precisa usar comandos específicos
```
"média de horas"
"ranking"
"outliers"
```

**Com IA**: Entende variações naturais
```
"qual a média?"
"quanto tempo em média?"
"quem trabalhou mais?"
"tem algo fora do normal?"
```

---

## 🔧 Como Funciona

### Arquitetura

```
Usuário → Teams → Bot API → Conversação IA → Agente Apontamentos → Dados
                                    ↓
                              GPT (Azure/OpenAI)
```

### Fluxo de Processamento

1. **Recebe mensagem** do usuário no Teams
2. **Histórico de contexto**: Últimas 5 mensagens mantidas
3. **GPT interpreta** a pergunta e identifica qual função usar
4. **Executa função** no agente de apontamentos
5. **GPT formata** a resposta de forma amigável
6. **Envia card** formatado ao Teams

### Funções Disponíveis para IA

A IA pode chamar automaticamente:
- `duracao_media_geral()` - Média de horas
- `duracao_media_usuario(nome)` - Média por usuário
- `apontamentos_hoje(usuario)` - Apontamentos de hoje
- `ranking_funcionarios()` - Top funcionários
- `total_horas_usuario(nome)` - Total de horas
- `identificar_outliers()` - Anomalias
- `resumo_semanal(usuario)` - Resumo da semana
- `comparar_periodos()` - Comparação entre períodos

---

## ⚙️ Configurações Avançadas

### Ajustar Temperatura

Edite `bot/ai_conversation.py`:

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=mensagens,
    temperature=0.7,  # 0.0 = preciso, 1.0 = criativo
    max_tokens=500
)
```

### Controlar Histórico

Por padrão, mantém últimas 5 mensagens:

```python
# Em ai_conversation.py
mensagens.extend(historico[-5:])  # Alterar número aqui
```

### Limpar Histórico de Usuário

```python
from bot.ai_conversation import conversacao_ia

# Limpar histórico de um usuário específico
conversacao_ia.limpar_historico("João Silva")
```

---

## 📊 Monitoramento

### Verificar Status

**Endpoint de health**:
```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "healthy",
  "bot_configured": true,
  "agente_available": true,
  "ia_conversacional_available": true,
  "environment": "development"
}
```

### Logs

O bot registra cada interação:
```
INFO - ✅ Processado com IA conversacional
INFO - 📨 Mensagem de João Silva: quanto trabalhei hoje?
```

---

## 💰 Custos

### Azure OpenAI
- Preços por 1000 tokens
- GPT-4: ~$0.03/1k tokens
- GPT-3.5-turbo: ~$0.002/1k tokens

### OpenAI Direto
- GPT-4o-mini: $0.15/$0.60 (input/output por 1M tokens)
- GPT-4o: $2.50/$10.00 (input/output por 1M tokens)

**Estimativa**: 
- Mensagem típica: ~200-500 tokens
- 1000 mensagens/mês: ~$2-10 (GPT-4o-mini)

---

## 🔒 Segurança

### Boas Práticas

1. **Não compartilhe API keys** em código ou repositórios
2. **Use variáveis de ambiente** para credenciais
3. **Azure OpenAI** para dados sensíveis (mantém dados no Azure)
4. **Monitore uso** para evitar custos inesperados
5. **Limite rate**: Configure limites no Azure/OpenAI

### Dados Processados

- ✅ Apenas estatísticas e resumos são enviados para IA
- ✅ Nenhum dado sensível individual é compartilhado
- ✅ Histórico de conversação mantido apenas em memória

---

## 🐛 Troubleshooting

### Erro: "OpenAI não disponível"

**Causa**: Biblioteca não instalada
```bash
pip install openai>=1.10.0
```

### Erro: "API key inválida"

**Verificar**:
1. Chave está correta no `.env`
2. Para Azure: endpoint e deployment corretos
3. Para OpenAI: chave começa com "sk-"

### Bot não usa IA

**Verificar logs**:
```
⚠️ Nenhuma chave de API configurada - modo fallback
```

**Solução**: Configure AZURE_OPENAI_* ou OPENAI_API_KEY

### Respostas lentas

**Opções**:
1. Use modelo mais rápido (gpt-4o-mini)
2. Reduza max_tokens
3. Verifique latência de rede

---

## 📚 Recursos Adicionais

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Bot Framework Documentation](https://docs.microsoft.com/bot-framework/)

---

## 🎓 Próximos Passos

1. Configure suas credenciais de IA
2. Teste com perguntas variadas
3. Monitore custos e uso
4. Ajuste prompts conforme necessário
5. Implemente feedback dos usuários
