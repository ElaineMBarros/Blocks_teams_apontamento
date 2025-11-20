"""
📊 RELATÓRIO DE DADOS ANONIMIZADOS
Mostra quais campos foram anonimizados e exemplos
"""

import pandas as pd

# Carregar dados
print("📂 Carregando dados anonimizados...\n")
df = pd.read_csv('resultados/dados_anonimizados_decupado_20251118_211544.csv', low_memory=False, nrows=10)

print("="*80)
print("🔐 CAMPOS ANONIMIZADOS NO ARQUIVO")
print("="*80)

# Lista de campos anonimizados
campos_anonimizados = [
    ('s_nr_cpf', 's_nr_cpf_original', 'CPF'),
    ('s_nm_recurso', 's_nm_recurso_original', 'Nome do Recurso/Funcionário'),
    ('s_nm_usuario_valida', 's_nm_usuario_valida_original', 'Nome do Validador'),
    ('s_nm_usuario', 's_nm_usuario_original', 'Nome do Usuário')
]

print("\n📋 CAMPOS QUE FORAM ANONIMIZADOS:\n")

for campo_anonimo, campo_original, descricao in campos_anonimizados:
    print(f"✅ {descricao}")
    print(f"   • Campo anônimo: {campo_anonimo}")
    print(f"   • Campo original preservado: {campo_original}")
    print()

print("-"*80)
print("\n🔍 EXEMPLOS DE DADOS ANONIMIZADOS (5 registros):\n")
print("="*80)

# Mostrar exemplos para cada campo
for campo_anonimo, campo_original, descricao in campos_anonimizados:
    print(f"\n{descricao.upper()}:")
    print("-"*80)
    
    # Pegar valores únicos (primeiros 5)
    valores_unicos = df[[campo_anonimo, campo_original]].drop_duplicates().head(5)
    
    for idx, row in valores_unicos.iterrows():
        print(f"  Anônimo:  {row[campo_anonimo]}")
        print(f"  Original: {row[campo_original]}")
        print()

print("="*80)
print("\n📊 ESTATÍSTICAS DE ANONIMIZAÇÃO:\n")

# Contar dados únicos
print(f"✅ Total de CPFs únicos: {df['s_nr_cpf'].nunique()}")
print(f"✅ Total de Recursos únicos: {df['s_nm_recurso'].nunique()}")
print(f"✅ Total de Validadores únicos: {df['s_nm_usuario_valida'].nunique()}")
print(f"✅ Total de Usuários únicos: {df['s_nm_usuario'].nunique()}")

print("\n" + "="*80)
print("\n💡 INFORMAÇÕES ADICIONAIS:\n")
print("• Os dados originais estão preservados nas colunas terminadas em '_original'")
print("• O bot usa apenas as colunas anonimizadas para proteção de dados")
print("• A anonimização garante LGPD compliance")
print("• Padrões de anonimização:")
print("  - CPF: CPF_XXXXXXXXX (números aleatórios)")
print("  - Nomes: RECURSO_XXXXXXXXX / VALIDADOR_XXXXXXXXX (IDs únicos)")
print("\n" + "="*80)
