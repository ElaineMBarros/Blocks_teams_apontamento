import pandas as pd

# Ler o arquivo
df = pd.read_csv('resultados/dados_20251117_170227_corrigido.csv', low_memory=False)

# Converter para datetime
df['d_dt_data'] = pd.to_datetime(df['d_dt_data'])

# Calcular estatísticas
data_min = df['d_dt_data'].min()
data_max = df['d_dt_data'].max()
periodo_dias = (data_max - data_min).days
total_registros = len(df)

print("=" * 80)
print("ANÁLISE DO PERÍODO DE DADOS")
print("=" * 80)
print(f"\n📅 Data mais antiga: {data_min.strftime('%d/%m/%Y')}")
print(f"📅 Data mais recente: {data_max.strftime('%d/%m/%Y')}")
print(f"⏱️  Período total: {periodo_dias} dias")
print(f"📊 Total de registros: {total_registros:,}")
print(f"\n✅ Este arquivo {'contém' if periodo_dias <= 90 else 'NÃO contém apenas'} aproximadamente 90 dias de dados")

if periodo_dias <= 90:
    print(f"   (Contém {periodo_dias} dias de apontamentos)")
else:
    print(f"   (Contém {periodo_dias} dias de apontamentos - mais de 90 dias)")

print("=" * 80)
