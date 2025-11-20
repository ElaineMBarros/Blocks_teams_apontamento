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
            return self.listar_contratos()
        
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
            media_horas_liquidas = total_horas_liquidas / dias_trabalhados_total if dias_trabalhados_total > 0 else 0
            
            # Ranking no período
            top_usuarios = df_periodo.groupby('s_nm_recurso')['duracao_horas'].sum().nlargest(5)
            
            resposta = f"📅 **Período: {inicio.date()} a {fim.date()}**\n\n"
            if usuario:
                resposta += f"👤 Usuário: **{usuario}**\n\n"
            
            resposta += f"⏱️ **Horas Brutas:** {total_horas_brutas:.2f}h\n" + \
                       f"🍽️ **Desconto Almoço:** {total_desconto_almoco:.1f}h\n" + \
                       f"✅ **Horas Líquidas:** {total_horas_liquidas:.2f}h\n\n" + \
                       f"📊 **Média Bruta:** {media_horas_brutas:.2f}h/dia\n" + \
                       f"📊 **Média Líquida:** {media_horas_liquidas:.2f}h/dia\n\n" + \
                       f"📝 **Apontamentos:** {quantidade}\n" + \
                       f"📅 **Dias Úteis:** {dias_uteis_trabalhados}\n" + \
                       f"🏖️ **Fins de Semana:** {dias_fim_semana_trabalhados}\n" + \
                       f"📆 **Total de Dias:** {dias_trabalhados_total}"
            
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
                    "media_horas_brutas": round(media_horas_brutas, 2),
                    "media_horas_liquidas": round(media_horas_liquidas, 2),
                    "quantidade": quantidade,
                    "dias_uteis": dias_uteis_trabalhados,
                    "dias_fim_semana": dias_fim_semana_trabalhados,
                    "dias_trabalhados": dias_trabalhados_total,
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
    
    def listar_contratos(self) -> Dict:
        """Lista todos os contratos com apontamentos"""
        if self.df is None or 's_nr_contrato' not in self.df.columns:
            return {"erro": "Dados de contratos não disponíveis", "tipo": "erro"}
        
        # Agrupar por contrato
        contratos = self.df.groupby('s_nr_contrato').agg({
            'duracao_horas': 'sum',
            's_id_apontamento': 'count',
            's_nm_recurso': 'nunique'
        }).sort_values('duracao_horas', ascending=False)
        
        contratos.columns = ['total_horas', 'apontamentos', 'recursos']
        
        resposta = f"📋 **Contratos com Apontamentos** ({len(contratos)} contratos)\n\n"
        
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
