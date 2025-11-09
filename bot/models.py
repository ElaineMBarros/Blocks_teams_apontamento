"""
Modelos Pydantic para API do Bot
Usado para validação e documentação automática no Swagger
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class TipoPergunta(str, Enum):
    """Tipos de perguntas suportadas pelo agente"""
    ESTATISTICA_GERAL = "estatistica_geral"
    RANKING = "ranking"
    USUARIO_INDIVIDUAL = "usuario_individual"
    OUTLIERS = "outliers"
    HOJE = "hoje"
    SEMANA = "semana"
    PERIODO = "periodo"


class PerguntaRequest(BaseModel):
    """
    Requisição para fazer uma pergunta ao agente
    """
    pergunta: str = Field(
        ...,
        description="Pergunta em linguagem natural",
        example="Qual a média de horas trabalhadas?"
    )
    usuario: Optional[str] = Field(
        None,
        description="Nome do usuário fazendo a pergunta (opcional)",
        example="João Silva"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "pergunta": "Qual a média de horas trabalhadas?",
                    "usuario": "João Silva"
                },
                {
                    "pergunta": "Quem são os top 5 funcionários do mês?",
                    "usuario": "Maria Santos"
                },
                {
                    "pergunta": "Quantas pessoas trabalharam menos de 6 horas hoje?"
                }
            ]
        }


class EstatisticaResponse(BaseModel):
    """Resposta com estatísticas gerais"""
    tipo: str = Field(..., description="Tipo de resposta")
    media_horas: float = Field(..., description="Média de horas em decimal")
    formatado: str = Field(..., description="Média formatada (HH:MM)")
    total_apontamentos: int = Field(..., description="Total de registros")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "estatistica_geral",
                "media_horas": 8.5,
                "formatado": "08:30",
                "total_apontamentos": 1250
            }
        }


class RankingItem(BaseModel):
    """Item do ranking"""
    nome: str = Field(..., description="Nome do funcionário")
    total_horas: float = Field(..., description="Total de horas trabalhadas")
    num_apontamentos: int = Field(..., description="Número de apontamentos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "total_horas": 176.5,
                "num_apontamentos": 22
            }
        }


class RankingResponse(BaseModel):
    """Resposta com ranking de funcionários"""
    tipo: str = Field(..., description="Tipo de resposta")
    ranking: List[RankingItem] = Field(..., description="Lista ordenada por horas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "ranking",
                "ranking": [
                    {"nome": "João Silva", "total_horas": 176.5, "num_apontamentos": 22},
                    {"nome": "Maria Santos", "total_horas": 172.0, "num_apontamentos": 21},
                    {"nome": "Pedro Costa", "total_horas": 168.5, "num_apontamentos": 20}
                ]
            }
        }


class ErroResponse(BaseModel):
    """Resposta de erro"""
    erro: str = Field(..., description="Descrição do erro")
    tipo: Optional[str] = Field(None, description="Tipo de erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "erro": "Agente não disponível",
                "tipo": "servico_indisponivel"
            }
        }


class PerguntaResponse(BaseModel):
    """Resposta genérica para pergunta"""
    sucesso: bool = Field(..., description="Se a operação foi bem-sucedida")
    resultado: Dict[str, Any] = Field(..., description="Resultado da pergunta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "resultado": {
                    "tipo": "estatistica_geral",
                    "resposta": "A média de horas trabalhadas é 08:30",
                    "dados": {
                        "media_horas": 8.5,
                        "formatado": "08:30"
                    }
                }
            }
        }


class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: str = Field(..., description="Status do serviço")
    agente: str = Field(..., description="Status do agente de apontamentos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "agente": "available"
            }
        }


class EndpointInfo(BaseModel):
    """Informação de um endpoint"""
    path: str = Field(..., description="Caminho do endpoint")
    method: str = Field(..., description="Método HTTP")
    description: str = Field(..., description="Descrição do endpoint")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "/test/pergunta",
                "method": "POST",
                "description": "Enviar pergunta ao agente"
            }
        }


class APIInfoResponse(BaseModel):
    """Informações da API"""
    name: str = Field(..., description="Nome da API")
    version: str = Field(..., description="Versão")
    status: str = Field(..., description="Status atual")
    agente_disponivel: bool = Field(..., description="Se o agente está disponível")
    endpoints: List[EndpointInfo] = Field(..., description="Lista de endpoints")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bot Teams - API de Teste",
                "version": "0.1.0",
                "status": "running",
                "agente_disponivel": True,
                "endpoints": [
                    {"path": "/", "method": "GET", "description": "Info da API"},
                    {"path": "/health", "method": "GET", "description": "Health check"}
                ]
            }
        }
