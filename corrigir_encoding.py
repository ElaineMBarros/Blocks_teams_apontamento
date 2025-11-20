"""
Corrige encoding do arquivo extraído via sqlcmd
"""
import pandas as pd
from datetime import datetime

# Arquivo original (Latin-1/Windows-1252)
arquivo_original = 'resultados/dados_20251117_162636.csv'

print(f"Lendo arquivo: {arquivo_original}")
print("Tentando detectar encoding correto...")

# Ler com encoding UTF-8 (como sqlcmd gera)
df = pd.read_csv(arquivo_original, encoding='utf-8', on_bad_lines='skip', low_memory=False)
print(f"Total de registros: {len(df)}")

# Salvar em UTF-8 com BOM
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
arquivo_novo = f'resultados/dados_{timestamp}_utf8.csv'

df.to_csv(arquivo_novo, index=False, encoding='utf-8-sig')
print(f"\nArquivo salvo: {arquivo_novo}")
print("Encoding: UTF-8 com BOM")

# Mostrar amostra
print("\nPrimeiras linhas:")
print(df.head(2).to_string())

print("\n✅ Conversão concluída!")
print(f"Agora 'Preparação' deve aparecer corretamente!")
