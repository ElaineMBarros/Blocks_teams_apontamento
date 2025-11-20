"""
🔐 GERENCIADOR DE SESSÕES - MULTISESSÃO
Isola contexto e histórico de cada usuário
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio


class SessionManager:
    """
    Gerencia sessões isoladas por conversation_id
    Cada usuário tem seu próprio histórico e contexto
    """
    
    def __init__(self, timeout_minutes: int = 30):
        """
        Inicializa o gerenciador de sessões
        
        Args:
            timeout_minutes: Tempo para expirar sessão inativa (padrão: 30 min)
        """
        self.sessions: Dict[str, Dict] = {}
        self.timeout_minutes = timeout_minutes
        self._cleanup_task = None
        
        # Limpeza automática será iniciada quando houver um loop de eventos
    
    def get_or_create_session(self, conversation_id: str) -> Dict:
        """
        Obtém sessão existente ou cria nova
        
        Args:
            conversation_id: ID único da conversa
        
        Returns:
            Dict com dados da sessão
        """
        if conversation_id not in self.sessions:
            self.sessions[conversation_id] = {
                'historico': [],
                'contexto': {},
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'message_count': 0
            }
            print(f"✅ Nova sessão criada: {conversation_id[:20]}...")
        else:
            # Atualizar última atividade
            self.sessions[conversation_id]['last_activity'] = datetime.now()
        
        return self.sessions[conversation_id]
    
    def add_message_to_session(
        self, 
        conversation_id: str, 
        role: str, 
        content: str
    ):
        """
        Adiciona mensagem ao histórico da sessão
        
        Args:
            conversation_id: ID da conversa
            role: 'user' ou 'assistant'
            content: Conteúdo da mensagem
        """
        session = self.get_or_create_session(conversation_id)
        
        session['historico'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
        
        session['message_count'] += 1
        
        # Limitar histórico (últimas 20 mensagens)
        if len(session['historico']) > 20:
            session['historico'] = session['historico'][-20:]
    
    def get_session_history(self, conversation_id: str) -> List[Dict]:
        """
        Retorna histórico da sessão
        
        Args:
            conversation_id: ID da conversa
        
        Returns:
            Lista de mensagens
        """
        session = self.get_or_create_session(conversation_id)
        return session['historico']
    
    def get_session_context(self, conversation_id: str) -> Dict:
        """
        Retorna contexto da sessão
        
        Args:
            conversation_id: ID da conversa
        
        Returns:
            Dict com contexto
        """
        session = self.get_or_create_session(conversation_id)
        return session['contexto']
    
    def update_session_context(
        self, 
        conversation_id: str, 
        key: str, 
        value: any
    ):
        """
        Atualiza contexto da sessão
        
        Args:
            conversation_id: ID da conversa
            key: Chave do contexto
            value: Valor a armazenar
        """
        session = self.get_or_create_session(conversation_id)
        session['contexto'][key] = value
    
    def clear_session(self, conversation_id: str):
        """
        Limpa sessão específica
        
        Args:
            conversation_id: ID da conversa
        """
        if conversation_id in self.sessions:
            del self.sessions[conversation_id]
            print(f"🗑️ Sessão removida: {conversation_id[:20]}...")
    
    def get_active_sessions_count(self) -> int:
        """
        Retorna número de sessões ativas
        
        Returns:
            Quantidade de sessões
        """
        return len(self.sessions)
    
    def get_session_stats(self, conversation_id: str) -> Dict:
        """
        Retorna estatísticas da sessão
        
        Args:
            conversation_id: ID da conversa
        
        Returns:
            Dict com estatísticas
        """
        if conversation_id not in self.sessions:
            return None
        
        session = self.sessions[conversation_id]
        uptime = datetime.now() - session['created_at']
        
        return {
            'messages': session['message_count'],
            'uptime_minutes': int(uptime.total_seconds() / 60),
            'last_activity': session['last_activity'].strftime('%H:%M:%S'),
            'context_keys': list(session['contexto'].keys())
        }
    
    def start_cleanup_task(self):
        """Inicia tarefa de limpeza se ainda não estiver rodando"""
        if self._cleanup_task is None:
            try:
                loop = asyncio.get_event_loop()
                self._cleanup_task = loop.create_task(self._cleanup_expired_sessions())
            except RuntimeError:
                # Sem loop de eventos ainda, limpeza manual será feita
                pass
    
    async def _cleanup_expired_sessions(self):
        """
        Tarefa em background para limpar sessões expiradas
        """
        while True:
            try:
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
                
                now = datetime.now()
                expired = []
                
                for conv_id, session in self.sessions.items():
                    last_activity = session['last_activity']
                    time_since = now - last_activity
                    
                    if time_since > timedelta(minutes=self.timeout_minutes):
                        expired.append(conv_id)
                
                for conv_id in expired:
                    print(f"⏰ Sessão expirada: {conv_id[:20]}... ({self.timeout_minutes}min inativa)")
                    self.clear_session(conv_id)
                
                if expired:
                    print(f"🗑️ {len(expired)} sessões limpas. Ativas: {self.get_active_sessions_count()}")
            
            except Exception as e:
                print(f"❌ Erro na limpeza de sessões: {e}")
    
    def get_all_sessions_info(self) -> List[Dict]:
        """
        Retorna informações de todas as sessões
        
        Returns:
            Lista com info de cada sessão
        """
        info = []
        
        for conv_id, session in self.sessions.items():
            uptime = datetime.now() - session['created_at']
            info.append({
                'conversation_id': conv_id[:30] + '...',
                'messages': session['message_count'],
                'uptime_min': int(uptime.total_seconds() / 60),
                'last_activity': session['last_activity'].strftime('%H:%M:%S')
            })
        
        return info


# Instância global (singleton)
_session_manager = None


def get_session_manager() -> SessionManager:
    """
    Retorna instância única do SessionManager
    
    Returns:
        SessionManager instance
    """
    global _session_manager
    
    if _session_manager is None:
        _session_manager = SessionManager()
        print("✅ SessionManager inicializado")
    
    return _session_manager
