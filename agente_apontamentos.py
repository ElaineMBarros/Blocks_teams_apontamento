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
            arquivos = glob.glob("resultados/dados_com_duracao_*.csv")
            if not arquivos:
                print("⚠️ Nenhum dado encontrado. Execute: python analise_duracao_trabalho.py")
                return False
            
            arquivo_mais_recente = max(arquivos)
            self.df = pd.read_csv(arquivo_mais_recente, encoding='utf-8-sig')
            
            # Converter colunas de data
            if 'd_dt_data' in self.df.columns:
                self.df['data'] = pd.to_datetime(self.df['d_dt_data'], errors='coerce')
            
            self.ultima_atualizacao = datetime.now()
            print(f"✅ Dados carregados: {len(self.df)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
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
        """Retorna apontamentos do dia"""
        if self.df is None or 'data' not in self.df.columns:
            return {"erro": "Dados não disponíveis"}
        
        hoje = pd.Timestamp.now().date()
        df_hoje = self.df[
            (self.df['data'].dt.date == hoje) & 
            (self.df['s_nm_recurso'].str.contains(usuario, case=False, na=False))
        ]
        
        if len(df_hoje) == 0:
            return {
                "resposta": f"📅 Você ainda não tem apontamentos registrados para hoje ({hoje}).",
                "tipo": "info"
            }
        
        total_horas = df_hoje['duracao_horas'].sum()
        horas = int(total_horas)
        minutos = int((total_horas - horas) * 60)
        
        apontamentos = []
        for _, row in df_hoje.iterrows():
            apontamentos.append({
                "operacao": row.get('s_ds_operacao', 'N/A'),
                "duracao": row.get('duracao_horas', 0)
            })
        
        return {
            "resposta": f"📅 **Hoje ({hoje})**\n" +
                       f"⏱️ Total apontado: **{horas}h{minutos:02d}min**\n" +
                       f"📝 Número de apontamentos: {len(df_hoje)}",
            "dados": {
                "data": str(hoje),
                "total_horas": round(total_horas, 2),
                "quantidade": len(df_hoje),
                "apontamentos": apontamentos
            },
            "tipo": "dia_atual"
        }
    
    def resumo_semanal(self, usuario: str) -> Dict:
        """Retorna resumo da semana para um usuário"""
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
        
        total_horas = df_semana['duracao_horas'].sum()
        media_diaria = df_semana.groupby(df_semana['data'].dt.date)['duracao_horas'].sum().mean()
        
        return {
            "resposta": f"📅 **Resumo Semanal - {usuario}**\n" +
                       f"⏱️ Total: {total_horas:.2f}h\n" +
                       f"📊 Média diária: {media_diaria:.2f}h\n" +
                       f"📝 Apontamentos: {len(df_semana)}",
            "dados": {
                "total_horas": round(total_horas, 2),
                "media_diaria": round(media_diaria, 2),
                "quantidade": len(df_semana)
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
