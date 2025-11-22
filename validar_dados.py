import pandas as pd

# Carregar dados
df = pd.read_csv('resultados/dados_anonimizados_decupado_20251118_211544.csv', 
                 encoding='utf-8-sig', low_memory=False)

# Processar datas
df['data'] = pd.to_datetime(df['d_dt_data'], errors='coerce')
df['d_dt_inicio'] = pd.to_datetime(df['d_dt_inicio_apontamento'], errors='coerce')
df['d_dt_fim'] = pd.to_datetime(df['d_dt_fim_apontamento'], errors='coerce')
df['duracao_horas'] = (df['d_dt_fim'] - df['d_dt_inicio']).dt.total_seconds() / 3600

# Filtrar período 20/09 a 20/10/2025
inicio = pd.to_datetime('2025-09-20')
fim = pd.to_datetime('2025-10-20')
df_periodo = df[(df['data'] >= inicio) & (df['data'] <= fim)].copy()

print(f"\n📅 VALIDAÇÃO - Período: 20/09/2025 a 20/10/2025")
print(f"=" * 60)

# Estatísticas gerais
print(f"\n🔍 ESTATÍSTICAS GERAIS:")
print(f"Total de apontamentos: {len(df_periodo):,}")
print(f"Total de horas (soma de todos): {df_periodo['duracao_horas'].sum():,.2f}h")
print(f"Dias corridos: {(fim - inicio).days + 1}")
print(f"Dias únicos com apontamento: {df_periodo['data'].nunique()}")
print(f"Recursos únicos: {df_periodo['s_nm_recurso'].nunique()}")

# Média correta
dias_corridos = (fim - inicio).days + 1
media_por_dia_corrido = df_periodo['duracao_horas'].sum() / dias_corridos
print(f"\n📊 MÉDIA CORRETA:")
print(f"Total horas / Dias corridos = {df_periodo['duracao_horas'].sum():,.2f}h / {dias_corridos} = {media_por_dia_corrido:,.2f}h/dia")

# Validar RECURSO_62702985
print(f"\n👤 VALIDAÇÃO - RECURSO_62702985:")
print(f"=" * 60)
df_recurso = df_periodo[df_periodo['s_nm_recurso'] == 'RECURSO_62702985']
print(f"Total horas: {df_recurso['duracao_horas'].sum():.2f}h")
print(f"Número de apontamentos: {len(df_recurso)}")
print(f"Dias únicos: {df_recurso['data'].nunique()}")
print(f"Média por dia: {df_recurso['duracao_horas'].sum() / df_recurso['data'].nunique():.2f}h/dia")

# Top 5
print(f"\n🏆 TOP 5 RECURSOS NO PERÍODO:")
print(f"=" * 60)
top5 = df_periodo.groupby('s_nm_recurso')['duracao_horas'].sum().nlargest(5)
for i, (recurso, horas) in enumerate(top5.items(), 1):
    apontamentos = len(df_periodo[df_periodo['s_nm_recurso'] == recurso])
    print(f"{i}. {recurso}: {horas:.2f}h ({apontamentos} apontamentos)")
