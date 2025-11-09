"""
API de teste simplificada - sem Bot Framework
Para testar a estrutura básica
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Adicionar path para importar agente
sys.path.insert(0, str(Path(__file__).parent))

app = FastAPI(
    title="Bot Teams - API de Teste",
    description="API simplificada para testar estrutura",
    version="0.1.0"
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


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "name": "Bot Teams - Teste",
        "version": "0.1.0",
        "status": "running",
        "agente_disponivel": agente_disponivel,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Info da API"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/test/pergunta", "method": "POST", "description": "Testar pergunta ao agente"}
        ]
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agente": "available" if agente_disponivel else "unavailable"
    }


@app.post("/test/pergunta")
async def test_pergunta(pergunta: dict):
    """
    Testar pergunta ao agente
    Body: {"pergunta": "sua pergunta", "usuario": "nome (opcional)"}
    """
    if not agente_disponivel:
        return JSONResponse(
            status_code=503,
            content={"erro": "Agente não disponível"}
        )
    
    try:
        texto = pergunta.get("pergunta", "")
        usuario = pergunta.get("usuario", None)
        
        resultado = agente.responder_pergunta(texto, usuario)
        
        return {
            "sucesso": True,
            "resultado": resultado
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": str(e)}
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
