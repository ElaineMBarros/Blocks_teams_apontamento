"""
🔍 SCRIPT DE VERIFICAÇÃO - CONSULTA 90 DIAS
Verifica se os dados do datalake cobrem os últimos 90 dias
"""

import pandas as pd
from datetime import datetime, timedelta
import glob

def verificar_dados_90_dias():
    """Verifica se os dados cobrem os últimos 90 dias"""
    
    print("=" * 80)
    print("🔍 VERIFICAÇÃO DE DADOS - ÚLTIMOS 90 DIAS")
    print("=" * 80 + "\n")
    
    # 1. Encontrar arquivo de dados mais recente
    arquivos = glob.glob("resultados/dados_com_duracao_*.csv")
    if not arquivos:
        print("❌ Nenhum arquivo de dados encontrado em 'resultados/'")
        print("💡 Execute o script de extração do datalake primeiro")
        return
    
    arquivo_mais_recente = max(arquivos)
    print(f"📁 Arquivo encontrado: {arquivo_mais_recente}")
    
    # 2. Carregar dados
    try:
        df = pd.read_csv(arquivo_mais_recente, encoding='utf-8-sig')
        print(f"✅ Dados carregados: {len(df)} registros\n")
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # 3. Informações básicas
    print("📊 ESTRUTURA DOS DADOS")
    print("-" * 80)
    print(f"Colunas disponíveis: {list(df.columns)}")
    print(f"\nPrimeiras 3 linhas:")
    print(df.head(3).to_string())
    print("\n")
    
    # 4. Análise de datas
    if 'd_dt_data' not in df.columns:
        print("❌ Coluna 'd_dt_data' não encontrada")
        return
    
    # Converter coluna de data
    df['data'] = pd.to_datetime(df['d_dt_data'], errors='coerce')
    
    # Remover datas inválidas
    df_valido = df[df['data'].notna()].copy()
    
    data_minima = df_valido['data'].min()
    data_maxima = df_valido['data'].max()
    total_dias = (data_maxima - data_minima).days
    
    print("📅 PERÍODO DOS DADOS")
    print("-" * 80)
    print(f"Data mais antiga: {data_minima.strftime('%d/%m/%Y')}")
    print(f"Data mais recente: {data_maxima.strftime('%d/%m/%Y')}")
    print(f"Total de dias cobertos: {total_dias} dias")
    print(f"Total de registros válidos: {len(df_valido)}\n")
    
    # 5. Verificar últimos 90 dias
    hoje = pd.Timestamp.now()
    data_90_dias_atras = hoje - timedelta(days=90)
    
    print("🎯 VERIFICAÇÃO DOS ÚLTIMOS 90 DIAS")
    print("-" * 80)
    print(f"Data atual: {hoje.strftime('%d/%m/%Y')}")
    print(f"90 dias atrás: {data_90_dias_atras.strftime('%d/%m/%Y')}")
    print(f"Data mais recente nos dados: {data_maxima.strftime('%d/%m/%Y')}")
    
    # Verificar cobertura
    dias_faltando = (hoje - data_maxima).days
    
    if data_maxima < data_90_dias_atras:
        print(f"\n❌ DADOS DESATUALIZADOS!")
        print(f"   Os dados estão {dias_faltando} dias atrasados")
        print(f"   Data mais recente deveria ser: {hoje.strftime('%d/%m/%Y')}")
        print(f"   Data mais recente encontrada: {data_maxima.strftime('%d/%m/%Y')}")
    elif dias_faltando > 7:
        print(f"\n⚠️ DADOS PARCIALMENTE DESATUALIZADOS")
        print(f"   Última atualização há {dias_faltando} dias")
        print(f"   Recomenda-se atualizar os dados")
    else:
        print(f"\n✅ DADOS ATUALIZADOS")
        print(f"   Última atualização há {dias_faltando} dia(s)")
    
    # Filtrar últimos 90 dias
    df_90_dias = df_valido[df_valido['data'] >= data_90_dias_atras].copy()
    
    print(f"\n📊 ESTATÍSTICAS DOS ÚLTIMOS 90 DIAS")
    print("-" * 80)
    print(f"Registros nos últimos 90 dias: {len(df_90_dias)}")
    
    if len(df_90_dias) > 0:
        print(f"Primeira data (90 dias): {df_90_dias['data'].min().strftime('%d/%m/%Y')}")
        print(f"Última data (90 dias): {df_90_dias['data'].max().strftime('%d/%m/%Y')}")
        print(f"Dias com dados: {df_90_dias['data'].dt.date.nunique()}")
        
        # Estatísticas adicionais
        if 'duracao_horas' in df_90_dias.columns:
            total_horas = df_90_dias['duracao_horas'].sum()
            media_horas = df_90_dias['duracao_horas'].mean()
            print(f"\nTotal de horas: {total_horas:.2f}h")
            print(f"Média por apontamento: {media_horas:.2f}h")
        
        if 's_nm_recurso' in df_90_dias.columns:
            usuarios_unicos = df_90_dias['s_nm_recurso'].nunique()
            print(f"Usuários únicos: {usuarios_unicos}")
            
            # Top 5 usuários
            print(f"\n🏆 TOP 5 USUÁRIOS (últimos 90 dias):")
            top_usuarios = df_90_dias.groupby('s_nm_recurso')['duracao_horas'].sum().nlargest(5)
            for i, (usuario, horas) in enumerate(top_usuarios.items(), 1):
                print(f"   {i}. {usuario}: {horas:.2f}h")
    else:
        print("⚠️ Nenhum registro encontrado nos últimos 90 dias")
    
    # 6. Verificar lacunas nos dados
    print(f"\n🔍 ANÁLISE DE LACUNAS NOS ÚLTIMOS 90 DIAS")
    print("-" * 80)
    
    if len(df_90_dias) > 0:
        # Criar conjunto de todas as datas esperadas
        datas_esperadas = pd.date_range(start=data_90_dias_atras, end=min(data_maxima, hoje), freq='D')
        datas_nos_dados = set(df_90_dias['data'].dt.date)
        datas_faltantes = [d.date() for d in datas_esperadas if d.date() not in datas_nos_dados]
        
        if datas_faltantes:
            print(f"⚠️ Encontradas {len(datas_faltantes)} datas sem apontamentos")
            if len(datas_faltantes) <= 10:
                print("Datas faltantes:")
                for data in datas_faltantes[:10]:
                    dia_semana = pd.Timestamp(data).day_name()
                    print(f"   • {data.strftime('%d/%m/%Y')} ({dia_semana})")
            else:
                print(f"Primeiras 10 datas faltantes:")
                for data in datas_faltantes[:10]:
                    dia_semana = pd.Timestamp(data).day_name()
                    print(f"   • {data.strftime('%d/%m/%Y')} ({dia_semana})")
                print(f"   ... e mais {len(datas_faltantes) - 10} data(s)")
        else:
            print("✅ Todos os dias têm apontamentos registrados")
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSÃO")
    print("=" * 80)
    
    if data_maxima >= data_90_dias_atras and len(df_90_dias) > 0:
        cobertura = (df_90_dias['data'].dt.date.nunique() / 90) * 100
        print(f"✅ Os dados COBREM os últimos 90 dias")
        print(f"   Cobertura: {cobertura:.1f}% dos dias")
        print(f"   Status: {'COMPLETO' if cobertura >= 80 else 'PARCIAL'}")
    else:
        print(f"❌ Os dados NÃO cobrem os últimos 90 dias completamente")
        print(f"   É necessário atualizar a extração do datalake")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    if dias_faltando > 7:
        print("   1. Execute o script de extração do datalake")
        print("   2. Verifique a query SQL para garantir filtro de 90 dias")
        print("   3. Reexecute este script para validar")
    else:
        print("   1. Dados estão atualizados ✅")
        print("   2. Sistema pronto para uso")
    
    print("\n")

if __name__ == "__main__":
    verificar_dados_90_dias()
