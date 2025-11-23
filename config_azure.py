"""
Configuração para carregar connection string diretamente no código
Este arquivo será gerado dinamicamente no Railway usando variáveis de ambiente
"""
import os

# Connection string do Azure Blob Storage
# Será lida de variável de ambiente no Railway
AZURE_STORAGE_CONNECTION_STRING = os.getenv('RAILWAY_AZURE_CONNECTION_STRING', '')

BLOB_CONTAINER_NAME = "dados"
BLOB_FILE_NAME = "dados_anonimizados_decupado_20251118_211544.csv"
