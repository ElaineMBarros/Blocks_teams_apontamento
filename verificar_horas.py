import pandas as pd

df = pd.read_csv('resultados/dados_anonimizados_decupado_20251118_211544.csv', low_memory=False, nrows=5)
print("Colunas de horas:")
print(df[['f_hr_hora_inicio', 'f_hr_hora_fim']].head())
print("\nTipos:")
print(df[['f_hr_hora_inicio', 'f_hr_hora_fim']].dtypes)
