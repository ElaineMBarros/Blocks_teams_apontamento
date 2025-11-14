# 📅 Funcionalidade de Dias Úteis e Desconto de Almoço

## 📋 Visão Geral

O agente de apontamentos agora inclui cálculo automático de horas líquidas considerando:
- **Dias Úteis vs Fins de Semana**: Identificação automática de sábados e domingos
- **Desconto de Almoço**: Aplicação de 1 hora de desconto apenas em dias úteis

Esta funcionalidade está alinhada com a implementação existente no projeto Streamlit.

---

## 🔧 Funcionalidades Implementadas

### 1. Verificação de Dia Útil

```python
def eh_dia_util(self, data: datetime) -> bool
```

**O que faz:**
- Verifica se uma data é dia útil (segunda a sexta-feira)
- Identifica automaticamente sábados (weekday=5) e domingos (weekday=6)

**Retorna:**
- `True`: Dia útil (segunda a sexta)
- `False`: Fim de semana (sábado ou domingo)

**Observação:** A função está preparada para incluir verificação de feriados nacionais no futuro.

---

### 2. Aplicação de Desconto de Almoço

```python
def aplicar_desconto_almoco(self, horas: float, eh_dia_util: bool = True) -> float
```

**O que faz:**
- Aplica desconto de 1 hora de almoço APENAS em dias úteis
- Fins de semana NÃO têm desconto de almoço
- Garante que o resultado não seja negativo

**Exemplo:**
```python
# Dia útil com 8h apontadas
horas_liquidas = aplicar_desconto_almoco(8.0, True)  # Retorna 7.0

# Fim de semana com 8h apontadas
horas_liquidas = aplicar_desconto_almoco(8.0, False)  # Retorna 8.0

# Dia útil com apenas 0.5h apontada
horas_liquidas = aplicar_desconto_almoco(0.5, True)  # Retorna 0.0 (não fica negativo)
```

---

### 3. Classificação de Apontamentos

```python
def classificar_apontamento(self, data: datetime, horas: float) -> Dict
```

**O que faz:**
- Classifica completamente um apontamento
- Determina se é dia útil ou fim de semana
- Calcula horas líquidas
- Retorna informações estruturadas

**Retorno:**
```python
{
    "dia_util": True/False,                    # Se é dia útil
    "tipo_dia": "📅 Dia Útil" ou "🏖️ Fim de Semana",
    "horas_brutas": 8.5,                       # Horas antes do desconto
    "horas_liquidas": 7.5,                     # Horas após desconto
    "desconto_almoco": 1.0                     # Valor do desconto aplicado
}
```

---

## 📊 Métodos Atualizados

### ✅ `apontamentos_hoje(usuario: str)`

**Informações exibidas:**
- **Tipo de dia**: Indica se hoje é dia útil ou fim de semana
- **Horas Brutas**: Total sem desconto
- **Desconto Almoço**: Valor descontado (1h em dias úteis, 0h em fins de semana)
- **Horas Líquidas**: Total após desconto

**Exemplo de resposta:**
```
📅 Hoje (2025-11-13) - 📅 Dia Útil
⏱️ Horas Brutas: 8h30min
🍽️ Desconto Almoço: 1.0h
✅ Horas Líquidas: 7h30min
📝 Número de apontamentos: 5
```

---

### ✅ `resumo_semanal(usuario: str)`

**Informações exibidas:**
- **Horas Brutas**: Total da semana sem descontos
- **Desconto Almoço**: Total descontado na semana
- **Horas Líquidas**: Total após descontos
- **Médias**: Diária bruta e líquida
- **Dias Úteis**: Quantidade de dias úteis trabalhados
- **Fins de Semana**: Quantidade de sábados/domingos trabalhados

**Exemplo de resposta:**
```
📅 Resumo Semanal - João Silva

⏱️ Horas Brutas: 42.5h
🍽️ Desconto Almoço: 5.0h
✅ Horas Líquidas: 37.5h

📊 Média Diária Bruta: 8.5h
📊 Média Diária Líquida: 7.5h

📝 Apontamentos: 25
📅 Dias Úteis: 5
🏖️ Fins de Semana: 0
```

---

### ✅ `consultar_periodo(data_inicio, data_fim, usuario)`

**Informações exibidas:**
- **Período**: Data inicial e final
- **Horas Brutas/Líquidas**: Com detalhamento de desconto
- **Médias**: Por dia (bruta e líquida)
- **Estatísticas de dias**: Úteis, fins de semana e total

**Exemplo de resposta:**
```
📅 Período: 2025-11-01 a 2025-11-30

👤 Usuário: Maria Santos

⏱️ Horas Brutas: 176.0h
🍽️ Desconto Almoço: 22.0h
✅ Horas Líquidas: 154.0h

📊 Média Bruta: 8.0h/dia
📊 Média Líquida: 7.0h/dia

📝 Apontamentos: 110
📅 Dias Úteis: 22
🏖️ Fins de Semana: 0
📆 Total de Dias: 22
```

---

## 🎯 Casos de Uso

### Caso 1: Consulta de Hoje (Dia Útil)
```python
agente = AgenteApontamentos()
resultado = agente.apontamentos_hoje("João Silva")

# Resultado mostra:
# - Horas brutas: 8.5h
# - Desconto: 1.0h
# - Horas líquidas: 7.5h
```

### Caso 2: Consulta de Hoje (Fim de Semana)
```python
agente = AgenteApontamentos()
resultado = agente.apontamentos_hoje("Maria Santos")

# Resultado mostra:
# - Horas brutas: 4.0h
# - Desconto: 0.0h (sem desconto em fim de semana)
# - Horas líquidas: 4.0h
```

### Caso 3: Resumo Semanal
```python
agente = AgenteApontamentos()
resultado = agente.resumo_semanal("Carlos Oliveira")

# Resultado mostra:
# - Total de 5 dias úteis trabalhados
# - 1 fim de semana trabalhado
# - Desconto de 5.0h (1h x 5 dias úteis)
```

---

## 🔄 Compatibilidade com Bot Framework

A funcionalidade é **totalmente compatível** com:

### Microsoft Teams Bot
```python
# O bot automaticamente aplica as regras
@bot.message_handler
async def handle_message(turn_context):
    usuario = turn_context.activity.from_property.name
    mensagem = turn_context.activity.text
    
    # Agente aplica regras automaticamente
    resultado = agente.responder_pergunta(mensagem, usuario)
    await turn_context.send_activity(resultado['resposta'])
```

### Adaptive Cards
Os cards podem exibir as informações estruturadas:
```python
{
    "dados": {
        "total_horas_brutas": 8.5,
        "total_horas_liquidas": 7.5,
        "desconto_almoco": 1.0,
        "dia_util": True,
        "tipo_dia": "📅 Dia Útil"
    }
}
```

---

## 📈 Dados Retornados

Todos os métodos atualizados retornam dados estruturados incluindo:

```python
{
    "resposta": "Texto formatado para exibição",
    "dados": {
        "total_horas_brutas": float,      # Horas sem desconto
        "total_horas_liquidas": float,    # Horas com desconto
        "desconto_almoco": float,         # Valor descontado
        "dia_util": bool,                 # Se é dia útil
        "tipo_dia": str,                  # Descrição do tipo de dia
        "dias_uteis": int,                # Quantidade de dias úteis
        "dias_fim_semana": int            # Quantidade de fins de semana
    },
    "tipo": "tipo_da_consulta"
}
```

---

## 🚀 Integração com API

A funcionalidade está integrada à API REST do bot:

```python
# GET /api/apontamentos/hoje/{usuario}
# Retorna apontamentos de hoje com cálculo de horas líquidas

# GET /api/apontamentos/semana/{usuario}
# Retorna resumo semanal com separação dias úteis/fins de semana

# POST /api/apontamentos/periodo
# Body: { "data_inicio": "DD/MM/YYYY", "data_fim": "DD/MM/YYYY", "usuario": "nome" }
# Retorna consulta com detalhamento completo
```

---

## 🔮 Melhorias Futuras

### 1. Feriados Nacionais
```python
# TODO: Implementar verificação de feriados
# Possível integração com:
# - API de feriados brasileiros
# - Lista configurável de feriados
# - Feriados estaduais/municipais
```

### 2. Configuração de Desconto
```python
# TODO: Permitir configuração do tempo de almoço
# - 1h (padrão)
# - 0.5h, 1.5h, 2h (configurável)
```

### 3. Horários de Trabalho
```python
# TODO: Validação de horários de trabalho
# - Horário comercial: 8h às 18h
# - Alertas para apontamentos fora do horário
```

---

## 📝 Notas Importantes

1. **Desconto Fixo**: O desconto de almoço é fixo em 1 hora para dias úteis
2. **Não há Desconto Negativo**: Se as horas forem menores que 1h, o resultado será 0h
3. **Fins de Semana**: Não recebem desconto de almoço
4. **Compatibilidade**: Funcionalidade alinhada com projeto Streamlit existente
5. **Dados Históricos**: A lógica é aplicada em tempo real, não modifica dados originais

---

## 🧪 Testando a Funcionalidade

### Teste Manual
```python
from agente_apontamentos import AgenteApontamentos

# Inicializar agente
agente = AgenteApontamentos()

# Testar consulta de hoje
resultado = agente.apontamentos_hoje("Seu Nome")
print(resultado['resposta'])

# Testar resumo semanal
resultado = agente.resumo_semanal("Seu Nome")
print(resultado['resposta'])
```

### Teste via Bot Emulator
1. Abra o Bot Framework Emulator
2. Conecte ao bot local
3. Digite: "Quanto apontei hoje?"
4. Verifique se mostra horas brutas, desconto e horas líquidas

### Teste via Teams
1. Instale o bot no Teams
2. Envie mensagem: "resumo da semana"
3. Verifique separação entre dias úteis e fins de semana

---

## ✅ Conclusão

A funcionalidade de dias úteis e desconto de almoço está **totalmente implementada** e **pronta para uso** no bot do Microsoft Teams. Todos os cálculos são feitos automaticamente e as informações são apresentadas de forma clara e estruturada para o usuário.
