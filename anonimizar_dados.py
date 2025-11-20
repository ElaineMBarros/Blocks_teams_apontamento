import pandas as pd
import hashlib
from datetime import datetime

def gerar_cpf_anonimo(cpf_original):
    """Gera um CPF anonimizado baseado no hash do original"""
    if pd.isna(cpf_original):
        return None
    
    # Usar hash para garantir consistência
    hash_obj = hashlib.md5(str(cpf_original).encode())
    hash_hex = hash_obj.hexdigest()
    
    # Gerar CPF fictício a partir do hash
    numeros = ''.join(filter(str.isdigit, hash_hex[:11]))
    if len(numeros) < 11:
        numeros = (numeros + '00000000000')[:11]
    
    # Formatar como CPF
    cpf_anonimo = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:11]}"
    return cpf_anonimo

def gerar_nome_anonimo(nome_original, tipo='RECURSO'):
    """Gera um nome anonimizado baseado no hash do original"""
    if pd.isna(nome_original) or nome_original == '':
        return nome_original
    
    # Usar hash para garantir consistência
    hash_obj = hashlib.md5(str(nome_original).encode())
    hash_num = int(hash_obj.hexdigest()[:8], 16)
    
    # Gerar nome fictício
    nome_anonimo = f"{tipo}_{hash_num:08d}"
    return nome_anonimo

# Ler o CSV corrigido
print("📂 Lendo arquivo CSV...")
csv_file = 'resultados/dados_20251117_170227_corrigido.csv'
df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

print(f"✅ Arquivo lido: {len(df)} registros")
print(f"📊 Colunas: {len(df.columns)}")

# Criar dicionários para manter consistência na anonimização
cpf_map = {}
recurso_map = {}
validador_map = {}
usuario_map = {}

print("\n🔐 Anonimizando dados...")

# Anonimizar CPF
print("   - Anonimizando s_nr_cpf...")
df['s_nr_cpf_original'] = df['s_nr_cpf']  # Manter cópia para referência
for idx, cpf in df['s_nr_cpf'].items():
    if pd.notna(cpf):
        if cpf not in cpf_map:
            cpf_map[cpf] = gerar_cpf_anonimo(cpf)
        df.at[idx, 's_nr_cpf'] = cpf_map[cpf]

# Anonimizar nome do recurso
print("   - Anonimizando s_nm_recurso...")
df['s_nm_recurso_original'] = df['s_nm_recurso']  # Manter cópia para referência
for idx, nome in df['s_nm_recurso'].items():
    if pd.notna(nome) and nome != '':
        if nome not in recurso_map:
            recurso_map[nome] = gerar_nome_anonimo(nome, 'RECURSO')
        df.at[idx, 's_nm_recurso'] = recurso_map[nome]

# Anonimizar nome do usuário validador
print("   - Anonimizando s_nm_usuario_valida...")
df['s_nm_usuario_valida_original'] = df['s_nm_usuario_valida']  # Manter cópia para referência
for idx, nome in df['s_nm_usuario_valida'].items():
    if pd.notna(nome) and nome != '':
        if nome not in validador_map:
            validador_map[nome] = gerar_nome_anonimo(nome, 'VALIDADOR')
        df.at[idx, 's_nm_usuario_valida'] = validador_map[nome]

# Anonimizar nome do usuário
print("   - Anonimizando s_nm_usuario...")
df['s_nm_usuario_original'] = df['s_nm_usuario']  # Manter cópia para referência
for idx, nome in df['s_nm_usuario'].items():
    if pd.notna(nome) and nome != '':
        if nome not in usuario_map:
            usuario_map[nome] = gerar_nome_anonimo(nome, 'USUARIO')
        df.at[idx, 's_nm_usuario'] = usuario_map[nome]

# Salvar arquivo anonimizado
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f'resultados/dados_anonimizados_{timestamp}.csv'

print(f"\n💾 Salvando arquivo anonimizado...")
df.to_csv(output_file, index=False, encoding='utf-8')

# Criar arquivo de mapeamento (DE-PARA) para referência
mapping_file = f'resultados/mapeamento_anonimizacao_{timestamp}.txt'
print(f"📋 Criando arquivo de mapeamento...")

with open(mapping_file, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("MAPEAMENTO DE ANONIMIZAÇÃO - DE/PARA\n")
    f.write("=" * 100 + "\n\n")
    
    f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write(f"Arquivo Original: {csv_file}\n")
    f.write(f"Arquivo Anonimizado: {output_file}\n")
    f.write(f"Total de Registros: {len(df)}\n\n")
    
    f.write("=" * 100 + "\n")
    f.write("CAMPOS ANONIMIZADOS:\n")
    f.write("=" * 100 + "\n")
    f.write("- s_nr_cpf (CPF)\n")
    f.write("- s_nm_recurso (Nome do Recurso)\n")
    f.write("- s_nm_usuario_valida (Nome do Usuário Validador)\n")
    f.write("- s_nm_usuario (Nome do Usuário)\n\n")
    
    f.write("=" * 100 + "\n")
    f.write("MAPEAMENTO DE CPFs\n")
    f.write("=" * 100 + "\n")
    f.write(f"Total de CPFs únicos: {len(cpf_map)}\n\n")
    for original, anonimo in sorted(cpf_map.items()):
        f.write(f"{original} → {anonimo}\n")
    
    f.write("\n" + "=" * 100 + "\n")
    f.write("MAPEAMENTO DE RECURSOS (Funcionários)\n")
    f.write("=" * 100 + "\n")
    f.write(f"Total de recursos únicos: {len(recurso_map)}\n\n")
    for original, anonimo in sorted(recurso_map.items()):
        f.write(f"{original} → {anonimo}\n")
    
    f.write("\n" + "=" * 100 + "\n")
    f.write("MAPEAMENTO DE VALIDADORES\n")
    f.write("=" * 100 + "\n")
    f.write(f"Total de validadores únicos: {len(validador_map)}\n\n")
    for original, anonimo in sorted(validador_map.items()):
        f.write(f"{original} → {anonimo}\n")
    
    f.write("\n" + "=" * 100 + "\n")
    f.write("MAPEAMENTO DE USUÁRIOS\n")
    f.write("=" * 100 + "\n")
    f.write(f"Total de usuários únicos: {len(usuario_map)}\n\n")
    for original, anonimo in sorted(usuario_map.items()):
        f.write(f"{original} → {anonimo}\n")

print("\n" + "=" * 100)
print("✅ ANONIMIZAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 100)
print(f"\n📁 Arquivos gerados:")
print(f"   1. CSV Anonimizado: {output_file}")
print(f"   2. Mapeamento DE/PARA: {mapping_file}")
print(f"\n📊 Estatísticas:")
print(f"   - Total de registros: {len(df)}")
print(f"   - CPFs únicos anonimizados: {len(cpf_map)}")
print(f"   - Recursos únicos anonimizados: {len(recurso_map)}")
print(f"   - Validadores únicos anonimizados: {len(validador_map)}")
print(f"   - Usuários únicos anonimizados: {len(usuario_map)}")
print("\n💡 IMPORTANTE: Guarde o arquivo de mapeamento em local seguro!")
print("=" * 100)
