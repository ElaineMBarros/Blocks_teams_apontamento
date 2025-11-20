import pandas as pd

df = pd.read_csv('resultados/dados_anonimizados_decupado_20251118_211544.csv')
print(f'Total: {len(df)} registros')
print(f'\nTem duracao_horas? {"duracao_horas" in df.columns}')
print(f'\nColunas com hora/data:')
for col in df.columns:
    if 'hora' in col.lower() or 'dt' in col.lower():
        print(f'  - {col}')
