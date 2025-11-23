"""
API REST Simples para o Bot de Apontamentos
SEM dependência do Azure Bot Service
"""
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

# Importar o agente
try:
    from agente_apontamentos import AgenteApontamentos
    print("🔧 Inicializando agente...", flush=True)
    agente = AgenteApontamentos()
    registros = len(agente.df) if agente.df is not None else 0
    print(f"✅ Agente carregado com {registros} registros", flush=True)
except Exception as e:
    print(f"⚠️ Erro ao carregar agente: {e}", flush=True)
    agente = None

# Importar IA conversacional
try:
    from bot.ai_conversation import ConversacaoIA
    conversacao_ia = ConversacaoIA(agente) if agente else None
    print("✅ IA Conversacional carregada", flush=True)
except Exception as e:
    print(f"⚠️ IA não disponível: {e}", flush=True)
    conversacao_ia = None

app = FastAPI(title="Bot de Apontamentos - API Simples")

# CORS - permitir qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensagem(BaseModel):
    texto: str
    usuario: str = "Usuário Web"
    sessao: str = "web-session"

class Resposta(BaseModel):
    resposta: str
    tipo: str
    dados: Any = {}

@app.get("/")
async def root():
    return {
        "nome": "Bot de Apontamentos",
        "versao": "1.0",
        "status": "online",
        "agente_disponivel": agente is not None,
        "registros": len(agente.df) if agente and agente.df is not None else 0,
        "ia_disponivel": conversacao_ia is not None
    }

@app.get("/health")
async def health():
    """Health check para Railway"""
    return {"status": "ok"}

@app.post("/chat", response_model=Resposta)
async def chat(mensagem: Mensagem):
    """
    Endpoint principal para conversar com o bot
    """
    print(f"📨 Mensagem recebida: {mensagem.texto[:50]}... de {mensagem.usuario}", flush=True)
    
    if not agente:
        return Resposta(
            resposta="⚠️ Sistema em manutenção. Os dados ainda estão sendo carregados. Por favor, tente novamente em alguns minutos.",
            tipo="aviso",
            dados={}
        )
    
    try:
        # Usar IA conversacional se disponível
        if conversacao_ia:
            print(f"🤖 Usando IA conversacional...", flush=True)
            resultado = conversacao_ia.processar_mensagem(
                mensagem.texto,
                mensagem.usuario,
                mensagem.sessao
            )
        else:
            print(f"📊 Usando agente direto...", flush=True)
            resultado = agente.responder_pergunta(mensagem.texto, mensagem.usuario)
        
        print(f"✅ Resultado obtido: {type(resultado)}", flush=True)
        
        # Formatar resposta com HTML se tiver dados estruturados
        resposta_texto = resultado.get('resposta', 'Sem resposta')
        dados = resultado.get('dados', {})
        
        # Se tiver tabela, formatar em HTML
        if 'tabela' in dados or 'registros' in dados:
            resposta_texto = formatar_resposta_html(resposta_texto, dados)
        
        return Resposta(
            resposta=resposta_texto,
            tipo=resultado.get('tipo', 'info'),
            dados=dados
        )
    
    except Exception as e:
        print(f"❌ ERRO no chat: {type(e).__name__}: {str(e)}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")

def formatar_resposta_html(texto, dados):
    """Formata resposta com HTML bonito"""
    
    # Converter texto com quebras de linha para HTML
    # Substituir \n por <br> SEMPRE
    texto_html = texto.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    # Detectar se é ranking pelo texto
    is_ranking = '🏆' in texto or 'Top ' in texto or 'Ranking' in texto.lower()
    
    if is_ranking:
        # Formatar ranking especial
        html = "<div class='ranking-card'>"
        html += "<div class='ranking-header'>🏆 Top 10 - Horas Trabalhadas</div>"
        html += "<div class='ranking-list'>"
        
        # Remover markdown ** do texto
        texto_limpo = texto.replace('**', '')
        
        # Extrair linhas do ranking (pular o título)
        linhas = texto_limpo.split('\n')
        linhas_dados = []
        
        for linha in linhas:
            linha = linha.strip()
            # Procurar linhas que começam com número seguido de ponto
            if linha and linha[0].isdigit() and '.' in linha and ':' in linha and 'h' in linha:
                linhas_dados.append(linha)
        
        for i, linha in enumerate(linhas_dados[:10], 1):
            try:
                # Parse: "1. RECURSO_62702985: 1103.52h (193 apontamentos)"
                # Separar posição do resto
                partes = linha.split('.', 1)
                if len(partes) < 2:
                    continue
                    
                resto = partes[1].strip()
                
                # Separar recurso de info
                partes2 = resto.split(':', 1)
                if len(partes2) < 2:
                    continue
                    
                recurso = partes2[0].strip()
                info = partes2[1].strip()
                
                # Extrair horas
                horas = info.split('h')[0].strip()
                
                # Extrair apontamentos
                apontamentos = ''
                if '(' in info:
                    apontamentos = info.split('(')[1].split('apontamentos')[0].strip()
                
                # Emoji de medalha para top 3
                emoji = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f"{i}º"
                
                html += f"""
                <div class='ranking-item rank-{i}'>
                    <div class='rank-position'>{emoji}</div>
                    <div class='rank-info'>
                        <div class='rank-recurso'>{recurso}</div>
                        <div class='rank-stats'>
                            <span class='rank-horas'>⏱️ {horas}h</span>
                            <span class='rank-apontamentos'>📝 {apontamentos} apontamentos</span>
                        </div>
                    </div>
                </div>
                """
            except Exception as e:
                print(f"⚠️ Erro ao parsear linha: {linha} - {e}")
                continue
        
        html += "</div></div>"
        return html
    
    # Formato padrão com quebras de linha
    html = f"<div class='resposta-bot'>{texto_html}</div>"
    
    # Se tiver estatísticas
    if 'total_horas' in dados or 'media_horas' in dados:
        html += "<div class='stats-card'>"
        if 'total_horas' in dados:
            html += f"<div class='stat-item'><span class='stat-label'>📊 Total:</span> <span class='stat-value'>{dados['total_horas']}</span></div>"
        if 'media_horas' in dados:
            html += f"<div class='stat-item'><span class='stat-label'>📈 Média:</span> <span class='stat-value'>{dados['media_horas']}</span></div>"
        if 'registros' in dados:
            html += f"<div class='stat-item'><span class='stat-label'>📝 Registros:</span> <span class='stat-value'>{dados['registros']}</span></div>"
        html += "</div>"
    
    # Se tiver tabela
    if 'tabela' in dados:
        tabela = dados['tabela']
        if isinstance(tabela, list) and len(tabela) > 0:
            html += "<div class='tabela-card'><table class='dados-tabela'>"
            
            # Cabeçalho
            html += "<thead><tr>"
            for col in tabela[0].keys():
                html += f"<th>{col}</th>"
            html += "</tr></thead>"
            
            # Dados (máximo 10 linhas)
            html += "<tbody>"
            for row in tabela[:10]:
                html += "<tr>"
                for val in row.values():
                    html += f"<td>{val}</td>"
                html += "</tr>"
            html += "</tbody></table>"
            
            if len(tabela) > 10:
                html += f"<div class='tabela-info'>Mostrando 10 de {len(tabela)} registros</div>"
            
            html += "</div>"
    
    return html

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agente": agente is not None,
        "ia": conversacao_ia is not None
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Iniciando API Simples na porta {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
