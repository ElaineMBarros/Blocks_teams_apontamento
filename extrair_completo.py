"""
Extração completa dos últimos 90 dias - UTF-8 correto
"""
import subprocess
import pyodbc
import pandas as pd
import json
from datetime import datetime

SERVER = "zwyhqouopquuta6vdefgzqatmu-4wt3acgsbsneboaodwlmudpbwu.datawarehouse.fabric.microsoft.com"
DATABASE = "DW_Portal_Apontamento"

QUERY = """
SELECT * 
FROM dbo.gold_999_portal_outsourcing_apontamento_ultimos_90_dias 
WHERE d_dt_data >= DATEADD(DAY, -90, GETDATE())
ORDER BY d_dt_data DESC
"""

print("Obtendo token...")
token_cmd = ["az", "account", "get-access-token", "--resource", "https://database.windows.net"]
token_raw = subprocess.check_output(token_cmd, shell=True)
token = json.loads(token_raw)["accessToken"]
print("Token obtido!")

print("Conectando ao Fabric...")
conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={SERVER};Database={DATABASE};Encrypt=yes;TrustServerCertificate=no;"

try:
    token_bytes = bytes(token, "utf-16-le")
    conn = pyodbc.connect(conn_str, attrs_before={1256: token_bytes})
    print("Conectado!")
    
    print("Executando query...")
    df = pd.read_sql(QUERY, conn)
    print(f"Extraídos: {len(df)} registros")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'resultados/dados_{timestamp}.csv'
    
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\nSalvo: {filename}")
    print(f"Encoding: UTF-8 com BOM")
    
    if 'd_dt_data' in df.columns:
        print(f"Período: {df['d_dt_data'].min()} a {df['d_dt_data'].max()}")
    
    conn.close()
    print("\nConcluído!")
    
except Exception as e:
    print(f"Erro: {e}")
