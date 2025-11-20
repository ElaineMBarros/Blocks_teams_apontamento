"""
Aplica transformação para corrigir encoding nos dados extraídos
"""
import pandas as pd
from datetime import datetime
import ftfy  # biblioteca para corrigir encoding

arquivo_original = 'resultados/dados_20251117_162636.csv'

print(f"📂 Lendo arquivo: {arquivo_original}")

# Ler arquivo
df = pd.read_csv(arquivo_original, encoding='utf-8', on_bad_lines='skip', low_memory=False)
print(f"✅ Total de registros: {len(df)}")

# Remover linhas de separador
df = df[df.iloc[:, 0].astype(str) != '----------------']
print(f"✅ Após limpeza: {len(df)} registros")

# Colunas de texto para corrigir
colunas_texto = ['s_ds_operacao', 's_nm_recurso', 's_ds_cargo', 's_ds_tipo_jornada', 
                  's_ds_divisao', 's_nm_sigla', 's_nm_cliente_operacional', 
                  's_nm_usuario', 's_nm_usuario_valida']

print("\n🔧 Corrigindo encoding...")

def corrigir_texto(texto):
    """Corrige problemas de encoding duplo"""
    if pd.isna(texto) or texto == 'NULL':
        return texto
    try:
        # ftfy corrige encoding duplo automaticamente
        return ftfy.fix_text(str(texto))
    except:
        return texto

# Aplicar correção apenas nas colunas de texto que existem
for col in colunas_texto:
    if col in df.columns:
        print(f"  → Corrigindo coluna: {col}")
        df[col] = df[col].apply(corrigir_texto)

# Salvar arquivo corrigido
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
arquivo_final = f'resultados/dados_{timestamp}_corrigido.csv'

df.to_csv(arquivo_final, index=False, encoding='utf-8-sig')

print(f"\n💾 Arquivo salvo: {arquivo_final}")
print(f"📊 Total de registros: {len(df)}")
print(f"🎯 Encoding: UTF-8 com BOM")

# Mostrar amostra corrigida
print("\n📋 Amostra dos dados corrigidos:")
if 's_ds_operacao' in df.columns:
    print("\nOperações únicas (primeiras 5):")
    print(df['s_ds_operacao'].dropna().unique()[:5])

if 's_nm_recurso' in df.columns:
    print("\nRecursos únicos (primeiros 5):")
    print(df['s_nm_recurso'].dropna().unique()[:5])

print("\n✅ Transformação concluída!")
print("Agora 'Educação' deve aparecer corretamente!")
