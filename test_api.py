"""
API de teste simplificada - sem Bot Framework
Para testar a estrutura básica com Swagger completo
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Adicionar path para importar agente
sys.path.insert(0, str(Path(__file__).parent))

# Importar modelos Pydantic
from bot.models import (
    PerguntaRequest,
    PerguntaResponse,
    HealthResponse,
    APIInfoResponse,
    EndpointInfo,
    ErroResponse
)

app = FastAPI(
    title="🤖 Bot Teams - API de Apontamentos",
    description="""
## API para consulta de dados de apontamentos via Microsoft Teams

Esta API permite interagir com o agente de apontamentos através de perguntas em linguagem natural.

### 🎯 Funcionalidades Principais

* **Consultas em Linguagem Natural:** Pergunte sobre dados de apontamentos
* **Estatísticas:** Médias, totais, comparações
* **Rankings:** Top funcionários por horas trabalhadas
* **Análises:** Outliers, padrões, tendências
* **Períodos:** Hoje, semana, mês, customizado

### 📊 Exemplos de Perguntas

* "Qual a média de horas trabalhadas?"
* "Quem são os top 5 funcionários do mês?"
* "Quantas pessoas trabalharam menos de 6 horas hoje?"
* "Mostre os outliers da semana"

### 🔗 Links Úteis

* [GitHub](https://github.com/ElaineMBarros/Blocks_teams_apontamento)
* [Documentação Completa](https://github.com/ElaineMBarros/Blocks_teams_apontamento#readme)
    """,
    version="1.0.0",
    contact={
        "name": "Equipe de Desenvolvimento",
        "url": "https://github.com/ElaineMBarros/Blocks_teams_apontamento",
        "email": "contato@exemplo.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Sistema",
            "description": "Endpoints de informações e status do sistema"
        },
        {
            "name": "Consultas",
            "description": "Endpoints para consultar dados de apontamentos"
        }
    ]
)

# Tentar importar agente
try:
    from agente_apontamentos import AgenteApontamentos
    agente = AgenteApontamentos()
    agente_disponivel = True
    print("✅ Agente carregado com sucesso!")
except Exception as e:
    agente = None
    agente_disponivel = False
    print(f"⚠️ Agente não disponível: {e}")


@app.get(
    "/",
    response_model=APIInfoResponse,
    tags=["Sistema"],
    summary="Informações da API",
    description="Retorna informações gerais sobre a API, versão e endpoints disponíveis"
)
async def root() -> APIInfoResponse:
    """
    ## Informações da API
    
    Este endpoint retorna:
    - Nome e versão da API
    - Status atual do serviço
    - Disponibilidade do agente
    - Lista de endpoints disponíveis
    
    ### Uso
    Simplesmente acesse a raiz da API para obter estas informações.
    """
    return APIInfoResponse(
        name="Bot Teams - API de Apontamentos",
        version="1.0.0",
        status="running",
        agente_disponivel=agente_disponivel,
        endpoints=[
            EndpointInfo(path="/", method="GET", description="Informações da API"),
            EndpointInfo(path="/health", method="GET", description="Verificação de saúde do serviço"),
            EndpointInfo(path="/api/pergunta", method="POST", description="Enviar pergunta ao agente")
        ]
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Sistema"],
    summary="Health Check",
    description="Verifica se o serviço está funcionando e se o agente está disponível",
    responses={
        200: {
            "description": "Serviço funcionando normalmente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "agente": "available"
                    }
                }
            }
        }
    }
)
async def health() -> HealthResponse:
    """
    ## Verificação de Saúde
    
    Este endpoint é usado para:
    - Monitoramento da aplicação
    - Verificar se o agente está carregado
    - Health checks de infraestrutura
    
    ### Status Possíveis
    - **healthy**: Serviço operacional
    - **agente**: available | unavailable
    """
    return HealthResponse(
        status="healthy",
        agente="available" if agente_disponivel else "unavailable"
    )


@app.post(
    "/api/pergunta",
    response_model=PerguntaResponse,
    tags=["Consultas"],
    summary="Fazer Pergunta ao Agente",
    description="Envia uma pergunta em linguagem natural para o agente de apontamentos",
    responses={
        200: {
            "description": "Pergunta processada com sucesso",
            "content": {
                "application/json": {
                    "examples": {
                        "estatistica": {
                            "summary": "Estatística Geral",
                            "value": {
                                "sucesso": True,
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
                        },
                        "ranking": {
                            "summary": "Ranking de Funcionários",
                            "value": {
                                "sucesso": True,
                                "resultado": {
                                    "tipo": "ranking",
                                    "resposta": "Top 3 funcionários do mês",
                                    "dados": {
                                        "ranking": [
                                            {"nome": "João Silva", "total_horas": 176.5},
                                            {"nome": "Maria Santos", "total_horas": 172.0},
                                            {"nome": "Pedro Costa", "total_horas": 168.5}
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        503: {
            "description": "Agente não disponível",
            "model": ErroResponse
        },
        500: {
            "description": "Erro interno no processamento",
            "model": ErroResponse
        }
    }
)
async def fazer_pergunta(pergunta: PerguntaRequest) -> PerguntaResponse:
    """
    ## Fazer Pergunta ao Agente
    
    Envia uma pergunta em linguagem natural e recebe a resposta processada.
    
    ### 📝 Exemplos de Perguntas
    
    **Estatísticas:**
    - "Qual a média de horas trabalhadas?"
    - "Quantos apontamentos temos no total?"
    - "Qual a duração média por dia?"
    
    **Rankings:**
    - "Quem são os top 5 funcionários?"
    - "Mostre o ranking de horas do mês"
    - "Quem trabalhou mais horas?"
    
    **Análises:**
    - "Quantas pessoas trabalharam menos de 6 horas hoje?"
    - "Mostre os outliers da semana"
    - "Quais apontamentos estão fora do padrão?"
    
    **Períodos:**
    - "Dados de hoje"
    - "Resumo da semana"
    - "Estatísticas do mês"
    
    ### 💡 Dicas
    
    - Use linguagem natural e clara
    - Seja específico sobre o período desejado
    - Opcionalmente, informe o usuário para contexto
    """
    if not agente_disponivel:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agente de apontamentos não está disponível no momento"
        )
    
    try:
        resultado = agente.responder_pergunta(pergunta.pergunta, pergunta.usuario)
        
        return PerguntaResponse(
            sucesso=True,
            resultado=resultado
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pergunta: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Iniciando API de Teste")
    print("="*60)
    print(f"✅ FastAPI: OK")
    print(f"{'✅' if agente_disponivel else '⚠️'} Agente: {'Disponível' if agente_disponivel else 'Não disponível'}")
    print("\n📍 Acesse: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
