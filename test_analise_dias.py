"""
Teste da análise de apontamentos por dia
Verifica: dias úteis, validação e almoço
"""

import pandas as pd
from datetime import datetime

# Carregar dados
df = pd.read_csv('resultados/dados_anonimizados_decupado_20251118_211544.csv', low_memory=False, nrows=1000)

# Calcular duracao_horas (f_hr_hora_inicio já contém a duração!)
df['duracao_horas'] = df['f_hr_hora_inicio'].fillna(8.0)

# Converter data
df['data'] = pd.to_datetime(df['d_dt_data'])
df['dia_semana'] = df['data'].dt.dayofweek
df['eh_util'] = df['dia_semana'] < 5

# Agrupar por data e recurso
analise = df.groupby(['data', 's_nm_recurso']).agg({
    'duracao_horas': 'sum',
    'b_fl_validado': 'sum',
    's_id_apontamento': 'count'
}).reset_index()

analise.columns = ['data', 'recurso', 'total_horas', 'validados', 'qtd_apontamentos']

# Adicionar informações
analise['dia_semana'] = pd.to_datetime(analise['data']).dt.dayofweek
analise['eh_util'] = analise['dia_semana'] < 5
analise['tipo_dia'] = analise['eh_util'].map({True: '📅 Dia Útil', False: '🏖️ Fim de Semana'})
analise['tem_almoco'] = analise['total_horas'] >= 9.0
analise['todos_validados'] = analise['validados'] == analise['qtd_apontamentos']

print("="*80)
print("📊 ANÁLISE DE APONTAMENTOS POR DIA")
print("="*80)
print(f"\nTotal de dias analisados: {len(analise)}")
print(f"Dias úteis: {analise['eh_util'].sum()}")
print(f"Fins de semana: {(~analise['eh_util']).sum()}")
print(f"\n🍽️ Dias com almoço (>= 9h): {analise['tem_almoco'].sum()}")
print(f"✅ Dias totalmente validados: {analise['todos_validados'].sum()}")

print("\n" + "="*80)
print("📋 EXEMPLOS DE DIAS (5 primeiros):")
print("="*80)

for idx, row in analise.head(5).iterrows():
    print(f"\n📅 {row['data'].date()} - {row['tipo_dia']}")
    print(f"   👤 Recurso: {row['recurso']}")
    print(f"   ⏱️  Horas: {row['total_horas']:.2f}h")
    print(f"   📝 Apontamentos: {int(row['qtd_apontamentos'])}")
    print(f"   🍽️  Almoço: {'✅ Sim' if row['tem_almoco'] else '❌ Não'}")
    print(f"   ✅ Validação: {'✅ Todos validados' if row['todos_validados'] else f'⏳ {int(row['validados'])}/{int(row['qtd_apontamentos'])} validados'}")

print("\n" + "="*80)
