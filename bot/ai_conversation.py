"""
🤖 MÓDULO DE CONVERSAÇÃO COM IA
Processamento de linguagem natural para consultas sobre apontamentos
Usa Azure OpenAI ou OpenAI para interpretação inteligente
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

try:
    from openai import AzureOpenAI, OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ openai não instalado. Execute: pip install openai")


class ConversacaoIA:
    """
    Gerencia conversações inteligentes sobre dados de apontamentos
    usando GPT para interpretação de linguagem natural
    """
    
    def __init__(self, agente_apontamentos):
        """
        Inicializa o módulo de conversação
        
        Args:
            agente_apontamentos: Instância do AgenteApontamentos com os dados
        """
        self.agente = agente_apontamentos
        self.historico_conversas = {}  # {user_id: [mensagens]}
        self.client = None
        self.model = None
        
        # Configurar cliente OpenAI
        self._configurar_cliente()
    
    def _configurar_cliente(self):
        """Configura cliente OpenAI (Azure ou OpenAI direto)"""
        if not OPENAI_AVAILABLE:
            print("⚠️ OpenAI não disponível - modo fallback")
            return
        
        try:
            # Tentar Azure OpenAI primeiro
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_key = os.getenv("AZURE_OPENAI_KEY")
            azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
            
            if azure_endpoint and azure_key:
                self.client = AzureOpenAI(
                    api_key=azure_key,
                    api_version="2024-02-15-preview",
                    azure_endpoint=azure_endpoint
                )
                self.model = azure_deployment
                print("✅ Azure OpenAI configurado")
                return
            
            # Fallback para OpenAI direto
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.client = OpenAI(api_key=openai_key)
                self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                print("✅ OpenAI configurado")
                return
            
            print("⚠️ Nenhuma chave de API configurada - modo fallback")
            
        except Exception as e:
            print(f"⚠️ Erro ao configurar OpenAI: {e}")
    
    def _obter_contexto_dados(self) -> str:
        """Prepara contexto sobre os dados disponíveis"""
        if self.agente.df is None:
            return "Dados não disponíveis no momento."
        
        df = self.agente.df
        
        # Estatísticas básicas
        total_registros = len(df)
        total_horas = df['duracao_horas'].sum()
        media_horas = df['duracao_horas'].mean()
        
        # Período dos dados
        data_min = df['data'].min() if 'data' in df.columns else None
        data_max = df['data'].max() if 'data' in df.columns else None
        
        # Top usuários
        top_usuarios = df.groupby('s_nm_recurso')['duracao_horas'].sum().nlargest(5)
        
        contexto = f"""
CONTEXTO DOS DADOS DE APONTAMENTOS:

**Estatísticas Gerais:**
- Total de registros: {total_registros}
- Total de horas: {total_horas:.2f}h
- Média de horas por apontamento: {media_horas:.2f}h
- Período: {data_min} até {data_max}

**Top 5 Usuários (por horas):**
{top_usuarios.to_string()}

**Colunas disponíveis:**
- s_nm_recurso: Nome do funcionário
- duracao_horas: Duração do apontamento em horas
- data: Data do apontamento
- s_ds_operacao: Descrição da operação
"""
        return contexto
    
    def _criar_prompt_sistema(self) -> str:
        """Cria o prompt do sistema com contexto dos dados"""
        return f"""Você é um assistente inteligente especializado em análise de dados de apontamentos de trabalho.
Seu objetivo é ajudar usuários a consultar e entender os dados de forma simples e direta.

{self._obter_contexto_dados()}

**DIRETRIZES:**
1. Seja CONCISO e DIRETO - respostas curtas e objetivas
2. Use emojis para tornar as respostas mais amigáveis
3. Sempre formate números (use vírgula para decimais, ex: 8,5h)
4. Se não souber algo, diga que não tem essa informação
5. Sugira consultas quando apropriado
6. Não invente dados - use apenas o que está disponível

**FERRAMENTAS DISPONÍVEIS:**
Você pode solicitar que eu execute funções para obter dados específicos:
- duracao_media_geral(): Média geral de horas
- duracao_media_usuario(nome): Média de um usuário específico
- apontamentos_hoje(usuario): Apontamentos de hoje
- ranking_funcionarios(): Top funcionários por horas
- total_horas_usuario(nome): Total de horas de um usuário
- identificar_outliers(): Apontamentos fora do padrão
- resumo_semanal(usuario): Resumo da semana
- comparar_periodos(): Comparar semanas

Para usar uma ferramenta, responda no formato:
FERRAMENTA: nome_da_funcao(parametros)

Exemplo de conversa:
User: "quantas horas eu trabalhei?"
Assistant: FERRAMENTA: total_horas_usuario(Usuario Nome)

User: "qual a média geral?"
Assistant: FERRAMENTA: duracao_media_geral()"""
    
    def _extrair_ferramenta(self, resposta_ia: str) -> Optional[Tuple[str, Dict]]:
        """
        Extrai chamada de ferramenta da resposta da IA
        
        Returns:
            (nome_funcao, parametros) ou None
        """
        if "FERRAMENTA:" not in resposta_ia:
            return None
        
        try:
            # Extrair linha com FERRAMENTA:
            for linha in resposta_ia.split('\n'):
                if "FERRAMENTA:" in linha:
                    chamada = linha.split("FERRAMENTA:")[1].strip()
                    
                    # Parse simples: nome_funcao(param1, param2)
                    if '(' in chamada:
                        nome = chamada.split('(')[0].strip()
                        params_str = chamada.split('(')[1].split(')')[0]
                        
                        # Converter para dict
                        params = {}
                        if params_str.strip():
                            # Por simplicidade, assumir apenas um parâmetro
                            params['arg'] = params_str.strip().strip('"\'')
                        
                        return (nome, params)
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair ferramenta: {e}")
        
        return None
    
    def _executar_ferramenta(self, nome: str, params: Dict, usuario: str) -> Dict:
        """Executa função do agente"""
        try:
            if nome == "duracao_media_geral":
                return self.agente.duracao_media_geral()
            
            elif nome == "duracao_media_usuario":
                user = params.get('arg', usuario)
                return self.agente.duracao_media_usuario(user)
            
            elif nome == "apontamentos_hoje":
                return self.agente.apontamentos_hoje(usuario)
            
            elif nome == "ranking_funcionarios":
                return self.agente.ranking_funcionarios()
            
            elif nome == "total_horas_usuario":
                user = params.get('arg', usuario)
                return self.agente.total_horas_usuario(user)
            
            elif nome == "identificar_outliers":
                return self.agente.identificar_outliers()
            
            elif nome == "resumo_semanal":
                return self.agente.resumo_semanal(usuario)
            
            elif nome == "comparar_periodos":
                return self.agente.comparar_periodos()
            
            else:
                return {"erro": f"Ferramenta '{nome}' não encontrada"}
        
        except Exception as e:
            return {"erro": f"Erro ao executar ferramenta: {e}"}
    
    def processar_mensagem(self, mensagem: str, usuario: str) -> Dict:
        """
        Processa mensagem do usuário com IA
        
        Args:
            mensagem: Mensagem do usuário
            usuario: Nome do usuário
        
        Returns:
            Dict com resposta e dados
        """
        # Se IA não disponível, usar fallback
        if not self.client:
            return self._fallback_processar(mensagem, usuario)
        
        try:
            # Obter histórico do usuário
            if usuario not in self.historico_conversas:
                self.historico_conversas[usuario] = []
            
            historico = self.historico_conversas[usuario]
            
            # Construir mensagens
            mensagens = [
                {"role": "system", "content": self._criar_prompt_sistema()}
            ]
            
            # Adicionar histórico (últimas 5 mensagens)
            mensagens.extend(historico[-5:])
            
            # Adicionar mensagem atual
            mensagens.append({"role": "user", "content": f"[Usuário: {usuario}] {mensagem}"})
            
            # Chamar IA
            response = self.client.chat.completions.create(
                model=self.model,
                messages=mensagens,
                temperature=0.7,
                max_tokens=500
            )
            
            resposta_ia = response.choices[0].message.content
            
            # Verificar se IA solicitou ferramenta
            ferramenta = self._extrair_ferramenta(resposta_ia)
            
            if ferramenta:
                nome_func, params = ferramenta
                
                # Executar ferramenta
                resultado = self._executar_ferramenta(nome_func, params, usuario)
                
                # Pedir para IA formatar resposta
                mensagens.append({"role": "assistant", "content": resposta_ia})
                mensagens.append({
                    "role": "user", 
                    "content": f"RESULTADO DA FERRAMENTA: {json.dumps(resultado, ensure_ascii=False)}\n\nAgora formate isso de forma amigável e concisa para o usuário."
                })
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=mensagens,
                    temperature=0.7,
                    max_tokens=300
                )
                
                resposta_final = response.choices[0].message.content
                
                # Atualizar histórico
                historico.append({"role": "user", "content": mensagem})
                historico.append({"role": "assistant", "content": resposta_final})
                
                return {
                    "resposta": resposta_final,
                    "dados": resultado.get('dados', {}),
                    "tipo": resultado.get('tipo', 'ia_conversacao'),
                    "usa_ia": True
                }
            
            else:
                # Resposta direta da IA
                historico.append({"role": "user", "content": mensagem})
                historico.append({"role": "assistant", "content": resposta_ia})
                
                return {
                    "resposta": resposta_ia,
                    "tipo": "ia_conversacao",
                    "usa_ia": True
                }
        
        except Exception as e:
            print(f"❌ Erro ao processar com IA: {e}")
            return self._fallback_processar(mensagem, usuario)
    
    def _fallback_processar(self, mensagem: str, usuario: str) -> Dict:
        """Fallback quando IA não está disponível"""
        # Usar lógica existente do agente
        return self.agente.responder_pergunta(mensagem, usuario)
    
    def limpar_historico(self, usuario: str):
        """Limpa histórico de conversação de um usuário"""
        if usuario in self.historico_conversas:
            self.historico_conversas[usuario] = []
