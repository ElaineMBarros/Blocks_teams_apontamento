import pandas as pd

df = pd.read_csv('resultados/dados_20251117_170227_corrigido.csv', low_memory=False)
print('TODAS as colunas:')
for i, col in enumerate(df.columns, 1):
    print(f'{i}. {col}')
