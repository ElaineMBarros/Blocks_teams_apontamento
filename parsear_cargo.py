"""
Script para parsear o campo s_ds_cargo e criar colunas separadas
Padrão: 7689-3-GP/PRO/RPA-ANALISTA DE PROCESSOS-NÍVEL 2
Onde:
- 7689 = codigo_contrato_cargo
- 3 = nivel_numero
- GP/PRO/RPA = tecnologia_cargo
- ANALISTA DE PROCESSOS = cargo_funcao
- NÍVEL 2 = nivel_descricao
"""

import pandas as pd
import re
from datetime import datetime

def parsear_cargo(cargo_str):
    """
    Parseia o campo s_ds_cargo
    Retorna dict com as partes separadas
    """
    if pd.isna(cargo_str) or cargo_str == '':
        return {
            'codigo_contrato_cargo': None,
            'nivel_numero': None,
            'tecnologia_cargo': None,
            'cargo_funcao': None,
            'nivel_descricao': None
        }
    
    try:
        # Padrão: XXXX-Y-TECNOLOGIA-CARGO-NÍVEL Z
        # Exemplo: 7689-3-GP/PRO/RPA-ANALISTA DE PROCESSOS-NÍVEL 2
        partes = str(cargo_str).split('-')
        
        if len(partes) >= 3:
            codigo = partes[0].strip()
            nivel_num = partes[1].strip()
            
            # O resto precisa ser reconstruído pois pode ter mais "-"
            resto = '-'.join(partes[2:])
            
            # Tentar separar tecnologia do cargo
            # Procurar por "NÍVEL" para saber onde o cargo termina
            if 'NÍVEL' in resto.upper():
                idx_nivel = resto.upper().rfind('NÍVEL')
                antes_nivel = resto[:idx_nivel].strip().rstrip('-').strip()
                nivel_desc = resto[idx_nivel:].strip()
                
                # Separar tecnologia e cargo
                partes_antes = antes_nivel.split('-', 1)
                if len(partes_antes) == 2:
                    tecnologia = partes_antes[0].strip()
                    cargo_func = partes_antes[1].strip()
                else:
                    tecnologia = None
                    cargo_func = antes_nivel
            else:
                # Sem nível no texto
                partes_antes = resto.split('-', 1)
                if len(partes_antes) == 2:
                    tecnologia = partes_antes[0].strip()
                    cargo_func = partes_antes[1].strip()
                else:
                    tecnologia = None
                    cargo_func = resto
                nivel_desc = None
            
            return {
                'codigo_contrato_cargo': codigo,
                'nivel_numero': nivel_num,
                'tecnologia_cargo': tecnologia,
                'cargo_funcao': cargo_func,
                'nivel_descricao': nivel_desc
            }
        else:
            # Formato diferente, apenas guardar como está
            return {
                'codigo_contrato_cargo': None,
                'nivel_numero': None,
                'tecnologia_cargo': None,
                'cargo_funcao': cargo_str,
                'nivel_descricao': None
            }
    except:
        return {
            'codigo_contrato_cargo': None,
            'nivel_numero': None,
            'tecnologia_cargo': None,
            'cargo_funcao': cargo_str,
            'nivel_descricao': None
        }

# Carregar dados
print("📁 Carregando dados...")
df = pd.read_csv('resultados/dados_anonimizados_decupado_20251118_211544.csv', encoding='utf-8-sig', low_memory=False)

print(f"✅ {len(df)} registros carregados")
print("\n🔍 Exemplo de s_ds_cargo:")
print(df['s_ds_cargo'].head(10).tolist())

# Parsear campo s_ds_cargo
print("\n⚙️ Parseando campo s_ds_cargo...")
cargos_parseados = df['s_ds_cargo'].apply(parsear_cargo)

# Adicionar novas colunas
df['codigo_contrato_cargo'] = [c['codigo_contrato_cargo'] for c in cargos_parseados]
df['nivel_numero'] = [c['nivel_numero'] for c in cargos_parseados]
df['tecnologia_cargo'] = [c['tecnologia_cargo'] for c in cargos_parseados]
df['cargo_funcao'] = [c['cargo_funcao'] for c in cargos_parseados]
df['nivel_descricao'] = [c['nivel_descricao'] for c in cargos_parseados]

# Mostrar exemplos
print("\n📊 Exemplos de dados parseados:")
print(df[['s_ds_cargo', 'codigo_contrato_cargo', 'nivel_numero', 'tecnologia_cargo', 'cargo_funcao', 'nivel_descricao']].head(20).to_string())

# Salvar
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'resultados/dados_parseados_{timestamp}.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✅ Arquivo salvo: {output_file}")
print(f"📊 Total de registros: {len(df)}")
print("\n🔍 Estatísticas:")
print(f"- Códigos de contrato únicos: {df['codigo_contrato_cargo'].nunique()}")
print(f"- Níveis únicos: {df['nivel_numero'].nunique()}")
print(f"- Tecnologias únicas: {df['tecnologia_cargo'].nunique()}")
print(f"- Cargos únicos: {df['cargo_funcao'].nunique()}")
