# 📘 Guia da API - Swagger Documentation

## 🎯 Visão Geral

A API do Bot Teams possui documentação interativa completa via **Swagger UI**, gerada automaticamente pelo FastAPI.

---

## 🌐 Acessando o Swagger

### Desenvolvimento Local

```bash
# 1. Iniciar servidor
python test_api.py

# 2. Acessar Swagger UI
http://localhost:8000/docs

# 3. Acessar ReDoc (alternativa)
http://localhost:8000/redoc

# 4. Baixar OpenAPI Schema
http://localhost:8000/openapi.json
```

### Produção (Azure)

```bash
# Swagger UI
https://seu-app.azurewebsites.net/docs

# ReDoc
https://seu-app.azurewebsites.net/redoc

# OpenAPI Schema
https://seu-app.azurewebsites.net/openapi.json
```

---

## 📋 Endpoints Disponíveis

### 1. Sistema

#### GET `/`
**Informações da API**

Retorna dados gerais sobre a API.

```json
{
  "name": "Bot Teams - API de Apontamentos",
  "version": "1.0.0",
  "status": "running",
  "agente_disponivel": true,
  "endpoints": [...]
}
```

**Uso:**
```bash
curl http://localhost:8000/
```

---

#### GET `/health`
**Health Check**

Verifica saúde do serviço e disponibilidade do agente.

```json
{
  "status": "healthy",
  "agente": "available"
}
```

**Uso:**
```bash
curl http://localhost:8000/health
```

**Status Possíveis:**
- `healthy` - Serviço operacional
- `agente`: `available` | `unavailable`

---

### 2. Consultas

#### POST `/api/pergunta`
**Fazer Pergunta ao Agente**

Envia pergunta em linguagem natural para processamento.

**Request Body:**
```json
{
  "pergunta": "Qual a média de horas trabalhadas?",
  "usuario": "João Silva"  // opcional
}
```

**Response 200 - Sucesso:**
```json
{
  "sucesso": true,
  "resultado": {
    "tipo": "estatistica_geral",
    "resposta": "A média de horas trabalhadas é 08:30",
    "dados": {
      "media_horas": 8.5,
      "formatado": "08:30",
      "total_apontamentos": 1250
    }
  }
}
```

**Response 503 - Agente Indisponível:**
```json
{
  "detail": "Agente de apontamentos não está disponível no momento"
}
```

**Response 500 - Erro Interno:**
```json
{
  "detail": "Erro ao processar pergunta: [detalhes]"
}
```

**Uso:**
```bash
curl -X POST http://localhost:8000/api/pergunta \
  -H "Content-Type: application/json" \
  -d '{
    "pergunta": "Qual a média de horas?",
    "usuario": "João Silva"
  }'
```

---

## 📊 Exemplos de Perguntas

### Estatísticas Gerais

```json
{
  "pergunta": "Qual a média de horas trabalhadas?"
}
```

```json
{
  "pergunta": "Quantos apontamentos temos no total?"
}
```

```json
{
  "pergunta": "Qual a duração média por dia?"
}
```

### Rankings

```json
{
  "pergunta": "Quem são os top 5 funcionários?"
}
```

```json
{
  "pergunta": "Mostre o ranking de horas do mês"
}
```

```json
{
  "pergunta": "Quem trabalhou mais horas?"
}
```

### Análises

```json
{
  "pergunta": "Quantas pessoas trabalharam menos de 6 horas hoje?"
}
```

```json
{
  "pergunta": "Mostre os outliers da semana"
}
```

```json
{
  "pergunta": "Quais apontamentos estão fora do padrão?"
}
```

### Períodos Específicos

```json
{
  "pergunta": "Dados de hoje"
}
```

```json
{
  "pergunta": "Resumo da semana"
}
```

```json
{
  "pergunta": "Estatísticas do mês"
}
```

---

## 🔧 Recursos do Swagger UI

### 1. Try it Out
Teste endpoints diretamente no navegador:
1. Clique em um endpoint
2. Clique em "Try it out"
3. Preencha os parâmetros
4. Clique em "Execute"
5. Veja a resposta

### 2. Schemas
Visualize modelos de dados:
- Scroll até "Schemas" no final da página
- Veja estrutura completa de request/response
- Campos obrigatórios marcados

### 3. Autorização
Para APIs com autenticação:
- Clique no botão "Authorize"
- Insira credenciais
- Todos os requests usarão automaticamente

### 4. Download
Baixe a especificação OpenAPI:
- Acesse `/openapi.json`
- Use em ferramentas como Postman
- Gere clientes automaticamente

---

## 📝 Modelos de Dados

### PerguntaRequest
```python
{
  "pergunta": str,      # Obrigatório
  "usuario": str | None  # Opcional
}
```

### PerguntaResponse
```python
{
  "sucesso": bool,
  "resultado": {
    "tipo": str,
    "resposta": str,
    "dados": object
  }
}
```

### HealthResponse
```python
{
  "status": str,
  "agente": str
}
```

### APIInfoResponse
```python
{
  "name": str,
  "version": str,
  "status": str,
  "agente_disponivel": bool,
  "endpoints": [
    {
      "path": str,
      "method": str,
      "description": str
    }
  ]
}
```

---

## 🧪 Testando com Ferramentas

### cURL

```bash
# GET
curl http://localhost:8000/health

# POST
curl -X POST http://localhost:8000/api/pergunta \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "média de horas"}'
```

### Postman

1. Importe OpenAPI: `http://localhost:8000/openapi.json`
2. Collection será criada automaticamente
3. Teste todos os endpoints

### Python Requests

```python
import requests

# GET
response = requests.get("http://localhost:8000/health")
print(response.json())

# POST
data = {
    "pergunta": "Qual a média de horas?",
    "usuario": "João Silva"
}
response = requests.post(
    "http://localhost:8000/api/pergunta",
    json=data
)
print(response.json())
```

### JavaScript Fetch

```javascript
// GET
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log(data));

// POST
fetch('http://localhost:8000/api/pergunta', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    pergunta: 'Qual a média de horas?',
    usuario: 'João Silva'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 🎨 Customizações

### Alterando Título e Descrição

Edite `test_api.py`:

```python
app = FastAPI(
    title="Seu Título",
    description="Sua descrição...",
    version="2.0.0"
)
```

### Adicionando Tags

```python
@app.post("/endpoint", tags=["Categoria"])
async def endpoint():
    pass
```

### Exemplos Personalizados

```python
@app.post(
    "/endpoint",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"key": "value"}
                }
            }
        }
    }
)
```

---

## 📦 Exportando Documentação

### OpenAPI JSON

```bash
# Salvar especificação
curl http://localhost:8000/openapi.json > api-spec.json
```

### Gerar Clientes

```bash
# Instalar gerador
npm install -g @openapitools/openapi-generator-cli

# Gerar cliente Python
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client

# Gerar cliente JavaScript
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g javascript \
  -o ./js-client
```

---

## 🔒 Segurança

### CORS

Configurado em `test_api.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Produção: especificar domínios
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### Rate Limiting

```bash
# Instalar
pip install slowapi

# Configurar
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/pergunta")
@limiter.limit("10/minute")
async def fazer_pergunta():
    pass
```

---

## 📊 Monitoramento

### Logs

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/pergunta")
async def fazer_pergunta(pergunta: PerguntaRequest):
    logger.info(f"Pergunta recebida: {pergunta.pergunta}")
    # ...
```

### Métricas

```bash
# Instalar Prometheus
pip install prometheus-fastapi-instrumentator

# Configurar
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# Acessar métricas
http://localhost:8000/metrics
```

---

## 🎓 Boas Práticas

### 1. Versionamento

```python
# v1
@app.post("/v1/api/pergunta")

# v2
@app.post("/v2/api/pergunta")
```

### 2. Paginação

```python
@app.get("/api/dados")
async def listar(skip: int = 0, limit: int = 100):
    return dados[skip : skip + limit]
```

### 3. Filtros

```python
@app.get("/api/apontamentos")
async def filtrar(
    data_inicio: str = None,
    data_fim: str = None,
    usuario: str = None
):
    # Filtrar dados
    pass
```

### 4. Ordenação

```python
@app.get("/api/ranking")
async def ranking(ordem: str = "desc"):
    # Ordenar dados
    pass
```

---

## 🔗 Links Úteis

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **OpenAPI Spec:** https://swagger.io/specification/
- **Swagger UI:** https://swagger.io/tools/swagger-ui/
- **ReDoc:** https://redocly.com/redoc/
- **OpenAPI Generator:** https://openapi-generator.tech/

---

## 💡 Dicas

1. **Swagger UI:** Melhor para testes interativos
2. **ReDoc:** Melhor para documentação de leitura
3. **OpenAPI JSON:** Use para integração com outras ferramentas
4. **Modelos Pydantic:** Validação automática e documentação
5. **Exemplos:** Adicione muitos exemplos para clareza
6. **Tags:** Organize endpoints em categorias
7. **Descrições:** Seja claro e detalhado
8. **Status Codes:** Documente todos os possíveis retornos

---

**Última atualização:** 09/11/2025  
**Versão da API:** 1.0.0
