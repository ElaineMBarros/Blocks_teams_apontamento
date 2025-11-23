"""
Configuração para carregar connection string diretamente no código
para contornar problema de variáveis de ambiente no Railway
"""

# Connection string do Azure Blob Storage
# Em produção no Railway, esta será a única forma de configurar
AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=dadosaplicacoes;AccountKey=rZv+bkceFe4+99IJcaSdk0ri0yL31YYFubfnYPpje6qLgYNdRjXrJhGHWBYW4uvacxQiNaW91DtX+AStz4zxyA==;EndpointSuffix=core.windows.net"

BLOB_CONTAINER_NAME = "dados"
BLOB_FILE_NAME = "dados_anonimizados_decupado_20251118_211544.csv"
