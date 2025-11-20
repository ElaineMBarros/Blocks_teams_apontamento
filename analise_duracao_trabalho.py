"""
📊 EXTRAÇÃO DE DADOS DO DATALAKE - MICROSOFT FABRIC
Script para extrair apontamentos dos últimos 90 dias
Tabela: gold_999_portal_outsourcing_apontamento_ultimos_90_dias
"""

import pyodbc
import pandas as pd
import subprocess
import json
import os
from datetime import datetime

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
    -- Calcular duração em horas
    DATEDIFF(HOUR, d_dt_inicio_apontamento, d_dt_fim_apontamento) AS duracao_horas
FROM 
    {TABLE}
WHERE 
    -- Filtro para últimos 90 dias
    d_dt_data >= DATEADD(DAY, -90, GETDATE())
    AND d_dt_data <= GETDATE()
    AND b_fl_validado = 1  -- Apenas validados
ORDER BY 
    d_dt_data DESC,
    s_nm_recurso
"""

# ============================================================
# 🔎 LOCALIZA O AZURE CLI
# ============================================================
def encontrar_azure_cli():
    """Encontra o executável do Azure CLI no sistema"""
    print("🔍 Verificando instalação do Azure CLI...")
    
    POSSIBLE_PATHS = [
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Users\elain\AppData\Local\Programs\Microsoft VS Code\bin\az.cmd",
    ]
    
    # Tentar encontrar via 'where az'
    try:
        result = subprocess.run(['where', 'az'], capture_output=True, text=True, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            az_path = result.stdout.strip().split('\n')[0]
            if os.path.exists(az_path):
                print(f"✅ Azure CLI encontrado via 'where': {az_path}")
                return az_path
    except:
        pass
    
    # Tentar caminhos conhecidos
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            print(f"✅ Azure CLI encontrado em: {path}")
            return path
    
    raise FileNotFoundError(
        "❌ Azure CLI não encontrado.\n"
        "   Instale com: winget install Microsoft.AzureCLI\n"
        "   Ou rode 'where az' no PowerShell para encontrar o caminho"
    )

# ============================================================
# 🔑 OBTÉM TOKEN DE AUTENTICAÇÃO VIA AZURE CLI
# ============================================================
def obter_token_azure(az_path=None):
    """Obtém token de acesso do Azure AD via Azure CLI"""
    print("\n🔑 Solicitando token ao Azure Entra ID...")
    
    try:
        # Usar 'az' diretamente, deixando o Windows resolver o caminho
        token_cmd = ["az", "account", "get-access-token", "--resource", "https://database.windows.net"]
        token_raw = subprocess.check_output(token_cmd, shell=True)
        access_token = json.loads(token_raw)["accessToken"]
        print("✅ Token obtido com sucesso!")
        return access_token
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"❌ Erro ao obter token do Azure CLI: {e}\n"
            "   Execute: az login\n"
            "   Para fazer login no Azure"
        )
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao processar token: {e}")

# ============================================================
# 🔗 CONECTA E EXTRAI DADOS DO MICROSOFT FABRIC
# ============================================================
def extrair_dados_fabric():
    """Conecta ao Microsoft Fabric e extrai dados dos últimos 90 dias"""
    
    print("="*80)
    print("📊 EXTRAÇÃO DE DADOS - MICROSOFT FABRIC DATA WAREHOUSE")
    print("="*80)
    print(f"\n📍 Servidor: {SERVER}")
    print(f"📍 Database: {DATABASE}")
    print(f"📍 Tabela: {TABLE}\n")
    
    # Obter token de autenticação diretamente
    try:
        access_token = obter_token_azure()
    except RuntimeError as e:
        print(e)
        print("\n💡 Certifique-se de que:")
        print("   1. Azure CLI está instalado")
        print("   2. Você executou: az login")
        print("   3. Tem permissões no Data Warehouse")
        return None
    
    # Conectar ao Fabric Data Warehouse
    print("\n🔗 Tentando conectar ao Microsoft Fabric DW...")
    
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server={SERVER};"
        f"Database={DATABASE};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    
    try:
        # Converte o token para bytes (requisito do ODBC Driver)
        token_bytes = bytes(access_token, "utf-16-le")
        
        # Estabelece conexão com o token
        conn = pyodbc.connect(conn_str, attrs_before={1256: token_bytes})
        
        print("✅ Conexão bem-sucedida!")
        print("\n📥 Executando query SQL...")
        print(f"   Buscando dados dos últimos 90 dias...")
        
        # Executar query e carregar em DataFrame
        df = pd.read_sql(QUERY, conn)
        
        print(f"\n✅ Dados extraídos com sucesso!")
        print(f"   Total de registros: {len(df)}")
        
        if len(df) > 0:
            # Mostrar informações básicas
            print(f"   Período: {df['d_dt_data'].min()} a {df['d_dt_data'].max()}")
            print(f"   Usuários únicos: {df['s_nm_recurso'].nunique()}")
            
            # Salvar em CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'resultados/dados_com_duracao_{timestamp}.csv'
            
            # Criar diretório se não existir
            os.makedirs('resultados', exist_ok=True)
            
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n💾 Dados salvos em: {filename}")
            
            # Estatísticas adicionais
            if 'duracao_horas' in df.columns:
                total_horas = df['duracao_horas'].sum()
                media_horas = df['duracao_horas'].mean()
                print(f"\n📊 Estatísticas:")
                print(f"   Total de horas: {total_horas:.2f}h")
                print(f"   Média por apontamento: {media_horas:.2f}h")
        else:
            print("\n⚠️ Nenhum dado encontrado para o período especificado")
        
        conn.close()
        print("\n🔒 Conexão encerrada com segurança.")
        print("="*80)
        
        return df
        
    except pyodbc.Error as e:
        print(f"\n❌ Erro na conexão ODBC: {e}")
        print("\n💡 Dicas:")
        print("   - Verifique se ODBC Driver 18 for SQL Server está instalado")
        print("   - Execute: az login (para autenticar)")
        print("   - Verifique permissões de acesso ao Data Warehouse")
        return None
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return None

# ============================================================
# 🧠 FUNÇÃO PRINCIPAL
# ============================================================
def main():
    """Função principal do script"""
    try:
        df = extrair_dados_fabric()
        
        if df is not None and len(df) > 0:
            print("\n✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"\n💡 Próximo passo: Execute 'python verificar_90_dias.py' para validar os dados")
            return 0
        else:
            print("\n❌ EXTRAÇÃO FALHOU OU SEM DADOS")
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
