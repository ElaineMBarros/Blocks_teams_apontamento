"""
Configurações do Bot
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class Config:
    """Configurações da aplicação"""
    
    # Azure Bot Service
    BOT_APP_ID = os.getenv("BOT_APP_ID", "")
    BOT_APP_PASSWORD = os.getenv("BOT_APP_PASSWORD", "")
    BOT_TENANT_ID = os.getenv("BOT_TENANT_ID", "")
    
    # Microsoft Fabric
    FABRIC_ENDPOINT = os.getenv("FABRIC_ENDPOINT", "")
    FABRIC_DATABASE = os.getenv("FABRIC_DATABASE", "")
    
    # Azure AD
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
    
    # Application
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Bot Info
    BOT_NAME = os.getenv("BOT_NAME", "Agente Apontamentos")
    BOT_DESCRIPTION = os.getenv("BOT_DESCRIPTION", "Bot para consultar dados de apontamentos")
    
    # Cache (Redis)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "https://teams.microsoft.com,https://*.teams.microsoft.com"
    ).split(",")
    
    @classmethod
    def validate(cls):
        """Valida configurações obrigatórias"""
        required = []
        
        if not cls.BOT_APP_ID:
            required.append("BOT_APP_ID")
        if not cls.BOT_APP_PASSWORD:
            required.append("BOT_APP_PASSWORD")
        if not cls.BOT_TENANT_ID:
            required.append("BOT_TENANT_ID (necessário para Single Tenant)")
        
        if required:
            raise ValueError(f"Configurações obrigatórias faltando: {', '.join(required)}")
        
        return True


# Instância global de configuração
config = Config()
