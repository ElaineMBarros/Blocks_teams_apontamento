"""
📊 EXTRAÇÃO DE DADOS DO DATALAKE - VIA TOKEN (REST API)
Script alternativo usando REST API do Microsoft Fabric
Tabela: gold_999_portal_outsourcing_apontamento_ultimos_90_dias
"""

import requests
import pandas as pd
import subprocess
import json
import os
from datetime import datetime
from io import StringIO

# ============================================================
# ⚙️ CONFIGURAÇÕES DE CONEXÃO
# ============================================================
SERVER = "zwyhqouopquuta6vdefgzqatmu-4wt3acgsbsneboaodwlmudpbwu.datawarehouse.fabric.microsoft.com"
DATABASE = "DW_Portal_Apontamento"
TABLE = "dbo.gold_999_portal_outsourcing_apontamento_ultimos_90_dias"

# Query SQL para extrair dados dos últimos 90 dias
QUERY = f"""
SELECT 
    s_id_apontamento,
    s_ds_operacao,
    s_nr_contrato,
    s_nr_cpf,
    s_id_recurso,
    s_nm_recurso,
    s_id_cargo,
    s_ds_cargo,
    d_dt_data,
    d_dt_data_fim,
    d_dt_inicio_apontamento,
    d_dt_fim_apontamento,
    f_hr_hora_inicio,
    f_hr_hora_fim,
    n_fl_abatimento,
    b_fl_validado,
    s_id_usuario_valida,
    s_nm_usuario_valida,
    s_id_usuario,
    s_nm_usuario,
    s_id_tipo_jornada,
    s_ds_tipo_jornada,
    s_id_divisao,
    s_ds_divisao,
    s_nm_sigla,
    s_nm_cliente_operacional,
    d_dt_inicio_apontamento AS dt_inicio,
    d_dt_fim_apontamento AS dt_fim,
    DATEDIFF(HOUR, d_dt_inicio_apontamento, d_dt_fim_apontamento) AS duracao_horas
FROM {TABLE}
WHERE 
    d_dt_data >= DATEADD(DAY, -90, GETDATE())
    AND d_dt_data <= GETDATE()
    AND b_fl_validado = 1
ORDER BY 
    d_dt_data DESC,
    s_nm_recurso
"""

# ============================================================
# 🔑 OBTÉM TOKEN DE AUTENTICAÇÃO VIA AZURE CLI
# ============================================================
def obter_token_azure():
    """Obtém token de acesso do Azure AD via Azure CLI"""
    print("🔑 Solicitando token ao Azure Entra ID...")
    
    try:
        token_cmd = ["az", "account", "get-access-token", "--resource", "https://database.windows.net"]
        token_raw = subprocess.check_output(token_cmd, shell=True)
        token_data = json.loads(token_raw)
        access_token = token_data["accessToken"]
        expires_on = token_data.get("expiresOn", "desconhecido")
        
        print(f"✅ Token obtido com sucesso!")
        print(f"   Expira em: {expires_on}")
        return access_token
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"❌ Erro ao obter token do Azure CLI: {e}\n"
            "   Execute: az login --tenant '3a78b0cd-7c8e-4929-83d5-190a6cc01365'\n"
        )
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao processar token: {e}")

# ============================================================
# 🔗 CONECTA VIA REST API DO MICROSOFT FABRIC
# ============================================================
def extrair_dados_via_rest_api():
    """Conecta ao Microsoft Fabric via REST API e extrai dados dos últimos 90 dias"""
    
    print("="*80)
    print("📊 EXTRAÇÃO DE DADOS - MICROSOFT FABRIC (VIA REST API)")
    print("="*80)
    print(f"\n📍 Servidor: {SERVER}")
    print(f"📍 Database: {DATABASE}")
    print(f"📍 Tabela: {TABLE}\n")
    
    # Obter token de autenticação
    try:
        access_token = obter_token_azure()
    except RuntimeError as e:
        print(e)
        return None
    
    # Endpoint da REST API do SQL Database
    print("\n🔗 Conectando via REST API...")
    
    # URL base para API do Fabric/SQL
    api_url = f"https://{SERVER}/sql/{DATABASE}/query"
    
    # Headers com autenticação
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Payload com a query
    payload = {
        "query": QUERY.strip(),
        "parameters": []
    }
    
    try:
        print("📥 Executando query SQL...")
        print(f"   Buscando dados dos últimos 90 dias...")
        
        # Fazer requisição POST
        response = requests.post(api_url, headers=headers, json=payload, timeout=300)
        
        # Verificar resposta
        if response.status_code == 200:
            print("✅ Query executada com sucesso!")
            
            # Processar resposta JSON
            data = response.json()
            
            # Converter para DataFrame
            if 'rows' in data and 'columns' in data:
                df = pd.DataFrame(data['rows'], columns=data['columns'])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.read_json(StringIO(json.dumps(data)))
            
            print(f"   Total de registros: {len(df)}")
            
            if len(df) > 0:
                # Mostrar informações básicas
                if 'd_dt_data' in df.columns:
                    print(f"   Período: {df['d_dt_data'].min()} a {df['d_dt_data'].max()}")
                if 's_nm_recurso' in df.columns:
                    print(f"   Usuários únicos: {df['s_nm_recurso'].nunique()}")
                
                # Salvar em CSV
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'resultados/dados_com_duracao_{timestamp}.csv'
                
                os.makedirs('resultados', exist_ok=True)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"\n💾 Dados salvos em: {filename}")
                
                # Estatísticas
                if 'duracao_horas' in df.columns:
                    total_horas = df['duracao_horas'].sum()
                    media_horas = df['duracao_horas'].mean()
                    print(f"\n📊 Estatísticas:")
                    print(f"   Total de horas: {total_horas:.2f}h")
                    print(f"   Média por apontamento: {media_horas:.2f}h")
            else:
                print("\n⚠️ Nenhum dado encontrado para o período especificado")
            
            print("\n🔒 Operação concluída.")
            print("="*80)
            return df
            
        elif response.status_code == 401:
            print(f"❌ Erro de autenticação (401)")
            print("   Token pode ter expirado. Execute novamente: az login")
            return None
        elif response.status_code == 403:
            print(f"❌ Acesso negado (403)")
            print("   Verifique se você tem permissões no Data Warehouse")
            return None
        elif response.status_code == 404:
            print(f"❌ Recurso não encontrado (404)")
            print("   Verifique se a tabela existe: {TABLE}")
            return None
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição (>5min)")
        print("   A query pode estar demorando muito. Tente reduzir o período.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        print("   Verifique sua conexão com a internet e o endpoint do servidor")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================
# 🧠 FUNÇÃO PRINCIPAL
# ============================================================
def main():
    """Função principal do script"""
    try:
        df = extrair_dados_via_rest_api()
        
        if df is not None and len(df) > 0:
            print("\n✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"\n💡 Próximo passo: Execute 'python verificar_90_dias.py' para validar os dados")
            return 0
        else:
            print("\n❌ EXTRAÇÃO FALHOU OU SEM DADOS")
            print("\n💡 NOTA: Microsoft Fabric pode não suportar REST API direta")
            print("   Tente usar o script original: analise_duracao_trabalho.py")
            print("   Ou exporte os dados manualmente do portal do Fabric")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        return 1

# ============================================================
# 🚀 PONTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    exit(main())
