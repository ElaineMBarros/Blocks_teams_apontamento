import pandas as pd
import re
from datetime import datetime

def decupar_cargo(cargo_str):
    """
    Decupa o campo de cargo em suas partes componentes.
    Formato esperado: 7874-3-AZURE-GERENTE DE PROJETOS-NÍVEL 3
    
    Retorna um dicionário com:
    - contrato_fornecedor: 7874
    - item_contrato: 3
    - tecnologia: AZURE
    - perfil: GERENTE DE PROJETOS
    - nivel: NÍVEL 3
    """
    if pd.isna(cargo_str) or cargo_str == '':
        return {
            'contrato_fornecedor': None,
            'item_contrato': None,
            'tecnologia': None,
            'perfil': None,
            'nivel': None
        }
    
    try:
        # Padrão: XXXX-X-TECNOLOGIA-PERFIL-NÍVEL X
        # Usar regex para capturar as partes
        pattern = r'^(\d+)-(\d+)-([^-]+)-(.+)-(.+)$'
        match = re.match(pattern, cargo_str)
        
        if match:
            return {
                'contrato_fornecedor': match.group(1),
                'item_contrato': match.group(2),
                'tecnologia': match.group(3).strip(),
                'perfil': match.group(4).strip(),
                'nivel': match.group(5).strip()
            }
        else:
            # Se não casar com o padrão, tentar split simples
            partes = cargo_str.split('-')
            if len(partes) >= 5:
                return {
                    'contrato_fornecedor': partes[0].strip(),
                    'item_contrato': partes[1].strip(),
                    'tecnologia': partes[2].strip(),
                    'perfil': partes[3].strip(),
                    'nivel': partes[4].strip()
                }
            else:
                # Não conseguiu parsear
                return {
                    'contrato_fornecedor': None,
                    'item_contrato': None,
                    'tecnologia': None,
                    'perfil': None,
                    'nivel': None
                }
    except Exception as e:
        print(f"Erro ao processar cargo: {cargo_str} - {str(e)}")
        return {
            'contrato_fornecedor': None,
            'item_contrato': None,
            'tecnologia': None,
            'perfil': None,
            'nivel': None
        }

# Ler o CSV anonimizado
print("📂 Lendo arquivo CSV anonimizado...")
csv_file = 'resultados/dados_anonimizados_20251118_210225.csv'
df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

print(f"✅ Arquivo lido: {len(df)} registros")

# Criar novas colunas
print("\n🔧 Decupando campo s_ds_cargo...")
print("   - Criando colunas: contrato_fornecedor, item_contrato, tecnologia, perfil, nivel")

# Aplicar a função de decupagem
cargo_decupado = df['s_ds_cargo'].apply(decupar_cargo)

# Converter para DataFrame e adicionar as colunas
cargo_df = pd.DataFrame(cargo_decupado.tolist())

# Adicionar as novas colunas ao DataFrame original
df['contrato_fornecedor'] = cargo_df['contrato_fornecedor']
df['item_contrato'] = cargo_df['item_contrato']
df['tecnologia'] = cargo_df['tecnologia']
df['perfil'] = cargo_df['perfil']
df['nivel'] = cargo_df['nivel']

# Mostrar estatísticas
print("\n📊 Estatísticas das novas colunas:")
print(f"   - Contratos fornecedor únicos: {df['contrato_fornecedor'].nunique()}")
print(f"   - Itens de contrato únicos: {df['item_contrato'].nunique()}")
print(f"   - Tecnologias únicas: {df['tecnologia'].nunique()}")
print(f"   - Perfis únicos: {df['perfil'].nunique()}")
print(f"   - Níveis únicos: {df['nivel'].nunique()}")

# Mostrar exemplos
print("\n📋 Exemplos de cargos decupados:")
print("-" * 100)
exemplos = df[df['s_ds_cargo'].notna()][['s_ds_cargo', 'contrato_fornecedor', 'item_contrato', 
                                           'tecnologia', 'perfil', 'nivel']].head(10)
for idx, row in exemplos.iterrows():
    print(f"\nOriginal: {row['s_ds_cargo']}")
    print(f"  → Contrato Fornecedor: {row['contrato_fornecedor']}")
    print(f"  → Item Contrato: {row['item_contrato']}")
    print(f"  → Tecnologia: {row['tecnologia']}")
    print(f"  → Perfil: {row['perfil']}")
    print(f"  → Nível: {row['nivel']}")

# Salvar arquivo atualizado
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f'resultados/dados_anonimizados_decupado_{timestamp}.csv'

print(f"\n💾 Salvando arquivo com colunas decupadas...")
df.to_csv(output_file, index=False, encoding='utf-8')

# Criar relatório
print("\n📝 Criando relatório de tecnologias e perfis...")
relatorio_file = f'resultados/relatorio_cargos_{timestamp}.txt'

with open(relatorio_file, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("RELATÓRIO DE CARGOS DECUPADOS\n")
    f.write("=" * 100 + "\n\n")
    
    f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write(f"Arquivo Original: {csv_file}\n")
    f.write(f"Arquivo Gerado: {output_file}\n")
    f.write(f"Total de Registros: {len(df)}\n\n")
    
    f.write("=" * 100 + "\n")
    f.write("ESTATÍSTICAS GERAIS\n")
    f.write("=" * 100 + "\n")
    f.write(f"Contratos fornecedor únicos: {df['contrato_fornecedor'].nunique()}\n")
    f.write(f"Itens de contrato únicos: {df['item_contrato'].nunique()}\n")
    f.write(f"Tecnologias únicas: {df['tecnologia'].nunique()}\n")
    f.write(f"Perfis únicos: {df['perfil'].nunique()}\n")
    f.write(f"Níveis únicos: {df['nivel'].nunique()}\n\n")
    
    f.write("=" * 100 + "\n")
    f.write("CONTRATOS FORNECEDOR\n")
    f.write("=" * 100 + "\n")
    contratos = df['contrato_fornecedor'].value_counts()
    for contrato, count in contratos.items():
        f.write(f"{contrato}: {count} registros\n")
    
    f.write("\n" + "=" * 100 + "\n")
    f.write("TECNOLOGIAS\n")
    f.write("=" * 100 + "\n")
    tecnologias = df['tecnologia'].value_counts()
    for tec, count in tecnologias.items():
        f.write(f"{tec}: {count} registros\n")
    
    f.write("\n" + "=" * 100 + "\n")
    f.write("PERFIS\n")
    f.write("=" * 100 + "\n")
    perfis = df['perfil'].value_counts()
    for perfil, count in perfis.items():
        f.write(f"{perfil}: {count} registros\n")
    
    f.write("\n" + "=" * 100 + "\n")
    f.write("NÍVEIS\n")
    f.write("=" * 100 + "\n")
    niveis = df['nivel'].value_counts()
    for nivel, count in niveis.items():
        f.write(f"{nivel}: {count} registros\n")

print("\n" + "=" * 100)
print("✅ DECUPAGEM CONCLUÍDA COM SUCESSO!")
print("=" * 100)
print(f"\n📁 Arquivos gerados:")
print(f"   1. CSV com cargos decupados: {output_file}")
print(f"   2. Relatório de análise: {relatorio_file}")
print(f"\n📊 Novas colunas adicionadas:")
print(f"   - contrato_fornecedor")
print(f"   - item_contrato")
print(f"   - tecnologia")
print(f"   - perfil")
print(f"   - nivel")
print("=" * 100)
