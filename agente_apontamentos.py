"""
🤖 AGENTE INTELIGENTE DE APONTAMENTOS
API para consultas dinâmicas sobre dados de apontamento
Preparado para integração com chatbot do Microsoft Teams
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import glob
import calendar
import os
from pathlib import Path
from io import BytesIO

# Tentar importar azure-storage-blob
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_STORAGE_AVAILABLE = True
    print("✅ Azure Storage Blob SDK disponível")
except ImportError as e:
    AZURE_STORAGE_AVAILABLE = False
    print(f"⚠️ Azure Storage Blob SDK não disponível: {e}")

class AgenteApontamentos:
    """
    Agente inteligente que responde perguntas sobre apontamentos
    Pode ser integrado a chatbots (Teams, Slack, etc.)
    """
    
    def __init__(self):
        """Inicializa o agente e carrega dados"""
        self.df = None
        self.ultima_atualizacao = None
        self.carregar_dados()
        
    def carregar_dados(self) -> bool:
        """Carrega os dados mais recentes de apontamentos"""
        try:
            # URL do CSV no HostGator (fallback confiável)
            CSV_URL = os.getenv('CSV_URL', 'https://multibeat.com.br/apontamentos/dados/dados_anonimizados_decupado_20251118_211544.csv')
            
            # Método 1: Tentar carregar via URL HTTP (HostGator ou Azure público)
            if CSV_URL:
                try:
                    import requests
                    print(f"🌐 Tentando carregar CSV via URL: {CSV_URL[:80]}...", flush=True)
                    
                    # Headers para evitar bloqueio do HostGator
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/csv,text/plain,*/*'
                    }
                    
                    response = requests.get(CSV_URL, headers=headers, timeout=120)
                    response.raise_for_status()
                    
                    csv_bytes = response.content
                    print(f"✅ CSV baixado via HTTP ({len(csv_bytes)/1024/1024:.1f}MB)", flush=True)
                    self.df = pd.read_csv(BytesIO(csv_bytes), encoding='utf-8-sig', low_memory=False)
                    print(f"✅ Dados carregados via URL: {len(self.df)} registros", flush=True)
                    print(f"🔍 Colunas disponíveis: {list(self.df.columns[:10])}...", flush=True)
                    # NÃO retornar aqui - continuar para calcular duração
                except Exception as e:
                    print(f"⚠️ Erro ao carregar via URL: {e}", flush=True)
                except Exception as e:
                    print(f"⚠️ Erro ao carregar via URL: {e}", flush=True)
            
            # Método 2: Tentar Azure Blob Storage com connection string
            azure_conn_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            
            if not azure_conn_str:
                try:
                    from config_azure import AZURE_STORAGE_CONNECTION_STRING, BLOB_CONTAINER_NAME, BLOB_FILE_NAME
                    azure_conn_str = AZURE_STORAGE_CONNECTION_STRING
                    container_name = BLOB_CONTAINER_NAME
                    blob_name = BLOB_FILE_NAME
                    print("📋 Usando configuração do arquivo config_azure.py", flush=True)
                except ImportError:
                    print("⚠️ Arquivo config_azure.py não encontrado", flush=True)
                    container_name = "dados"
                    blob_name = "dados_anonimizados_decupado_20251118_211544.csv"
            else:
                print("📋 Usando AZURE_STORAGE_CONNECTION_STRING de variável de ambiente", flush=True)
                container_name = "dados"
                blob_name = "dados_anonimizados_decupado_20251118_211544.csv"
            
            print(f"🔍 AZURE_STORAGE_CONNECTION_STRING definida: {bool(azure_conn_str)}", flush=True)
            print(f"🔍 AZURE_STORAGE_AVAILABLE: {AZURE_STORAGE_AVAILABLE}", flush=True)
            
            if azure_conn_str and AZURE_STORAGE_AVAILABLE:
                try:
                    print(f"📦 Tentando carregar CSV do Azure Blob Storage: {container_name}/{blob_name}", flush=True)
                    blob_service = BlobServiceClient.from_connection_string(azure_conn_str)
                    container_client = blob_service.get_container_client(container_name)
                    blob_client = container_client.get_blob_client(blob_name)
                    
                    # Download do blob para memória
                    blob_data = blob_client.download_blob()
                    csv_bytes = blob_data.readall()
                    
                    print(f"✅ CSV baixado do Azure Storage ({len(csv_bytes)/1024/1024:.1f}MB)", flush=True)
                    self.df = pd.read_csv(BytesIO(csv_bytes), encoding='utf-8-sig', low_memory=False)
                    print(f"✅ Dados carregados do Azure Storage: {len(self.df)} registros", flush=True)
                    # NÃO retornar aqui - continuar para calcular duração
                except Exception as e:
                    print(f"⚠️ Erro ao carregar do Azure Storage: {e}", flush=True)
                    print("🔄 Tentando carregar do sistema de arquivos local...", flush=True)
            
            # Método 3: Fallback - carregar do sistema de arquivos local
            if self.df is None:
                # Determinar diretório base (onde está o script ou /home/site/wwwroot no Azure)
                base_dir = Path(__file__).parent
                resultados_dir = base_dir / "resultados"
                
                # Buscar arquivo anonimizado e decupado (COMPLETO com contratos)
                arquivos = list(resultados_dir.glob("dados_anonimizados_decupado_*.csv"))
                if not arquivos:
                    # Fallback: tentar dados_com_duracao
                    arquivos = list(resultados_dir.glob("dados_com_duracao_*.csv"))
                
                if not arquivos:
                    print(f"⚠️ Nenhum dado encontrado em {resultados_dir}")
                    return False
                
                arquivo_mais_recente = str(max(arquivos))
                print(f"📁 Carregando: {arquivo_mais_recente}")
                self.df = pd.read_csv(arquivo_mais_recente, encoding='utf-8-sig', low_memory=False)
            
            # Calcular duração se não existir
            if 'duracao_horas' not in self.df.columns:
                print("⏱️ Calculando duração...")
                self.df['d_dt_inicio_apontamento'] = pd.to_datetime(
                    self.df['d_dt_inicio_apontamento'], errors='coerce'
                )
                self.df['d_dt_fim_apontamento'] = pd.to_datetime(
                    self.df['d_dt_fim_apontamento'], errors='coerce'
                )
                
                # Calcular duração em horas
                duracao = (self.df['d_dt_fim_apontamento'] - self.df['d_dt_inicio_apontamento'])
                self.df['duracao_horas'] = duracao.dt.total_seconds() / 3600
                
                # Remover valores inválidos
                self.df = self.df[self.df['duracao_horas'] > 0].copy()
            
            # Converter colunas de data
            if 'd_dt_data' in self.df.columns:
                self.df['data'] = pd.to_datetime(self.df['d_dt_data'], errors='coerce')
            
            self.ultima_atualizacao = datetime.now()
            print(f"✅ Dados carregados: {len(self.df)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def eh_dia_util(self, data: datetime) -> bool:
        """
        Verifica se uma data é dia útil (segunda a sexta, exceto feriados)
        
        Args:
            data: Data a verificar
        
        Returns:
            True se for dia útil, False se for fim de semana
        """
        # Verifica se é fim de semana (5=sábado, 6=domingo)
        if data.weekday() >= 5:
            return False
        
        # TODO: Adicionar verificação de feriados nacionais se necessário
        # Por enquanto, apenas verifica se não é fim de semana
        return True
    
    def aplicar_desconto_almoco(self, horas: float, eh_dia_util: bool = True) -> float:
        """
        Aplica desconto de 1 hora de almoço apenas em dias úteis
        
        Args:
            horas: Horas trabalhadas brutas
            eh_dia_util: Se True, aplica desconto de almoço
        
        Returns:
            Horas líquidas (com desconto de almoço se aplicável)
        """
        if eh_dia_util and horas > 0:
            return max(0, horas - 1.0)  # Desconta 1h, mas não permite negativo
        return horas
    
    def classificar_apontamento(self, data: datetime, horas: float) -> Dict:
        """
        Classifica um apontamento quanto a dia útil/fim de semana e aplica descontos
        
        Args:
            data: Data do apontamento
            horas: Horas trabalhadas brutas
        
        Returns:
            Dicionário com classificação e horas líquidas
        """
        dia_util = self.eh_dia_util(data)
        horas_liquidas = self.aplicar_desconto_almoco(horas, dia_util)
        
        return {
            "dia_util": dia_util,
            "tipo_dia": "📅 Dia Útil" if dia_util else "🏖️ Fim de Semana",
            "horas_brutas": horas,
            "horas_liquidas": horas_liquidas,
            "desconto_almoco": 1.0 if dia_util and horas > 0 else 0.0
        }
    
    def extrair_datas(self, texto: str) -> List[str]:
        """
        Extrai datas de um texto em formato DD/MM/YYYY ou DD/MM
        
        Args:
            texto: Texto para extrair datas
        
        Returns:
            Lista de datas encontradas (no formato DD/MM/YYYY)
        """
        import re
        datas = []
        
        # Padrão para DD/MM/YYYY, DD/MM/YY ou DD/MM
        padrao = r'(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)'
        matches = re.findall(padrao, texto)
        
        for match in matches:
            data = match.replace('-', '/')
            # Adicionar ano padrão 2025 se não tiver
            if data.count('/') == 1:  # DD/MM
                data += '/2025'
            elif len(data.split('/')[-1]) < 4:  # Ano incompleto
                data = '/'.join(data.split('/')[:-1]) + '/2025'
            datas.append(data)
        
        return datas
    
    def responder_pergunta(self, pergunta: str, usuario: Optional[str] = None) -> Dict:
        """
        Interpreta e responde perguntas sobre apontamentos
        
        Args:
            pergunta: Pergunta em linguagem natural
            usuario: Nome do usuário (opcional)
        
        Returns:
            Dicionário com resposta formatada
        """
        pergunta_lower = pergunta.lower()
        
        # Ignorar usuários genéricos do emulator
        if usuario and usuario.lower() in ['user', 'bot', 'test user', 'usuario teste']:
            usuario = None
        
        # Detectar consulta por período (ex: "10/10/2025 a 10/11/2025" ou "de 10/10 até 10/11")
        import re
        # Aceitar formatos: DD/MM/YYYY, DD/MM/YYY, DD/MM/YY, DD/MM (sem ano)
        padrao_periodo = r'(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)\s*(?:a|até|ate|at)\s*(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)'
        match_periodo = re.search(padrao_periodo, pergunta)
        
        if match_periodo:
            data_inicio = match_periodo.group(1).replace('-', '/')
            data_fim = match_periodo.group(2).replace('-', '/')
            
            # Adicionar ano padrão 2025 se não tiver ano
            if data_inicio.count('/') == 1:  # DD/MM
                data_inicio += '/2025'
            elif len(data_inicio.split('/')[-1]) < 4:  # Ano incompleto
                data_inicio = '/'.join(data_inicio.split('/')[:-1]) + '/2025'
                
            if data_fim.count('/') == 1:  # DD/MM
                data_fim += '/2025'
            elif len(data_fim.split('/')[-1]) < 4:  # Ano incompleto
                data_fim = '/'.join(data_fim.split('/')[:-1]) + '/2025'
            
            # Se a pergunta menciona "deveria fazer" ou "horas esperadas", chamar análise detalhada
            if any(palavra in pergunta_lower for palavra in ['deveria fazer', 'deveria ter', 'esperadas', 'quantas horas o colaborador']):
                # Extrair nome do colaborador da pergunta
                if usuario and usuario not in ['Usuário Web', 'User']:
                    return self.horas_esperadas_colaborador(usuario, data_inicio, data_fim)
                else:
                    # Tentar extrair nome da pergunta
                    # Padrão: "colaborador NOME deveria" ou "NOME deveria"
                    match_nome = re.search(r'colaborador\s+(\w+)', pergunta_lower)
                    if not match_nome:
                        match_nome = re.search(r'(\w+)\s+deveria', pergunta_lower)
                    
                    if match_nome:
                        nome_colaborador = match_nome.group(1)
                        return self.horas_esperadas_colaborador(nome_colaborador, data_inicio, data_fim)
                    else:
                        return {
                            "resposta": "❌ Por favor, especifique o nome do colaborador. Exemplo: 'Quantas horas o colaborador João deveria fazer de 01/09 a 30/09?'",
                            "tipo": "erro"
                        }
            
            # Se a pergunta menciona "contrato", redirecionar para listar_contratos
            if 'contrato' in pergunta_lower:
                return self.listar_contratos(inicio=data_inicio, fim=data_fim)
            
            # Se a pergunta menciona "quem", "quais", "recursos", "ranking", "top", "média" (sem "meu/minha"), buscar TODOS
            buscar_todos = any(palavra in pergunta_lower for palavra in ['quem', 'quais', 'recursos', 'pessoas', 'ranking', 'top'])
            buscar_todos = buscar_todos or ('média' in pergunta_lower and not any(p in pergunta_lower for p in ['meu', 'minha', 'mim']))
            buscar_todos = buscar_todos or ('media' in pergunta_lower and not any(p in pergunta_lower for p in ['meu', 'minha', 'mim']))
            
            # Sempre buscar todos se for consulta geral de período (não específica do usuário)
            if buscar_todos or usuario in ['Usuário Web', 'User', None]:
                return self.consultar_periodo(data_inicio, data_fim, None)
            else:
                return self.consultar_periodo(data_inicio, data_fim, usuario)
        
        # Mapeamento de perguntas para funções
        if any(palavra in pergunta_lower for palavra in ['média', 'media', 'quanto tempo']):
            # Se a pergunta menciona um nome específico, buscar por ele
            if usuario and any(palavra in pergunta_lower for palavra in ['meu', 'minha', 'mim']):
                return self.duracao_media_usuario(usuario)
            else:
                return self.duracao_media_geral()
        
        elif any(palavra in pergunta_lower for palavra in ['hoje', 'apontei hoje']):
            if usuario:
                return self.apontamentos_hoje(usuario)
            else:
                return {"resposta": "Por favor, identifique-se para consultar seus apontamentos."}
        
        elif any(palavra in pergunta_lower for palavra in ['semana', 'esta semana']):
            if usuario:
                return self.resumo_semanal(usuario)
            else:
                return self.resumo_semanal_geral()
        
        elif any(palavra in pergunta_lower for palavra in ['ranking', 'top', 'quem trabalhou mais']):
            return self.ranking_funcionarios()
        
        elif any(palavra in pergunta_lower for palavra in ['outlier', 'anormal', 'fora do padrão']):
            return self.identificar_outliers()
        
        elif any(palavra in pergunta_lower for palavra in ['total', 'soma', 'quantas horas']):
            if usuario:
                return self.total_horas_usuario(usuario)
            else:
                return self.total_horas_geral()
        
        elif any(palavra in pergunta_lower for palavra in ['comparar', 'comparação']):
            return self.comparar_periodos()
        
        elif any(palavra in pergunta_lower for palavra in ['contrato', 'contratos']):
            # Verificar se tem período especificado
            datas = self.extrair_datas(pergunta)
            if datas and len(datas) >= 2:
                return self.listar_contratos(inicio=datas[0], fim=datas[1])
            else:
                return self.listar_contratos()
        
        elif any(palavra in pergunta_lower for palavra in ['esqueceu', 'esqueci', 'saída', 'saida', 'bateu a saída', 'bateu saida', 'faltou', 'horário de saída']):
            # Detectar verificação de saídas esquecidas
            # Extrair nome do colaborador e período (se houver)
            datas = self.extrair_datas(pergunta)
            
            # Determinar usuário
            if usuario and usuario not in ['Usuário Web', 'User']:
                nome_usuario = usuario
            else:
                # Tentar extrair nome da pergunta
                import re
                match_nome = re.search(r'(?:recurso|colaborador|usuário|usuario)\s+(\w+)', pergunta_lower)
                if not match_nome:
                    # Procurar por RECURSO_ seguido de números
                    match_nome = re.search(r'(RECURSO_\d+)', pergunta, re.IGNORECASE)
                
                if match_nome:
                    nome_usuario = match_nome.group(1)
                else:
                    return {
                        "resposta": "❌ Por favor, especifique o nome do colaborador. Exemplo: 'O recurso RECURSO_123 esqueceu de informar horário de saída?'",
                        "tipo": "erro"
                    }
            
            # Chamar função de verificação
            if len(datas) >= 2:
                return self.verificar_saidas_esquecidas(nome_usuario, datas[0], datas[1])
            elif len(datas) == 1:
                return self.verificar_saidas_esquecidas(nome_usuario, data_inicio=datas[0])
            else:
                return self.verificar_saidas_esquecidas(nome_usuario)
        
        else:
            # Resposta padrão para perguntas fora do contexto
            if any(palavra in pergunta_lower for palavra in ['tempo', 'clima', 'ajuda', 'help', 'prompt']):
                return {
                    "resposta": "🤖 Olá! Sou especializado em **apontamentos de horas**.\n\n" +
                               "Posso ajudar você com:\n" +
                               "• 📊 Estatísticas e médias de horas\n" +
                               "• 📅 Consultas por período\n" +
                               "• 🏆 Rankings de produtividade\n" +
                               "• 📝 Detalhamento de apontamentos\n\n" +
                               "💡 **Exemplos:**\n" +
                               "• \"Qual a média de horas no período de 01/09/2025 a 30/09/2025?\"\n" +
                               "• \"Quem apontou entre 10/10/2025 e 20/10/2025?\"\n" +
                               "• \"Mostre o ranking de horas\"\n\n" +
                               "Como posso ajudar você com apontamentos? 😊",
                    "tipo": "info"
                }
            else:
                return self.ajuda()
    
    def duracao_media_geral(self) -> Dict:
        """Retorna duração média geral"""
        if self.df is None or 'duracao_horas' not in self.df.columns:
            return {"erro": "Dados não disponíveis"}
        
        media = self.df['duracao_horas'].mean()
        mediana = self.df['duracao_horas'].median()
        
        horas = int(media)
        minutos = int((media - horas) * 60)
        
        return {
            "resposta": f"📊 A duração média de trabalho é de **{horas}h{minutos:02d}min** ({media:.2f} horas)",
            "dados": {
                "media_horas": round(media, 2),
                "mediana_horas": round(mediana, 2),
                "formatado": f"{horas}h{minutos:02d}min"
            },
            "tipo": "estatistica_geral"
        }
    
    def duracao_media_usuario(self, usuario: str) -> Dict:
        """Retorna duração média de um usuário específico"""
        if self.df is None:
            return {"erro": "Dados não disponíveis"}
        
        # Buscar por nome
        df_usuario = self.df[self.df['s_nm_recurso'].str.contains(usuario, case=False, na=False)]
        
        if len(df_usuario) == 0:
            return {
                "resposta": f"❌ Usuário '{usuario}' não encontrado nos registros.",
                "tipo": "erro"
            }
        
        media = df_usuario['duracao_horas'].mean()
        total_apontamentos = len(df_usuario)
        
        horas = int(media)
        minutos = int((media - horas) * 60)
        
        # Comparar com média geral
        media_geral = self.df['duracao_horas'].mean()
        diferenca = media - media_geral
        comparacao = "acima" if diferenca > 0 else "abaixo"
        
        return {
            "resposta": f"👤 **{usuario}**\n" + 
                       f"📊 Duração média: **{horas}h{minutos:02d}min**\n" +
                       f"📋 Total de apontamentos: {total_apontamentos}\n" +
                       f"📈 {abs(diferenca):.2f}h {comparacao} da média geral",
            "dados": {
                "usuario": usuario,
                "media_horas": round(media, 2),
                "total_apontamentos": total_apontamentos,
                "diferenca_media_geral": round(diferenca, 2)
            },
            "tipo": "usuario_individual"
        }
    
    def apontamentos_hoje(self, usuario: str) -> Dict:
        """Retorna apontamentos do dia com informação de dia útil e desconto de almoço"""
        if self.df is None or 'data' not in self.df.columns:
            return {"erro": "Dados não disponíveis"}
        
        hoje = pd.Timestamp.now()
        hoje_date = hoje.date()
        df_hoje = self.df[
            (self.df['data'].dt.date == hoje_date) & 
            (self.df['s_nm_recurso'].str.contains(usuario, case=False, na=False))
        ]
        
        if len(df_hoje) == 0:
            return {
                "resposta": f"📅 Você ainda não tem apontamentos registrados para hoje ({hoje_date}).",
                "tipo": "info"
            }
        
        # Classificar o dia
        total_horas = df_hoje['duracao_horas'].sum()
        classificacao = self.classificar_apontamento(hoje, total_horas)
        
        horas_brutas = int(total_horas)
        minutos_brutos = int((total_horas - horas_brutas) * 60)
        
        horas_liquidas = classificacao['horas_liquidas']
        horas_liq = int(horas_liquidas)
        minutos_liq = int((horas_liquidas - horas_liq) * 60)
        
        apontamentos = []
        for _, row in df_hoje.iterrows():
            apontamentos.append({
                "operacao": row.get('s_ds_operacao', 'N/A'),
                "duracao": row.get('duracao_horas', 0)
            })
        
        resposta = f"📅 **Hoje ({hoje_date})** - {classificacao['tipo_dia']}\n" + \
                   f"⏱️ **Horas Brutas:** {horas_brutas}h{minutos_brutos:02d}min\n"
        
        if classificacao['desconto_almoco'] > 0:
            resposta += f"🍽️ **Desconto Almoço:** {classificacao['desconto_almoco']:.1f}h\n" + \
                       f"✅ **Horas Líquidas:** {horas_liq}h{minutos_liq:02d}min\n"
        
        resposta += f"📝 **Número de apontamentos:** {len(df_hoje)}"
        
        return {
            "resposta": resposta,
            "dados": {
                "data": str(hoje_date),
                "total_horas_brutas": round(total_horas, 2),
                "total_horas_liquidas": round(horas_liquidas, 2),
                "desconto_almoco": classificacao['desconto_almoco'],
                "dia_util": classificacao['dia_util'],
                "tipo_dia": classificacao['tipo_dia'],
                "quantidade": len(df_hoje),
                "apontamentos": apontamentos
            },
            "tipo": "dia_atual"
        }
    
    def resumo_semanal(self, usuario: str) -> Dict:
        """Retorna resumo da semana para um usuário com detalhamento de dias úteis"""
        if self.df is None or 'data' not in self.df.columns:
            return {"erro": "Dados não disponíveis"}
        
        hoje = pd.Timestamp.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        df_semana = self.df[
            (self.df['data'] >= inicio_semana) &
            (self.df['s_nm_recurso'].str.contains(usuario, case=False, na=False))
        ]
        
        if len(df_semana) == 0:
            return {
                "resposta": f"📅 Sem apontamentos esta semana para {usuario}",
                "tipo": "info"
            }
        
        # Calcular horas brutas
        total_horas_brutas = df_semana['duracao_horas'].sum()
        
        # Agrupar por dia e calcular horas líquidas considerando dias úteis
        total_horas_liquidas = 0
        dias_uteis_trabalhados = 0
        dias_fim_semana_trabalhados = 0
        total_desconto_almoco = 0
        
        for data, grupo in df_semana.groupby(df_semana['data'].dt.date):
            horas_dia = grupo['duracao_horas'].sum()
            data_dt = pd.Timestamp(data)
            classificacao = self.classificar_apontamento(data_dt, horas_dia)
            
            total_horas_liquidas += classificacao['horas_liquidas']
            total_desconto_almoco += classificacao['desconto_almoco']
            
            if classificacao['dia_util']:
                dias_uteis_trabalhados += 1
            else:
                dias_fim_semana_trabalhados += 1
        
        media_diaria_bruta = df_semana.groupby(df_semana['data'].dt.date)['duracao_horas'].sum().mean()
        media_diaria_liquida = total_horas_liquidas / (dias_uteis_trabalhados + dias_fim_semana_trabalhados) if (dias_uteis_trabalhados + dias_fim_semana_trabalhados) > 0 else 0
        
        resposta = f"📅 **Resumo Semanal - {usuario}**\n\n" + \
                   f"⏱️ **Horas Brutas:** {total_horas_brutas:.2f}h\n" + \
                   f"🍽️ **Desconto Almoço:** {total_desconto_almoco:.1f}h\n" + \
                   f"✅ **Horas Líquidas:** {total_horas_liquidas:.2f}h\n\n" + \
                   f"📊 **Média Diária Bruta:** {media_diaria_bruta:.2f}h\n" + \
                   f"📊 **Média Diária Líquida:** {media_diaria_liquida:.2f}h\n\n" + \
                   f"📝 **Apontamentos:** {len(df_semana)}\n" + \
                   f"📅 **Dias Úteis:** {dias_uteis_trabalhados}\n" + \
                   f"🏖️ **Fins de Semana:** {dias_fim_semana_trabalhados}"
        
        return {
            "resposta": resposta,
            "dados": {
                "total_horas_brutas": round(total_horas_brutas, 2),
                "total_horas_liquidas": round(total_horas_liquidas, 2),
                "desconto_almoco": round(total_desconto_almoco, 2),
                "media_diaria_bruta": round(media_diaria_bruta, 2),
                "media_diaria_liquida": round(media_diaria_liquida, 2),
                "quantidade": len(df_semana),
                "dias_uteis": dias_uteis_trabalhados,
                "dias_fim_semana": dias_fim_semana_trabalhados
            },
            "tipo": "resumo_semanal"
        }
    
    def resumo_semanal_geral(self) -> Dict:
        """Resumo semanal de todos"""
        hoje = pd.Timestamp.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        df_semana = self.df[self.df['data'] >= inicio_semana]
        total = df_semana['duracao_horas'].sum()
        
        return {
            "resposta": f"📊 Total apontado esta semana: **{total:.2f} horas**",
            "tipo": "estatistica"
        }
    
    def ranking_funcionarios(self, top_n: int = 10) -> Dict:
        """Ranking de funcionários por horas trabalhadas"""
        if self.df is None:
            return {"erro": "Dados não disponíveis"}
        
        ranking = self.df.groupby('s_nm_recurso')['duracao_horas'].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False).head(top_n)
        
        resposta = f"🏆 **Top {top_n} - Horas Trabalhadas**\n\n"
        for i, (nome, row) in enumerate(ranking.iterrows(), 1):
            resposta += f"{i}. {nome}: {row['sum']:.2f}h ({int(row['count'])} apontamentos)\n"
        
        return {
            "resposta": resposta,
            "dados": ranking.to_dict('index'),
            "tipo": "ranking"
        }
    
    def identificar_outliers(self) -> Dict:
        """Identifica outliers recentes"""
        if self.df is None:
            return {"erro": "Dados não disponíveis"}
        
        # Calcular z-score
        media = self.df['duracao_horas'].mean()
        std = self.df['duracao_horas'].std()
        self.df['z_score'] = (self.df['duracao_horas'] - media) / std
        
        outliers = self.df[abs(self.df['z_score']) > 2].sort_values('duracao_horas', ascending=False).head(5)
        
        if len(outliers) == 0:
            return {
                "resposta": "✅ Nenhum outlier detectado recentemente!",
                "tipo": "info"
            }
        
        resposta = "⚠️ **Apontamentos Fora do Padrão:**\n\n"
        for _, row in outliers.iterrows():
            resposta += f"• {row['s_nm_recurso']}: {row['duracao_horas']:.2f}h (Z-Score: {row['z_score']:.2f})\n"
        
        return {
            "resposta": resposta,
            "dados": outliers.to_dict('records'),
            "tipo": "outliers"
        }
    
    def total_horas_usuario(self, usuario: str) -> Dict:
        """Total de horas de um usuário"""
        if self.df is None:
            return {"erro": "Dados não disponíveis", "tipo": "erro"}
        
        df_usuario = self.df[self.df['s_nm_recurso'].str.contains(usuario, case=False, na=False)]
        total = df_usuario['duracao_horas'].sum()
        
        return {
            "resposta": f"⏱️ **{usuario}** - Total: **{total:.2f} horas**",
            "dados": {"total_horas": round(total, 2)},
            "tipo": "total"
        }
    
    def total_horas_geral(self) -> Dict:
        """Total geral de horas"""
        if self.df is None:
            return {"erro": "Dados não disponíveis", "tipo": "erro"}
        
        total = self.df['duracao_horas'].sum()
        return {
            "resposta": f"📊 Total geral: **{total:.2f} horas**",
            "tipo": "total_geral"
        }
    
    def consultar_periodo(self, data_inicio: str, data_fim: str, usuario: Optional[str] = None) -> Dict:
        """
        Consulta dados de um período específico com cálculo de dias úteis e desconto de almoço
        
        Args:
            data_inicio: Data inicial (formato: YYYY-MM-DD ou DD/MM/YYYY)
            data_fim: Data final (formato: YYYY-MM-DD ou DD/MM/YYYY)
            usuario: Nome do usuário (opcional, consulta geral se None)
        
        Returns:
            Dicionário com estatísticas do período incluindo horas brutas e líquidas
        """
        if self.df is None or 'data' not in self.df.columns:
            return {"erro": "Dados não disponíveis", "tipo": "erro"}
        
        try:
            # Converter strings para datetime (aceita múltiplos formatos)
            inicio = pd.to_datetime(data_inicio, dayfirst=True)
            fim = pd.to_datetime(data_fim, dayfirst=True)
            
            # Filtrar por período
            df_periodo = self.df[(self.df['data'] >= inicio) & (self.df['data'] <= fim)]
            
            # Filtrar por usuário se especificado
            if usuario:
                df_periodo = df_periodo[df_periodo['s_nm_recurso'].str.contains(usuario, case=False, na=False)]
            
            if len(df_periodo) == 0:
                msg = f"📅 Nenhum apontamento encontrado entre {inicio.date()} e {fim.date()}"
                if usuario:
                    msg += f" para {usuario}"
                return {
                    "resposta": msg,
                    "tipo": "info"
                }
            
            # Calcular estatísticas brutas
            total_horas_brutas = df_periodo['duracao_horas'].sum()
            media_horas_brutas = df_periodo['duracao_horas'].mean()
            quantidade = len(df_periodo)
            
            # Calcular número de dias corridos no período
            dias_corridos = (fim - inicio).days + 1
            
            # Calcular horas líquidas considerando dias úteis e desconto de almoço
            total_horas_liquidas = 0
            dias_uteis_trabalhados = 0
            dias_fim_semana_trabalhados = 0
            total_desconto_almoco = 0
            
            for data, grupo in df_periodo.groupby(df_periodo['data'].dt.date):
                horas_dia = grupo['duracao_horas'].sum()
                data_dt = pd.Timestamp(data)
                classificacao = self.classificar_apontamento(data_dt, horas_dia)
                
                total_horas_liquidas += classificacao['horas_liquidas']
                total_desconto_almoco += classificacao['desconto_almoco']
                
                if classificacao['dia_util']:
                    dias_uteis_trabalhados += 1
                else:
                    dias_fim_semana_trabalhados += 1
            
            dias_trabalhados_total = dias_uteis_trabalhados + dias_fim_semana_trabalhados
            
            # Média por dia CORRIDO do período (não por apontamento individual)
            media_horas_brutas_dia = total_horas_brutas / dias_corridos if dias_corridos > 0 else 0
            media_horas_liquidas_dia = total_horas_liquidas / dias_corridos if dias_corridos > 0 else 0
            
            # Número de recursos únicos no período
            num_recursos = df_periodo['s_nm_recurso'].nunique() if not usuario else 1
            
            # Ranking no período
            top_usuarios = df_periodo.groupby('s_nm_recurso')['duracao_horas'].sum().nlargest(5)
            
            resposta = f"📅 **Período: {inicio.date()} a {fim.date()}**\n\n"
            if usuario:
                resposta += f"👤 Usuário: **{usuario}**\n\n"
            else:
                resposta += f"👥 **Recursos Únicos:** {num_recursos} pessoas\n\n"
            
            # Calcular médias por pessoa
            media_horas_por_pessoa = total_horas_brutas / num_recursos if num_recursos > 0 else 0
            media_horas_pessoa_dia_util = media_horas_por_pessoa / dias_uteis_trabalhados if dias_uteis_trabalhados > 0 else 0
            
            resposta += f"⏱️ **Total de Horas (soma geral):** {total_horas_brutas:.2f}h\n" + \
                       f"📊 **Média por Pessoa no Período:** {media_horas_por_pessoa:.2f}h/pessoa\n" + \
                       f"📈 **Média por Pessoa/Dia Útil:** {media_horas_pessoa_dia_util:.2f}h/pessoa/dia\n\n" + \
                       f"📝 **Total de Apontamentos:** {quantidade}\n" + \
                       f"📅 **Dias com Registro:** {dias_trabalhados_total} (úteis: {dias_uteis_trabalhados}, FDS: {dias_fim_semana_trabalhados})\n" + \
                       f"📆 **Dias Corridos:** {dias_corridos}"
            
            if not usuario:
                resposta += f"\n\n🏆 **Top 5 no período:**\n"
                for i, (nome, horas) in enumerate(top_usuarios.items(), 1):
                    resposta += f"{i}. {nome}: {horas:.2f}h\n"
            
            return {
                "resposta": resposta,
                "dados": {
                    "data_inicio": str(inicio.date()),
                    "data_fim": str(fim.date()),
                    "total_horas_brutas": round(total_horas_brutas, 2),
                    "total_horas_liquidas": round(total_horas_liquidas, 2),
                    "desconto_almoco": round(total_desconto_almoco, 2),
                    "media_horas_brutas_dia": round(media_horas_brutas_dia, 2),
                    "media_horas_liquidas_dia": round(media_horas_liquidas_dia, 2),
                    "media_por_apontamento": round(media_horas_brutas, 2),
                    "quantidade": quantidade,
                    "dias_uteis": dias_uteis_trabalhados,
                    "dias_fim_semana": dias_fim_semana_trabalhados,
                    "dias_trabalhados": dias_trabalhados_total,
                    "dias_corridos": dias_corridos,
                    "top_usuarios": top_usuarios.to_dict() if not usuario else {}
                },
                "tipo": "periodo"
            }
            
        except Exception as e:
            return {
                "resposta": f"❌ Erro ao processar datas: {str(e)}\n💡 Use formato DD/MM/YYYY ou YYYY-MM-DD",
                "tipo": "erro"
            }
    
    def detalhar_apontamentos_por_dia(self, data_inicio: str, data_fim: str, usuario: Optional[str] = None) -> Dict:
        """
        Detalha apontamentos dia a dia no período especificado
        
        Args:
            data_inicio: Data inicial (formato: YYYY-MM-DD ou DD/MM/YYYY)
            data_fim: Data final (formato: YYYY-MM-DD ou DD/MM/YYYY)
            usuario: Nome do usuário (opcional, consulta geral se None)
        
        Returns:
            Dicionário com detalhamento dia a dia dos apontamentos
        """
        if self.df is None or 'data' not in self.df.columns:
            return {"erro": "Dados não disponíveis", "tipo": "erro"}
        
        try:
            # Converter strings para datetime
            inicio = pd.to_datetime(data_inicio, dayfirst=True)
            fim = pd.to_datetime(data_fim, dayfirst=True)
            
            # Filtrar por período
            df_periodo = self.df[(self.df['data'] >= inicio) & (self.df['data'] <= fim)]
            
            # Filtrar por usuário se especificado
            if usuario:
                df_periodo = df_periodo[df_periodo['s_nm_recurso'].str.contains(usuario, case=False, na=False)]
            
            if len(df_periodo) == 0:
                msg = f"📅 Nenhum apontamento encontrado entre {inicio.date()} e {fim.date()}"
                if usuario:
                    msg += f" para {usuario}"
                return {"resposta": msg, "tipo": "info"}
            
            # Agrupar por dia
            agrupado_por_dia = df_periodo.groupby(df_periodo['data'].dt.date).agg({
                'duracao_horas': 'sum',
                's_id_apontamento': 'count',
                's_ds_cargo': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A'
            }).sort_index()
            
            resposta = f"📅 **Apontamentos por Dia - {inicio.date()} a {fim.date()}**\n"
            if usuario:
                resposta += f"👤 Recurso: **{usuario}**\n"
            resposta += f"\n📊 **Total: {len(agrupado_por_dia)} dias com apontamentos**\n\n"
            
            # Listar cada dia
            for data, row in agrupado_por_dia.iterrows():
                data_dt = pd.Timestamp(data)
                dia_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'][data_dt.weekday()]
                emoji_dia = '📅' if data_dt.weekday() < 5 else '🏖️'
                
                resposta += f"{emoji_dia} **{data.strftime('%d/%m/%Y')} ({dia_semana})**\n"
                resposta += f"   ⏱️ {row['duracao_horas']:.2f}h | "
                resposta += f"📝 {int(row['s_id_apontamento'])} apontamentos\n"
            
            # Converter chaves datetime.date para string antes de retornar
            dados_serializavel = {str(data): valores for data, valores in agrupado_por_dia.to_dict('index').items()}
            
            return {
                "resposta": resposta,
                "dados": dados_serializavel,
                "tipo": "detalhamento_diario"
            }
            
        except Exception as e:
            return {
                "resposta": f"❌ Erro ao processar datas: {str(e)}\n💡 Use formato DD/MM/YYYY ou YYYY-MM-DD",
                "tipo": "erro"
            }
    
    def comparar_periodos(self) -> Dict:
        """Compara semana atual com anterior"""
        hoje = pd.Timestamp.now()
        inicio_semana_atual = hoje - timedelta(days=hoje.weekday())
        inicio_semana_anterior = inicio_semana_atual - timedelta(days=7)
        
        df_atual = self.df[(self.df['data'] >= inicio_semana_atual)]
        df_anterior = self.df[(self.df['data'] >= inicio_semana_anterior) & (self.df['data'] < inicio_semana_atual)]
        
        total_atual = df_atual['duracao_horas'].sum()
        total_anterior = df_anterior['duracao_horas'].sum()
        diferenca = total_atual - total_anterior
        
        return {
            "resposta": f"📊 **Comparação Semanal**\n" +
                       f"Esta semana: {total_atual:.2f}h\n" +
                       f"Semana passada: {total_anterior:.2f}h\n" +
                       f"Diferença: {diferenca:+.2f}h",
            "dados": {
                "total_atual": round(total_atual, 2),
                "total_anterior": round(total_anterior, 2),
                "diferenca": round(diferenca, 2),
                "atual": round(total_atual, 2),
                "anterior": round(total_anterior, 2)
            },
            "tipo": "comparacao"
        }
    
    def contar_dias_uteis_periodo(self, data_inicio: str, data_fim: str) -> Dict:
        """
        Conta quantos dias úteis existem em um período
        
        Args:
            data_inicio: Data inicial (formato: YYYY-MM-DD ou DD/MM/YYYY)
            data_fim: Data final (formato: YYYY-MM-DD ou DD/MM/YYYY)
        
        Returns:
            Dicionário com contagem de dias úteis e detalhes
        """
        try:
            # Converter strings para datetime
            inicio = pd.to_datetime(data_inicio, dayfirst=True)
            fim = pd.to_datetime(data_fim, dayfirst=True)
            
            # Contar dias úteis
            dias_uteis = 0
            dias_fim_semana = 0
            data_atual = inicio
            
            lista_dias_uteis = []
            lista_fins_semana = []
            
            while data_atual <= fim:
                if self.eh_dia_util(data_atual):
                    dias_uteis += 1
                    lista_dias_uteis.append(data_atual.strftime('%d/%m/%Y'))
                else:
                    dias_fim_semana += 1
                    lista_fins_semana.append(data_atual.strftime('%d/%m/%Y'))
                data_atual += timedelta(days=1)
            
            total_dias = dias_uteis + dias_fim_semana
            
            resposta = f"📅 **Período: {inicio.date()} a {fim.date()}**\n\n" + \
                       f"📊 **Dias Úteis:** {dias_uteis} dias\n" + \
                       f"🏖️ **Fins de Semana:** {dias_fim_semana} dias\n" + \
                       f"📆 **Total de Dias:** {total_dias} dias"
            
            return {
                "resposta": resposta,
                "dados": {
                    "data_inicio": str(inicio.date()),
                    "data_fim": str(fim.date()),
                    "dias_uteis": dias_uteis,
                    "dias_fim_semana": dias_fim_semana,
                    "total_dias": total_dias,
                    "lista_dias_uteis": lista_dias_uteis,
                    "lista_fins_semana": lista_fins_semana
                },
                "tipo": "contagem_dias_uteis"
            }
            
        except Exception as e:
            return {
                "resposta": f"❌ Erro ao processar datas: {str(e)}\n💡 Use formato DD/MM/YYYY ou YYYY-MM-DD",
                "tipo": "erro"
            }
    
    def calcular_horas_esperadas_periodo(self, data_inicio: str, data_fim: str, horas_por_dia: float = 8.0) -> Dict:
        """
        Calcula quantas horas um colaborador deveria fazer em um período
        
        Args:
            data_inicio: Data inicial (formato: YYYY-MM-DD ou DD/MM/YYYY)
            data_fim: Data final (formato: YYYY-MM-DD ou DD/MM/YYYY)
            horas_por_dia: Horas esperadas por dia útil (padrão: 8h)
        
        Returns:
            Dicionário com cálculo de horas esperadas
        """
        # Primeiro contar dias úteis
        resultado_dias = self.contar_dias_uteis_periodo(data_inicio, data_fim)
        
        if resultado_dias.get('tipo') == 'erro':
            return resultado_dias
        
        dias_uteis = resultado_dias['dados']['dias_uteis']
        horas_esperadas_brutas = dias_uteis * horas_por_dia
        horas_almoco = dias_uteis * 1.0  # 1h de almoço por dia útil
        horas_esperadas_liquidas = horas_esperadas_brutas - horas_almoco
        
        inicio = resultado_dias['dados']['data_inicio']
        fim = resultado_dias['dados']['data_fim']
        
        resposta = f"📅 **Período: {inicio} a {fim}**\n\n" + \
                   f"📊 **Dias Úteis:** {dias_uteis} dias\n" + \
                   f"⏱️ **Horas por Dia:** {horas_por_dia:.1f}h\n\n" + \
                   f"📈 **Horas Esperadas (Brutas):** {horas_esperadas_brutas:.1f}h\n" + \
                   f"🍽️ **Desconto Almoço:** {horas_almoco:.1f}h\n" + \
                   f"✅ **Horas Esperadas (Líquidas):** {horas_esperadas_liquidas:.1f}h"
        
        return {
            "resposta": resposta,
            "dados": {
                "data_inicio": inicio,
                "data_fim": fim,
                "dias_uteis": dias_uteis,
                "horas_por_dia": horas_por_dia,
                "horas_esperadas_brutas": round(horas_esperadas_brutas, 1),
                "horas_almoco": round(horas_almoco, 1),
                "horas_esperadas_liquidas": round(horas_esperadas_liquidas, 1)
            },
            "tipo": "horas_esperadas"
        }
    
    def dias_nao_apontados(self, data_inicio: str, data_fim: str, usuario: Optional[str] = None) -> Dict:
        """
        Identifica quais dias úteis não tiveram apontamentos
        
        Args:
            data_inicio: Data inicial (formato: YYYY-MM-DD ou DD/MM/YYYY)
            data_fim: Data final (formato: YYYY-MM-DD ou DD/MM/YYYY)
            usuario: Nome do usuário (opcional)
        
        Returns:
            Dicionário com lista de dias não apontados
        """
        if self.df is None or 'data' not in self.df.columns:
            return {"erro": "Dados não disponíveis", "tipo": "erro"}
        
        try:
            # Converter strings para datetime
            inicio = pd.to_datetime(data_inicio, dayfirst=True)
            fim = pd.to_datetime(data_fim, dayfirst=True)
            
            # Filtrar por período
            df_periodo = self.df[(self.df['data'] >= inicio) & (self.df['data'] <= fim)]
            
            # Se não especificar usuário, analisar todos
            if not usuario:
                # Pegar todos os usuários únicos do período
                usuarios = df_periodo['s_nm_recurso'].unique()
                
                if len(usuarios) == 0:
                    return {
                        "resposta": f"❌ Nenhum usuário encontrado no período {inicio.date()} a {fim.date()}",
                        "tipo": "info"
                    }
                
                # Analisar cada usuário
                resultado_usuarios = {}
                for usr in usuarios:
                    resultado_usuarios[usr] = self._analisar_dias_nao_apontados_usuario(inicio, fim, usr, df_periodo)
                
                # Montar resposta consolidada
                resposta = f"📅 **Período: {inicio.date()} a {fim.date()}**\n\n"
                resposta += f"👥 **Análise de {len(usuarios)} colaboradores**\n\n"
                
                usuarios_com_faltas = {usr: dados for usr, dados in resultado_usuarios.items() if dados['dias_nao_apontados'] > 0}
                
                if len(usuarios_com_faltas) == 0:
                    resposta += "✅ **Todos os colaboradores apontaram em todos os dias úteis!**"
                else:
                    resposta += f"⚠️ **{len(usuarios_com_faltas)} colaborador(es) com dias não apontados:**\n\n"
                    for usr, dados in sorted(usuarios_com_faltas.items(), key=lambda x: x[1]['dias_nao_apontados'], reverse=True)[:10]:
                        resposta += f"• **{usr}**: {dados['dias_nao_apontados']} dia(s) não apontado(s)\n"
                        if dados['lista_dias_faltantes']:
                            resposta += f"  Dias: {', '.join(dados['lista_dias_faltantes'][:5])}"
                            if len(dados['lista_dias_faltantes']) > 5:
                                resposta += f" ... (+{len(dados['lista_dias_faltantes'])-5})"
                            resposta += "\n"
                
                return {
                    "resposta": resposta,
                    "dados": {
                        "data_inicio": str(inicio.date()),
                        "data_fim": str(fim.date()),
                        "total_usuarios": len(usuarios),
                        "usuarios_com_faltas": len(usuarios_com_faltas),
                        "detalhes": resultado_usuarios
                    },
                    "tipo": "dias_nao_apontados_geral"
                }
            
            else:
                # Análise individual
                df_usuario = df_periodo[df_periodo['s_nm_recurso'].str.contains(usuario, case=False, na=False)]
                
                if len(df_usuario) == 0:
                    return {
                        "resposta": f"❌ Usuário '{usuario}' não encontrado no período {inicio.date()} a {fim.date()}",
                        "tipo": "erro"
                    }
                
                resultado = self._analisar_dias_nao_apontados_usuario(inicio, fim, usuario, df_periodo)
                
                resposta = f"📅 **Período: {inicio.date()} a {fim.date()}**\n" + \
                           f"👤 **Colaborador: {usuario}**\n\n" + \
                           f"📊 **Dias Úteis no Período:** {resultado['dias_uteis_total']}\n" + \
                           f"✅ **Dias Apontados:** {resultado['dias_apontados']}\n" + \
                           f"❌ **Dias Não Apontados:** {resultado['dias_nao_apontados']}\n"
                
                if resultado['dias_nao_apontados'] > 0:
                    resposta += f"\n⚠️ **Dias sem apontamento:**\n"
                    for dia in resultado['lista_dias_faltantes']:
                        resposta += f"• {dia}\n"
                else:
                    resposta += "\n🎉 **Parabéns! Todos os dias úteis foram apontados!**"
                
                return {
                    "resposta": resposta,
                    "dados": {
                        "data_inicio": str(inicio.date()),
                        "data_fim": str(fim.date()),
                        "usuario": usuario,
                        **resultado
                    },
                    "tipo": "dias_nao_apontados_individual"
                }
                
        except Exception as e:
            return {
                "resposta": f"❌ Erro ao processar: {str(e)}",
                "tipo": "erro"
            }
    
    def _analisar_dias_nao_apontados_usuario(self, inicio: pd.Timestamp, fim: pd.Timestamp, usuario: str, df_periodo: pd.DataFrame) -> Dict:
        """Função auxiliar para analisar dias não apontados de um usuário"""
        # Filtrar dados do usuário
        df_usuario = df_periodo[df_periodo['s_nm_recurso'].str.contains(usuario, case=False, na=False)]
        
        # Pegar datas que o usuário apontou
        datas_apontadas = set(df_usuario['data'].dt.date)
        
        # Listar todos os dias úteis do período
        dias_uteis_periodo = []
        data_atual = inicio
        while data_atual <= fim:
            if self.eh_dia_util(data_atual):
                dias_uteis_periodo.append(data_atual.date())
            data_atual += timedelta(days=1)
        
        # Identificar dias não apontados
        dias_nao_apontados = [dia for dia in dias_uteis_periodo if dia not in datas_apontadas]
        
        return {
            "dias_uteis_total": len(dias_uteis_periodo),
            "dias_apontados": len(datas_apontadas.intersection(set(dias_uteis_periodo))),
            "dias_nao_apontados": len(dias_nao_apontados),
            "lista_dias_faltantes": [dia.strftime('%d/%m/%Y') for dia in sorted(dias_nao_apontados)]
        }
    
    def listar_contratos(self, inicio: str = None, fim: str = None) -> Dict:
        """Lista todos os contratos com apontamentos, opcionalmente filtrado por período"""
        if self.df is None or 's_nr_contrato' not in self.df.columns:
            return {"erro": "Dados de contratos não disponíveis", "tipo": "erro"}
        
        df = self.df.copy()
        
        # Filtrar por período se fornecido
        if inicio and fim:
            df['data'] = pd.to_datetime(df['d_dt_data'], errors='coerce')
            inicio_dt = pd.to_datetime(inicio)
            fim_dt = pd.to_datetime(fim)
            df = df[(df['data'] >= inicio_dt) & (df['data'] <= fim_dt)]
            periodo_texto = f" ({inicio} a {fim})"
        else:
            periodo_texto = ""
        
        # Agrupar por contrato
        contratos = df.groupby('s_nr_contrato').agg({
            'duracao_horas': 'sum',
            's_id_apontamento': 'count',
            's_nm_recurso': 'nunique'
        }).sort_values('duracao_horas', ascending=False)
        
        contratos.columns = ['total_horas', 'apontamentos', 'recursos']
        
        resposta = f"📋 **Contratos com Apontamentos{periodo_texto}** ({len(contratos)} contratos)\n\n"
        
        # Mostrar TODOS os contratos
        for i, (contrato, row) in enumerate(contratos.iterrows(), 1):
            resposta += f"{i}. **{contrato}**\n"
            resposta += f"   ⏱️ {row['total_horas']:.2f}h | "
            resposta += f"📝 {int(row['apontamentos'])} apontamentos | "
            resposta += f"👥 {int(row['recursos'])} recursos\n\n"
        
        return {
            "resposta": resposta,
            "dados": contratos.to_dict('index'),
            "tipo": "contratos"
        }
    
    def recursos_por_contrato(self, contrato: str) -> Dict:
        """Lista recursos que trabalham em um contrato específico"""
        if self.df is None:
            return {"erro": "Dados de contratos não disponíveis", "tipo": "erro"}
        
        # Normalizar contrato (remover espaços e converter para string)
        contrato_busca = str(contrato).strip()
        
        # Buscar em s_nr_contrato (contratos EXTERNOS com E) OU contrato_fornecedor (contratos INTERNOS numéricos)
        df_contrato = pd.DataFrame()
        
        if 's_nr_contrato' in self.df.columns:
            df_externo = self.df[self.df['s_nr_contrato'].astype(str).str.strip() == contrato_busca]
            df_contrato = pd.concat([df_contrato, df_externo], ignore_index=True)
        
        if 'contrato_fornecedor' in self.df.columns:
            # Tentar como número float (ex: 7873.0)
            try:
                contrato_num = float(contrato_busca)
                df_interno = self.df[self.df['contrato_fornecedor'] == contrato_num]
                df_contrato = pd.concat([df_contrato, df_interno], ignore_index=True)
            except ValueError:
                pass  # Não é número, só busca em s_nr_contrato
        
        if len(df_contrato) == 0:
            return {
                "resposta": f"❌ Contrato '{contrato}' não encontrado nos registros.",
                "tipo": "erro"
            }
        
        # Agrupar por recurso
        recursos = df_contrato.groupby('s_nm_recurso').agg({
            'duracao_horas': 'sum',
            's_id_apontamento': 'count',
            's_ds_cargo': 'first',
            'tecnologia': 'first',
            'perfil': 'first'
        }).sort_values('duracao_horas', ascending=False)
        
        resposta = f"📋 **Contrato: {contrato}**\n\n"
        resposta += f"👥 **{len(recursos)} recursos trabalhando**\n\n"
        
        for i, (nome, row) in enumerate(recursos.head(20).iterrows(), 1):
            resposta += f"{i}. **{nome}**\n"
            resposta += f"   ⏱️ {row['duracao_horas']:.2f}h | "
            resposta += f"📝 {int(row['s_id_apontamento'])} apontamentos\n"
            if pd.notna(row.get('perfil')):
                resposta += f"   💼 {row.get('perfil', 'N/A')}"
            if pd.notna(row.get('tecnologia')):
                resposta += f" | 💻 {row.get('tecnologia', 'N/A')}\n"
            else:
                resposta += "\n"
        
        if len(recursos) > 20:
            resposta += f"\n... e mais {len(recursos) - 20} recursos\n"
        
        return {
            "resposta": resposta,
            "dados": recursos.to_dict('index'),
            "tipo": "recursos_contrato"
        }
    
    def horas_esperadas_colaborador(self, usuario: str, data_inicio: str, data_fim: str) -> Dict:
        """
        Calcula quantas horas o colaborador deveria fazer no período (dias úteis × jornada)
        e lista todos os apontamentos detalhados com contrato, horários e indicação de almoço
        
        Args:
            usuario: Nome do colaborador
            data_inicio: Data inicial (formato: DD/MM/YYYY ou YYYY-MM-DD)
            data_fim: Data final (formato: DD/MM/YYYY ou YYYY-MM-DD)
        
        Returns:
            Dicionário com horas esperadas vs realizadas e lista detalhada de apontamentos
        """
        if self.df is None:
            return {"erro": "Dados não disponíveis", "tipo": "erro"}
        
        try:
            # Converter strings para datetime
            inicio = pd.to_datetime(data_inicio, dayfirst=True)
            fim = pd.to_datetime(data_fim, dayfirst=True)
            
            # Filtrar apontamentos do usuário no período
            df_usuario = self.df[
                (self.df['s_nm_recurso'].str.contains(usuario, case=False, na=False)) &
                (self.df['data'] >= inicio) & 
                (self.df['data'] <= fim)
            ]
            
            if len(df_usuario) == 0:
                return {
                    "resposta": f"❌ Nenhum apontamento encontrado para '{usuario}' entre {inicio.date()} e {fim.date()}",
                    "tipo": "erro"
                }
            
            # Calcular dias úteis no período
            dias_uteis = 0
            data_atual = inicio
            while data_atual <= fim:
                if self.eh_dia_util(data_atual):
                    dias_uteis += 1
                data_atual += timedelta(days=1)
            
            # Jornada padrão: 8h/dia (pode ajustar conforme necessário)
            JORNADA_DIARIA = 8.0
            horas_esperadas = dias_uteis * JORNADA_DIARIA
            
            # Calcular horas realizadas (brutas)
            horas_realizadas = df_usuario['duracao_horas'].sum()
            
            # Agrupar apontamentos por dia
            apontamentos_detalhados = []
            for data, grupo in df_usuario.groupby(df_usuario['data'].dt.date):
                for _, apontamento in grupo.iterrows():
                    # Extrair informações
                    contrato = apontamento.get('s_nr_contrato', 'N/A')
                    operacao = apontamento.get('s_ds_operacao', 'N/A')
                    hora_inicio = apontamento.get('f_hr_hora_inicio', 'N/A')
                    hora_fim = apontamento.get('f_hr_hora_fim', 'N/A')
                    duracao = apontamento.get('duracao_horas', 0)
                    
                    # Determinar se teve almoço (se trabalhou mais de 6h no dia e é dia útil)
                    data_dt = pd.Timestamp(data)
                    horas_dia = grupo['duracao_horas'].sum()
                    tem_almoco = self.eh_dia_util(data_dt) and duracao > 0
                    
                    apontamentos_detalhados.append({
                        'data': str(data),
                        'contrato': contrato,
                        'operacao': operacao,
                        'hora_inicio': hora_inicio,
                        'hora_fim': hora_fim,
                        'duracao': duracao,
                        'tem_almoco': tem_almoco
                    })
            
            # Ordenar por data
            apontamentos_detalhados.sort(key=lambda x: x['data'])
            
            # Montar resposta
            nome_completo = df_usuario['s_nm_recurso'].iloc[0]
            diferenca = horas_realizadas - horas_esperadas
            percentual = (horas_realizadas / horas_esperadas * 100) if horas_esperadas > 0 else 0
            
            resposta = f"👤 **Colaborador:** {nome_completo}\n"
            resposta += f"📅 **Período:** {inicio.date()} a {fim.date()}\n\n"
            resposta += f"📊 **Análise de Horas:**\n"
            resposta += f"• **Dias Úteis no Período:** {dias_uteis} dias\n"
            resposta += f"• **Horas Esperadas (8h/dia):** {horas_esperadas:.2f}h\n"
            resposta += f"• **Horas Realizadas:** {horas_realizadas:.2f}h\n"
            
            if diferenca >= 0:
                resposta += f"• **Diferença:** +{diferenca:.2f}h ({percentual:.1f}%) ✅\n\n"
            else:
                resposta += f"• **Diferença:** {diferenca:.2f}h ({percentual:.1f}%) ⚠️\n\n"
            
            resposta += f"📝 **Apontamentos Detalhados ({len(apontamentos_detalhados)} registros):**\n\n"
            
            for apt in apontamentos_detalhados:
                almoco_icon = "🍽️" if apt['tem_almoco'] else "⏱️"
                resposta += f"{almoco_icon} **{apt['data']}** - {apt['hora_inicio']} às {apt['hora_fim']} ({apt['duracao']:.2f}h)\n"
                resposta += f"   📋 Contrato: {apt['contrato']}\n"
                resposta += f"   💼 Operação: {apt['operacao']}\n"
                if apt['tem_almoco']:
                    resposta += f"   🍽️ Almoço: Sim (1h descontada)\n"
                resposta += "\n"
            
            return {
                "resposta": resposta,
                "dados": {
                    "colaborador": nome_completo,
                    "periodo": {
                        "inicio": str(inicio.date()),
                        "fim": str(fim.date()),
                        "dias_uteis": dias_uteis
                    },
                    "horas": {
                        "esperadas": round(horas_esperadas, 2),
                        "realizadas": round(horas_realizadas, 2),
                        "diferenca": round(diferenca, 2),
                        "percentual": round(percentual, 1)
                    },
                    "apontamentos": apontamentos_detalhados
                },
                "tipo": "analise_colaborador"
            }
            
        except Exception as e:
            return {
                "resposta": f"❌ Erro ao processar: {str(e)}",
                "tipo": "erro"
            }

    def verificar_saidas_esquecidas(self, usuario: str, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> Dict:
        """
        Verifica se o recurso esqueceu de informar horário de saída em algum dia
        (tem hora de entrada mas não tem hora de saída ou hora de saída inválida)
        
        Args:
            usuario: Nome do colaborador
            data_inicio: Data inicial opcional (formato: DD/MM/YYYY)
            data_fim: Data final opcional (formato: DD/MM/YYYY)
        
        Returns:
            Dicionário com lista de apontamentos com saída esquecida
        """
        if self.df is None:
            return {"erro": "Dados não disponíveis", "tipo": "erro"}
        
        try:
            # Filtrar por usuário
            df_usuario = self.df[self.df['s_nm_recurso'].str.contains(usuario, case=False, na=False)]
            
            if len(df_usuario) == 0:
                return {
                    "resposta": f"❌ Usuário '{usuario}' não encontrado nos registros.",
                    "tipo": "erro"
                }
            
            # Filtrar por período se especificado
            if data_inicio and data_fim:
                inicio = pd.to_datetime(data_inicio, dayfirst=True)
                fim = pd.to_datetime(data_fim, dayfirst=True)
                df_usuario = df_usuario[(df_usuario['data'] >= inicio) & (df_usuario['data'] <= fim)]
                periodo_msg = f" entre {inicio.date()} e {fim.date()}"
            elif data_inicio:
                inicio = pd.to_datetime(data_inicio, dayfirst=True)
                df_usuario = df_usuario[df_usuario['data'] >= inicio]
                periodo_msg = f" a partir de {inicio.date()}"
            elif data_fim:
                fim = pd.to_datetime(data_fim, dayfirst=True)
                df_usuario = df_usuario[df_usuario['data'] <= fim]
                periodo_msg = f" até {fim.date()}"
            else:
                periodo_msg = ""
            
            # Detectar apontamentos com problemas na saída
            problemas = []
            
            for _, apontamento in df_usuario.iterrows():
                hora_inicio = apontamento.get('f_hr_hora_inicio', None)
                hora_fim = apontamento.get('f_hr_hora_fim', None)
                data = apontamento.get('data', None)
                contrato = apontamento.get('s_nr_contrato', 'N/A')
                operacao = apontamento.get('s_ds_operacao', 'N/A')
                
                # Verificar se tem entrada mas não tem saída ou saída inválida
                tem_problema = False
                tipo_problema = ""
                
                if pd.notna(hora_inicio) and hora_inicio not in [None, '', 'N/A']:
                    # Tem hora de entrada
                    if pd.isna(hora_fim) or hora_fim in [None, '', 'N/A', 0]:
                        tem_problema = True
                        tipo_problema = "❌ Sem horário de saída"
                    elif hora_fim == hora_inicio:
                        tem_problema = True
                        tipo_problema = "⚠️ Horário de entrada = saída"
                    elif hora_fim < hora_inicio:
                        tem_problema = True
                        tipo_problema = "⚠️ Horário de saída antes da entrada"
                
                if tem_problema:
                    problemas.append({
                        'data': str(data.date()) if pd.notna(data) else 'N/A',
                        'tipo_problema': tipo_problema,
                        'hora_inicio': hora_inicio,
                        'hora_fim': hora_fim if pd.notna(hora_fim) else 'NÃO INFORMADA',
                        'contrato': contrato,
                        'operacao': operacao
                    })
            
            # Ordenar por data
            problemas.sort(key=lambda x: x['data'])
            
            # Montar resposta
            nome_completo = df_usuario['s_nm_recurso'].iloc[0]
            
            if len(problemas) == 0:
                resposta = f"✅ **Colaborador:** {nome_completo}\n"
                resposta += f"📅 **Período:** {periodo_msg if periodo_msg else 'Todos os registros'}\n\n"
                resposta += f"🎉 **Nenhum problema encontrado!**\n"
                resposta += f"Todos os {len(df_usuario)} apontamentos têm horários de entrada e saída válidos."
                
                return {
                    "resposta": resposta,
                    "dados": {
                        "colaborador": nome_completo,
                        "problemas": 0,
                        "total_apontamentos": len(df_usuario)
                    },
                    "tipo": "verificacao_saidas"
                }
            
            resposta = f"⚠️ **Colaborador:** {nome_completo}\n"
            resposta += f"📅 **Período:** {periodo_msg if periodo_msg else 'Todos os registros'}\n\n"
            resposta += f"❌ **Encontrados {len(problemas)} problema(s) de horário:**\n\n"
            
            for problema in problemas:
                resposta += f"{problema['tipo_problema']}\n"
                resposta += f"📅 **Data:** {problema['data']}\n"
                resposta += f"🕐 **Entrada:** {problema['hora_inicio']}\n"
                resposta += f"🕐 **Saída:** {problema['hora_fim']}\n"
                resposta += f"📋 **Contrato:** {problema['contrato']}\n"
                resposta += f"💼 **Operação:** {problema['operacao']}\n"
                resposta += "\n"
            
            resposta += f"📊 **Total analisado:** {len(df_usuario)} apontamentos\n"
            resposta += f"⚠️ **Com problemas:** {len(problemas)} ({len(problemas)/len(df_usuario)*100:.1f}%)"
            
            return {
                "resposta": resposta,
                "dados": {
                    "colaborador": nome_completo,
                    "problemas": len(problemas),
                    "total_apontamentos": len(df_usuario),
                    "percentual_problemas": round(len(problemas)/len(df_usuario)*100, 1),
                    "detalhes": problemas
                },
                "tipo": "verificacao_saidas"
            }
            
        except Exception as e:
            return {
                "resposta": f"❌ Erro ao processar: {str(e)}",
                "tipo": "erro"
            }

    def ajuda(self) -> Dict:
        """Retorna mensagem de ajuda"""
        return {
            "resposta": """
🤖 **Comandos Disponíveis:**

📊 **Estatísticas:**
• "Qual a média de horas?"
• "Quanto tempo trabalhei?"
• "Total de horas"

📅 **Consultas Temporais:**
• "Quanto apontei hoje?"
• "Resumo da semana"
• "Comparar semanas"

🏆 **Rankings:**
• "Ranking de horas"
• "Quem trabalhou mais?"

⚠️ **Análises:**
• "Mostrar outliers"
• "Apontamentos fora do padrão"

💡 **Dica:** Mencione seu nome para consultas personalizadas!
""",
            "tipo": "ajuda"
        }


# Exemplo de uso para integração com chat
def processar_mensagem_chat(mensagem: str, usuario: str = None) -> str:
    """
    Função simples para integração com chatbot
    
    Args:
        mensagem: Mensagem do usuário
        usuario: Nome do usuário (obtido do Teams)
    
    Returns:
        Resposta formatada em Markdown
    """
    agente = AgenteApontamentos()
    resultado = agente.responder_pergunta(mensagem, usuario)
    return resultado.get('resposta', 'Desculpe, não entendi.')


if __name__ == "__main__":
    # Teste interativo
    print("\n" + "="*80)
    print("🤖 AGENTE INTELIGENTE DE APONTAMENTOS - MODO TESTE")
    print("="*80 + "\n")
    
    agente = AgenteApontamentos()
    
    if agente.df is None:
        print("❌ Não foi possível carregar os dados.")
        print("Execute: python analise_duracao_trabalho.py")
    else:
        print("✅ Agente inicializado com sucesso!")
        print("\n💡 Exemplos de perguntas:\n")
        
        # Teste de perguntas
        perguntas_teste = [
            "Qual a média de horas?",
            "Mostrar ranking",
            "Identificar outliers"
        ]
        
        for pergunta in perguntas_teste:
            print(f"\n❓ {pergunta}")
            resposta = agente.responder_pergunta(pergunta)
            print(f"🤖 {resposta['resposta']}")
            print("-" * 80)
        
        print("\n💡 Digite 'ajuda' para ver todos os comandos disponíveis")
