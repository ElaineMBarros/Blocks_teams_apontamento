"""
Configuração para carregar connection string diretamente no código
Este arquivo será gerado dinamicamente no Railway usando variáveis de ambiente
"""
import os

# DEBUG: Mostrar TODAS as variáveis disponíveis
print("🔍 DEBUG config_azure.py - Total de variáveis:", len(os.environ), flush=True)
print("🔍 Procurando por RAILWAY_, AZURE_, STORAGE_, CONNECTION_:", flush=True)
for key in sorted(os.environ.keys()):
    if any(palavra in key.upper() for palavra in ['RAILWAY', 'AZURE', 'STORAGE', 'CONNECTION', 'TESTE']):
        valor = os.environ[key]
        print(f"   {key} = {valor[:50]}..." if len(valor) > 50 else f"   {key} = {valor}", flush=True)

# Connection string do Azure Blob Storage
# Será lida de variável de ambiente no Railway
AZURE_STORAGE_CONNECTION_STRING = os.getenv('RAILWAY_AZURE_CONNECTION_STRING', '')

BLOB_CONTAINER_NAME = "dados"
BLOB_FILE_NAME = "dados_anonimizados_decupado_20251118_211544.csv"
