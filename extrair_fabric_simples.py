"""
Extração simples do Microsoft Fabric usando Token
"""
import pyodbc
import pandas as pd
import subprocess
import json
from datetime import datetime

# Configurações
SERVER = "zwyhqouopquuta6vdefgzqatmu-4wt3acgsbsneboaodwlmudpbwu.datawarehouse.fabric.microsoft.com"
DATABASE = "DW_Portal_Apontamento"

# Query: últimos 90 dias
QUERY = """
SELECT TOP 1000 *
FROM dbo.gold_999_portal_outsourcing_apontamento_ultimos_90_dias
WHERE d_dt_data >= DATEADD(DAY, -90, GETDATE())
ORDER BY d_dt_data DESC
"""

print("🔑 Obtendo token...")
token_cmd = ["az", "account", "get-access-token", "--resource", "https://database.windows.net"]
token_raw = subprocess.check_output(token_cmd, shell=True)
token = json.loads(token_raw)["accessToken"]
print("✅ Token obtido!")

print("\n🔗 Conectando ao Fabric...")
conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={SERVER};Database={DATABASE};Encrypt=yes;TrustServerCertificate=no;"

try:
    token_bytes = bytes(token, "utf-16-le")
    conn = pyodbc.connect(conn_str, attrs_before={1256: token_bytes})
    print("✅ Conectado!")
    
    print("\n📥 Executando query...")
    df = pd.read_sql(QUERY, conn)
    print(f"✅ {len(df)} registros extraídos!")
    
    # Salvar
    filename = f'resultados/dados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n💾 Salvo: {filename}")
    
    # Info básica
    if len(df) > 0 and 'd_dt_data' in df.columns:
        print(f"\n📊 Período: {df['d_dt_data'].min()} a {df['d_dt_data'].max()}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n💡 Verifique se:")
    print("   - Você tem permissões no Data Warehouse")
    print("   - A tabela existe")
