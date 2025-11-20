"""
🤖 AGENTE INTELIGENTE DE APONTAMENTOS V2
API completa para consultas dinâmicas sobre dados de apontamento
Inclui: Validação, Contratos, Tecnologias, Perfis e Níveis
Preparado para integração com chatbot do Microsoft Teams
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import glob
import re

class AgenteApontamentosV2:
    """
    Agente inteligente com funcionalidades expandidas
    Consultas por: validação, contrato, tecnologia, perfil, nível
    """
    
    def __init__(self):
        """Inicializa o agente e carrega dados"""
        self.df = None
        self.ultima_atualizacao = None
        self.carregar_dados()
        
    def carregar_dados(self) -> bool:
        """Carrega os dados mais recentes (preferencialmente o CSV decupado)"""
        try:
            # Tentar carregar CSV decupado primeiro
            arquivos_decupados = glob.glob("resultados/dados_anonimizados_decupado_*.csv")
            
            if arquivos_decupados:
                arquivo = max(arquivos_decupados)
                print(f"📂 Carregando CSV decupado: {arquivo}")
            else:
                # Fallback para CSV com duração
                arquivos = glob.glob("resultados/dados_com_duracao_*.csv")
                if not arquivos:
                    print("⚠️ Nenhum dado encontrado.")
                    return False
                arquivo = max(arquivos)
                print(f"📂 Carregando CSV padrão: {arquivo}")
            
            self.df = pd.read_csv(arquivo, encoding='utf-8', low_memory=False)
            
            # Preparar dados
            self.preparar_dados()
            
            self.ultima_atualizacao = datetime.now()
            print(f"✅ Dados carregados: {len(self.df)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def preparar_dados(self):
        """Prepara e enriquece os dados"""
        # Converter datas
        if 'd_dt_data' in self.df.columns:
            self.df['data'] = pd.to_datetime(self.df['d_dt_data'], errors='coerce')
        
        # Se não tiver colunas decupadas, fazer agora
        if 'contrato_fornecedor' not in self.df.columns and 's_ds_cargo' in self.df.columns:
            print("🔧 Decupando cargos...")
            self.decupar_cargos()
        
        # Criar flag de validação
        if 'b_fl_validado' in self.df.columns:
            self.df['validado'] = self.df['b_fl_validado'] == 1
        
        print("✅ Dados preparados")
    
    def decupar_cargos(self):
        """Decupa campo s_ds_cargo em componentes"""
        def decupar_cargo(cargo_str):
            if pd.isna(cargo_str) or cargo_str == '':
                return pd.Series([None, None, None, None, None])
            
            try:
                pattern = r'^(\d+)-(\d+)-([^-]+)-(.+)-(.+)$'
                match = re.match(pattern, cargo_str)
                
                if match:
                    return pd.Series([
                        match.group(1),
                        match.group(2),
                        match.group(3).strip(),
                        match.group(4).strip(),
                        match.group(5).strip()
                    ])
                else:
                    partes = cargo_str.split('-')
                    if len(partes) >= 5:
                        return pd.Series([p.strip() for p in partes[:5]])
                    return pd.Series([None, None, None, None, None])
            except:
                return pd.Series([None, None, None, None, None])
        
        self.df[['contrato_fornecedor', 'item_contrato', 'tecnologia', 
                 'perfil', 'nivel']] = self.df['s_ds_cargo'].apply(decupar_cargo)
    
    # ==================== NOVAS FUNÇÕES DE CONSULTA ====================
    
    def consultar_por_validacao(self, status='pendente') -> Dict:
        """
        Consulta apontamentos por status de validação
        
        Args:
            status: 'pendente', 'validado' ou 'todos'
        
        Returns:
            Dict com estatísticas de validação
        """
        if self.df is None:
            return {"erro": "Dados não disponíveis"}
        
        if 'validado' not in self.df.columns:
            return {"erro": "Campo de validação não disponível"}
        
        total = len(self.df)
        validados = self.df['validado'].sum()
        pendentes = total - validados
        
        pct_validados = (validados / total * 100) if total > 0 else 0
        pct_pendentes = (pendentes / total * 100) if total > 0 else 0
        
        if status == 'pendente':
            df_filtrado = self.df[~self.df['validado']]
            titulo = "⏳ APONTAMENTOS PENDENTES DE VALIDAÇÃO"
        elif status == 'validado':
            df_filtrado = self.df[self.df['validado']]
            titulo = "✅ APONTAMENTOS VALIDADOS"
        else:
            df_filtrado = self.df
            titulo = "📊 TODOS OS APONTAMENTOS"
        
        # Apontamentos mais antigos pendentes
        pendentes_antigos = []
        if status == 'pendente' and 'data' in self.df.columns:
            df_pend = self.df[~self.df['validado']].sort_values('data')
            if len(df_pend) > 0:
                for data, grupo in df_pend.groupby(df_pend['data'].dt.date):
                    pendentes_antigos.append({
                        'data': str(data),
                        'quantidade': len(grupo)
                    })
                    if len(pendentes_antigos) >= 5:
                        break
        
        resposta = f"{titulo}\n\n" + \
                   f"✅ Validados: {validados:,} ({pct_validados:.1f}%)\n" + \
                   f"⏳ Pendentes: {pendentes:,} ({pct_pendentes:.1f}%)\n" + \
                   f"📊 Total: {total:,}"
        
        if pendentes_antigos and status == 'pendente':
            resposta += "\n\n⚠️ **Mais antigos pendentes:**\n"
            for item in pendentes_antigos:
                resposta += f"• {item['quantidade']} de {item['data']}\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "total": total,
                "validados": int(validados),
                "pendentes": int(pendentes),
                "pct_validados": round(pct_validados, 2),
                "pct_pendentes": round(pct_pendentes, 2),
                "pendentes_antigos": pendentes_antigos
            },
            "tipo": "validacao"
        }
    
    def consultar_por_contrato(self, contrato: str) -> Dict:
        """
        Consulta apontamentos de um contrato específico
        
        Args:
            contrato: Código do contrato (ex: '7874', '8446')
        
        Returns:
            Dict com dados do contrato
        """
        if self.df is None or 'contrato_fornecedor' not in self.df.columns:
            return {"erro": "Dados de contrato não disponíveis"}
        
        # Converter para string para comparação (pode vir como float)
        df_contrato = self.df[self.df['contrato_fornecedor'].astype(str) == str(contrato)]
        
        if len(df_contrato) == 0:
            return {"resposta": f"❌ Contrato {contrato} não encontrado", "tipo": "erro"}
        
        # Estatísticas
        total_apontamentos = len(df_contrato)
        recursos_unicos = df_contrato['s_nm_recurso'].nunique() if 's_nm_recurso' in df_contrato.columns else 0
        
        # Horas (se disponível)
        total_horas = 0
        if 'duracao_horas' in df_contrato.columns:
            total_horas = df_contrato['duracao_horas'].sum()
        
        # Tecnologia principal
        tecnologia = df_contrato['tecnologia'].mode()[0] if 'tecnologia' in df_contrato.columns and len(df_contrato['tecnologia'].dropna()) > 0 else "N/A"
        
        # Top perfis
        top_perfis = []
        if 'perfil' in df_contrato.columns:
            top_perfis = df_contrato['perfil'].value_counts().head(3).to_dict()
        
        resposta = f"📋 **CONTRATO {contrato}**\n\n" + \
                   f"💻 Tecnologia: {tecnologia}\n" + \
                   f"📊 Total de apontamentos: {total_apontamentos:,}\n" + \
                   f"👥 Recursos únicos: {recursos_unicos}\n"
        
        if total_horas > 0:
            resposta += f"⏱️ Total de horas: {total_horas:,.2f}h\n"
        
        if top_perfis:
            resposta += "\n📋 **Top Perfis:**\n"
            for i, (perfil, qtd) in enumerate(list(top_perfis.items())[:3], 1):
                resposta += f"{i}. {perfil}: {qtd} apontamentos\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "contrato": contrato,
                "tecnologia": tecnologia,
                "total_apontamentos": total_apontamentos,
                "recursos_unicos": recursos_unicos,
                "total_horas": round(total_horas, 2),
                "top_perfis": top_perfis
            },
            "tipo": "contrato"
        }
    
    def consultar_por_tecnologia(self, tecnologia: str) -> Dict:
        """Consulta apontamentos por tecnologia"""
        if self.df is None or 'tecnologia' not in self.df.columns:
            return {"erro": "Dados de tecnologia não disponíveis"}
        
        df_tec = self.df[self.df['tecnologia'].str.contains(tecnologia, case=False, na=False)]
        
        if len(df_tec) == 0:
            return {"resposta": f"❌ Tecnologia '{tecnologia}' não encontrada", "tipo": "erro"}
        
        total = len(df_tec)
        recursos = df_tec['s_nm_recurso'].nunique() if 's_nm_recurso' in df_tec.columns else 0
        contratos = [str(c) for c in df_tec['contrato_fornecedor'].unique() if pd.notna(c)]
        
        total_horas = 0
        if 'duracao_horas' in df_tec.columns:
            total_horas = df_tec['duracao_horas'].sum()
        
        resposta = f"💻 **TECNOLOGIA: {tecnologia.upper()}**\n\n" + \
                   f"📊 Apontamentos: {total:,}\n" + \
                   f"👥 Recursos: {recursos}\n" + \
                   f"📋 Contratos: {', '.join(contratos)}\n"
        
        if total_horas > 0:
            resposta += f"⏱️ Total de horas: {total_horas:,.2f}h\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "tecnologia": tecnologia,
                "total": total,
                "recursos": recursos,
                "contratos": contratos,
                "total_horas": round(total_horas, 2)
            },
            "tipo": "tecnologia"
        }
    
    def consultar_por_perfil(self, perfil: str) -> Dict:
        """Consulta apontamentos por perfil profissional"""
        if self.df is None or 'perfil' not in self.df.columns:
            return {"erro": "Dados de perfil não disponíveis"}
        
        df_perfil = self.df[self.df['perfil'].str.contains(perfil, case=False, na=False)]
        
        if len(df_perfil) == 0:
            return {"resposta": f"❌ Perfil '{perfil}' não encontrado", "tipo": "erro"}
        
        total = len(df_perfil)
        recursos = df_perfil['s_nm_recurso'].nunique() if 's_nm_recurso' in df_perfil.columns else 0
        
        # Top tecnologias para este perfil
        top_tec = []
        if 'tecnologia' in df_perfil.columns:
            top_tec = df_perfil['tecnologia'].value_counts().head(3).to_dict()
        
        total_horas = 0
        if 'duracao_horas' in df_perfil.columns:
            total_horas = df_perfil['duracao_horas'].sum()
        
        resposta = f"👔 **PERFIL: {perfil.upper()}**\n\n" + \
                   f"📊 Apontamentos: {total:,}\n" + \
                   f"👥 Profissionais: {recursos}\n"
        
        if total_horas > 0:
            resposta += f"⏱️ Total de horas: {total_horas:,.2f}h\n"
        
        if top_tec:
            resposta += "\n💻 **Top Tecnologias:**\n"
            for i, (tec, qtd) in enumerate(list(top_tec.items())[:3], 1):
                resposta += f"{i}. {tec}: {qtd} apontamentos\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "perfil": perfil,
                "total": total,
                "recursos": recursos,
                "total_horas": round(total_horas, 2),
                "top_tecnologias": top_tec
            },
            "tipo": "perfil"
        }
    
    def consultar_por_nivel(self, nivel: str) -> Dict:
        """Consulta apontamentos por nível hierárquico"""
        if self.df is None or 'nivel' not in self.df.columns:
            return {"erro": "Dados de nível não disponíveis"}
        
        df_nivel = self.df[self.df['nivel'].str.contains(nivel, case=False, na=False)]
        
        if len(df_nivel) == 0:
            return {"resposta": f"❌ Nível '{nivel}' não encontrado", "tipo": "erro"}
        
        total = len(df_nivel)
        recursos = df_nivel['s_nm_recurso'].nunique() if 's_nm_recurso' in df_nivel.columns else 0
        
        # Distribuição por perfil
        top_perfis = []
        if 'perfil' in df_nivel.columns:
            top_perfis = df_nivel['perfil'].value_counts().head(5).to_dict()
        
        total_horas = 0
        if 'duracao_horas' in df_nivel.columns:
            total_horas = df_nivel['duracao_horas'].sum()
        
        resposta = f"📈 **NÍVEL: {nivel.upper()}**\n\n" + \
                   f"📊 Apontamentos: {total:,}\n" + \
                   f"👥 Profissionais: {recursos}\n"
        
        if total_horas > 0:
            resposta += f"⏱️ Total de horas: {total_horas:,.2f}h\n"
        
        if top_perfis:
            resposta += "\n👔 **Top Perfis:**\n"
            for i, (p, qtd) in enumerate(list(top_perfis.items())[:5], 1):
                resposta += f"{i}. {p}: {qtd}\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "nivel": nivel,
                "total": total,
                "recursos": recursos,
                "total_horas": round(total_horas, 2),
                "top_perfis": top_perfis
            },
            "tipo": "nivel"
        }
    
    def consulta_combinada(self, filtros: Dict) -> Dict:
        """
        Consulta com múltiplos filtros
        
        Args:
            filtros: Dict com chaves: contrato, tecnologia, perfil, nivel, validado
        
        Returns:
            Dict com resultados filtrados
        """
        if self.df is None:
            return {"erro": "Dados não disponíveis"}
        
        df_filtrado = self.df.copy()
        filtros_aplicados = []
        
        # Aplicar filtros
        if 'contrato' in filtros and 'contrato_fornecedor' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['contrato_fornecedor'] == str(filtros['contrato'])]
            filtros_aplicados.append(f"Contrato {filtros['contrato']}")
        
        if 'tecnologia' in filtros and 'tecnologia' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['tecnologia'].str.contains(filtros['tecnologia'], case=False, na=False)]
            filtros_aplicados.append(f"Tecnologia {filtros['tecnologia']}")
        
        if 'perfil' in filtros and 'perfil' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['perfil'].str.contains(filtros['perfil'], case=False, na=False)]
            filtros_aplicados.append(f"Perfil {filtros['perfil']}")
        
        if 'nivel' in filtros and 'nivel' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['nivel'].str.contains(filtros['nivel'], case=False, na=False)]
            filtros_aplicados.append(f"Nível {filtros['nivel']}")
        
        if 'validado' in filtros and 'validado' in df_filtrado.columns:
            if filtros['validado']:
                df_filtrado = df_filtrado[df_filtrado['validado']]
                filtros_aplicados.append("Validados")
            else:
                df_filtrado = df_filtrado[~df_filtrado['validado']]
                filtros_aplicados.append("Pendentes")
        
        if len(df_filtrado) == 0:
            return {"resposta": "❌ Nenhum resultado encontrado com estes filtros", "tipo": "erro"}
        
        total = len(df_filtrado)
        recursos = df_filtrado['s_nm_recurso'].nunique() if 's_nm_recurso' in df_filtrado.columns else 0
        
        total_horas = 0
        if 'duracao_horas' in df_filtrado.columns:
            total_horas = df_filtrado['duracao_horas'].sum()
        
        resposta = f"🔍 **CONSULTA COMBINADA**\n\n" + \
                   f"Filtros: {', '.join(filtros_aplicados)}\n\n" + \
                   f"📊 Apontamentos: {total:,}\n" + \
                   f"👥 Recursos: {recursos}\n"
        
        if total_horas > 0:
            resposta += f"⏱️ Total de horas: {total_horas:,.2f}h\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "filtros": filtros_aplicados,
                "total": total,
                "recursos": recursos,
                "total_horas": round(total_horas, 2)
            },
            "tipo": "combinada"
        }
    
    def analise_validadores(self) -> Dict:
        """Análise de performance dos validadores"""
        if self.df is None or 's_nm_usuario_valida' not in self.df.columns:
            return {"erro": "Dados de validadores não disponíveis"}
        
        df_validados = self.df[self.df['validado'] == True]
        
        if len(df_validados) == 0:
            return {"resposta": "❌ Nenhum apontamento validado encontrado", "tipo": "erro"}
        
        # Ranking de validadores
        ranking = df_validados['s_nm_usuario_valida'].value_counts().head(10)
        
        total_validadores = df_validados['s_nm_usuario_valida'].nunique()
        total_validados = len(df_validados)
        
        resposta = f"👤 **ANÁLISE DE VALIDADORES**\n\n" + \
                   f"📊 Total de validadores: {total_validadores}\n" + \
                   f"✅ Apontamentos validados: {total_validados:,}\n\n" + \
                   f"🏆 **Top 10 Validadores:**\n\n"
        
        for i, (validador, qtd) in enumerate(ranking.items(), 1):
            pct = (qtd / total_validados * 100)
            resposta += f"{i}. {validador}: {qtd:,} ({pct:.1f}%)\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "total_validadores": total_validadores,
                "total_validados": total_validados,
                "ranking": ranking.to_dict()
            },
            "tipo": "validadores"
        }
    
    def dashboard_executivo(self) -> Dict:
        """Dashboard executivo com visão geral"""
        if self.df is None:
            return {"erro": "Dados não disponíveis"}
        
        # Estatísticas gerais
        total_apontamentos = len(self.df)
        
        # Por validação
        validados = 0
        pendentes = 0
        if 'validado' in self.df.columns:
            validados = self.df['validado'].sum()
            pendentes = total_apontamentos - validados
        
        # Por contrato
        top_contratos = {}
        if 'contrato_fornecedor' in self.df.columns:
            top_contratos = self.df['contrato_fornecedor'].value_counts().head(5).to_dict()
        
        # Por tecnologia
        top_tecnologias = {}
        if 'tecnologia' in self.df.columns:
            top_tecnologias = self.df['tecnologia'].value_counts().head(5).to_dict()
        
        # Por perfil
        top_perfis = {}
        if 'perfil' in self.df.columns:
            top_perfis = self.df['perfil'].value_counts().head(5).to_dict()
        
        # Recursos
        recursos_unicos = 0
        if 's_nm_recurso' in self.df.columns:
            recursos_unicos = self.df['s_nm_recurso'].nunique()
        
        # Horas
        total_horas = 0
        if 'duracao_horas' in self.df.columns:
            total_horas = self.df['duracao_horas'].sum()
        
        resposta = f"📊 **DASHBOARD EXECUTIVO**\n\n" + \
                   f"📋 **Geral:**\n" + \
                   f"• Apontamentos: {total_apontamentos:,}\n" + \
                   f"• Recursos: {recursos_unicos}\n"
        
        if total_horas > 0:
            resposta += f"• Horas: {total_horas:,.2f}h\n"
        
        if validados > 0 or pendentes > 0:
            resposta += f"\n✅ **Validação:**\n" + \
                       f"• Validados: {validados:,}\n" + \
                       f"• Pendentes: {pendentes:,}\n"
        
        if top_contratos:
            resposta += f"\n📋 **Top 3 Contratos:**\n"
            for i, (c, qtd) in enumerate(list(top_contratos.items())[:3], 1):
                resposta += f"{i}. {c}: {qtd:,}\n"
        
        if top_tecnologias:
            resposta += f"\n💻 **Top 3 Tecnologias:**\n"
            for i, (t, qtd) in enumerate(list(top_tecnologias.items())[:3], 1):
                resposta += f"{i}. {t}: {qtd:,}\n"
        
        return {
            "resposta": resposta,
            "dados": {
                "total_apontamentos": total_apontamentos,
                "recursos_unicos": recursos_unicos,
                "total_horas": round(total_horas, 2),
                "validados": int(validados),
                "pendentes": int(pendentes),
                "top_contratos": top_contratos,
                "top_tecnologias": top_tecnologias,
                "top_perfis": top_perfis
            },
            "tipo": "dashboard"
        }
    
    def listar_opcoes(self, tipo: str) -> Dict:
        """
        Lista todas as opções disponíveis de um tipo
        
        Args:
            tipo: 'contratos', 'tecnologias', 'perfis', 'niveis', 'validadores'
        
        Returns:
            Dict com lista de opções
        """
        if self.df is None:
            return {"erro": "Dados não disponíveis"}
        
        mapeamento = {
            'contratos': 'contrato_fornecedor',
            'tecnologias': 'tecnologia',
            'perfis': 'perfil',
            'niveis': 'nivel',
            'validadores': 's_nm_usuario_valida'
        }
        
        if tipo not in mapeamento:
            return {"erro": f"Tipo inválido: {tipo}"}
        
        coluna = mapeamento[tipo]
        
        if coluna not in self.df.columns:
            return {"erro": f"Coluna {coluna} não disponível"}
        
        opcoes = self.df[coluna].value_counts().to_dict()
        total = len(opcoes)
        
        resposta = f"📋 **{tipo.upper()} DISPONÍVEIS** ({total})\n\n"
        
        for i, (item, qtd) in enumerate(list(opcoes.items())[:20], 1):
            resposta += f"{i}. {item}: {qtd:,} apontamentos\n"
        
        if total > 20:
            resposta += f"\n... e mais {total - 20} opções"
        
        return {
            "resposta": resposta,
            "dados": {
                "tipo": tipo,
                "total": total,
                "opcoes": opcoes
            },
            "tipo": "lista"
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🤖 AGENTE INTELIGENTE DE APONTAMENTOS V2 - MODO TESTE")
    print("="*80 + "\n")
    
    agente = AgenteApontamentosV2()
    
    if agente.df is None:
        print("❌ Não foi possível carregar os dados.")
    else:
        print("\n✅ Testando novas funcionalidades...\n")
        
        # Testes
        print("1️⃣ Status de Validação:")
        print(agente.consultar_por_validacao('pendente')['resposta'])
        print("\n" + "-"*80 + "\n")
        
        print("2️⃣ Dashboard Executivo:")
        print(agente.dashboard_executivo()['resposta'])
        print("\n" + "-"*80 + "\n")
        
        print("3️⃣ Listar Tecnologias:")
        print(agente.listar_opcoes('tecnologias')['resposta'])
