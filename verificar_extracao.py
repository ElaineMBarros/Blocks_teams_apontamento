import pandas as pd
from datetime import datetime, timedelta

arquivo = 'resultados/dados_20251117_162504.csv'

df = pd.read_csv(arquivo, encoding='utf-8', on_bad_lines='skip')
print(f"✅ Total de registros: {len(df)}")

if 'd_dt_data' in df.columns:
    df['data'] = pd.to_datetime(df['d_dt_data'], errors='coerce')
    df_valido = df[df['data'].notna()]
    
    print(f"📅 Data mínima: {df_valido['data'].min()}")
    print(f"📅 Data máxima: {df_valido['data'].max()}")
    print(f"📊 Dias com dados: {df_valido['data'].dt.date.nunique()}")
    
    # Verificar 90 dias
    hoje = pd.Timestamp.now()
    data_90_dias = hoje - timedelta(days=90)
    print(f"\n🎯 90 dias atrás: {data_90_dias.date()}")
    print(f"🎯 Hoje: {hoje.date()}")
    
    if df_valido['data'].max() >= data_90_dias:
        print("\n✅ Dados COBREM os últimos 90 dias!")
    else:
        print("\n❌ Dados NÃO cobrem os últimos 90 dias")
