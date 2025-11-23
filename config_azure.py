"""
Configuração para carregar connection string diretamente no código
Este arquivo tenta múltiplas fontes em ordem de prioridade
"""
import os
import base64

print("🔍 DEBUG config_azure.py - Buscando connection string...", flush=True)

# Connection string do Azure Blob Storage
# Tenta múltiplas variáveis possíveis
AZURE_STORAGE_CONNECTION_STRING = (
    os.getenv('RAILWAY_AZURE_CONNECTION_STRING') or
    os.getenv('AZURE_CONN_STR') or
    os.getenv('AZURE_STORAGE_CONNECTION_STRING') or
    ''
)

# Se ainda não achou, tentar versão Base64
if not AZURE_STORAGE_CONNECTION_STRING:
    b64_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING_B64', '')
    if b64_str:
        try:
            AZURE_STORAGE_CONNECTION_STRING = base64.b64decode(b64_str).decode('utf-8')
            print("✅ Connection string decodificada de Base64", flush=True)
        except Exception as e:
            print(f"❌ Erro ao decodificar Base64: {e}", flush=True)

if AZURE_STORAGE_CONNECTION_STRING:
    print(f"✅ Connection string encontrada (len={len(AZURE_STORAGE_CONNECTION_STRING)})", flush=True)
else:
    print("⚠️ Nenhuma connection string encontrada", flush=True)

BLOB_CONTAINER_NAME = "dados"
BLOB_FILE_NAME = "dados_anonimizados_decupado_20251118_211544.csv"
