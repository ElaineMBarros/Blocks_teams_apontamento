# 🔍 RELATÓRIO DE VERIFICAÇÃO - CONSULTA DATALAKE (90 DIAS)

**Data da Análise:** 17/11/2025  
**Autor:** Análise Automatizada  
**Status:** ⚠️ DADOS DESATUALIZADOS

---

## 📋 RESUMO EXECUTIVO

### Situação Encontrada
- **Arquivo de Dados:** `resultados/dados_com_duracao_20251104_130000.csv`
- **Data de Extração:** 04/11/2025 às 13:00
- **Última Atualização:** Há **35 dias** (dados desatualizados)
- **Status dos Dados:** ⚠️ **PARCIALMENTE DESATUALIZADOS**

### ⚠️ PROBLEMA IDENTIFICADO

Os dados **NÃO estão** trazendo os últimos 90 dias completos:

| Métrica | Esperado | Encontrado | Status |
|---------|----------|------------|--------|
| **Período de Cobertura** | 19/08/2025 - 17/11/2025 | 21/08/2025 - 13/10/2025 | ⚠️ Incompleto |
| **Total de Dias** | 90 dias | 53 dias | ❌ 37 dias faltando |
| **Dias com Dados** | ~90 dias | 23 dias | ⚠️ Cobertura de 25.6% |
| **Data Mais Recente** | 17/11/2025 (hoje) | 13/10/2025 | ❌ 35 dias atrasado |

---

## 📊 ANÁLISE DETALHADA DOS DADOS

### Estrutura dos Dados Encontrados

**Total de Registros:** 200  
**Usuários Únicos:** 19  
**Total de Horas:** 942.87h  
**Média por Apontamento:** 4.71h

### Período Coberto

```
Data Inicial:    21/08/2025
Data Final:      13/10/2025
Dias Cobertos:   53 dias
Dias com Dados:  23 dias
```

### Top 5 Usuários (período analisado)

1. **Rosiane Lopes dos Santos** - 117.18h
2. **Viviane Alves Dos Santos** - 73.13h
3. **João Vitor Veiga Alves** - 69.37h
4. **Karina Oliveira Inacio** - 68.58h
5. **Renan Siciliano de Oliveira** - 66.90h

### 🔴 Lacunas Identificadas

**33 datas sem apontamentos** nos últimos 90 dias, incluindo:
- 19/08/2025 (Tuesday)
- 20/08/2025 (Wednesday)
- 23/08/2025 (Saturday)
- 24/08/2025 (Sunday)
- ... e mais 29 datas

---

## 🔎 ARQUIVO DE CONSULTA AO DATALAKE

### ❌ ARQUIVO NÃO ENCONTRADO

O sistema faz referência a um arquivo chamado **`analise_duracao_trabalho.py`** que deveria fazer a consulta ao Microsoft Fabric Data Warehouse, mas este arquivo **não foi encontrado** no repositório atual.

### Referências no Código

O arquivo é mencionado em:
- `agente_apontamentos.py` (linha ~33): `"Execute: python analise_duracao_trabalho.py"`
- `teste_novas_funcionalidades.py`
- `teste_ia_conversacional.py`

### 📁 Localização Esperada

```
blocks_teams/
├── analise_duracao_trabalho.py   ❌ NÃO ENCONTRADO
├── agente_apontamentos.py         ✅ Existe (lê os CSVs)
└── resultados/
    └── dados_com_duracao_*.csv    ✅ Existe (dados desatualizados)
```

---

## 💡 EXEMPLO DE QUERY SQL PARA DATALAKE

### Query Recomendada (Microsoft Fabric Data Warehouse)

```sql
-- ============================================================
-- CONSULTA DATALAKE - ÚLTIMOS 90 DIAS
-- Data: @DATA_ATUAL
-- Objetivo: Extrair apontamentos dos últimos 90 dias
-- ============================================================

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
    [schema].[tabela_apontamentos]  -- AJUSTAR NOME DA TABELA
    
WHERE 
    -- FILTRO CRÍTICO: ÚLTIMOS 90 DIAS
    d_dt_data >= DATEADD(DAY, -90, GETDATE())
    AND d_dt_data <= GETDATE()
    
    -- Filtros adicionais (opcional)
    AND b_fl_validado = 1  -- Apenas validados
    
ORDER BY 
    d_dt_data DESC,
    s_nm_recurso;
```

### Verificação da Query

Para garantir que está trazendo 90 dias:

```sql
-- Query de verificação
SELECT 
    MIN(d_dt_data) AS data_minima,
    MAX(d_dt_data) AS data_maxima,
    DATEDIFF(DAY, MIN(d_dt_data), MAX(d_dt_data)) AS total_dias,
    COUNT(*) AS total_registros,
    COUNT(DISTINCT s_nm_recurso) AS total_usuarios,
    COUNT(DISTINCT CAST(d_dt_data AS DATE)) AS dias_com_dados
FROM 
    [schema].[tabela_apontamentos]
WHERE 
    d_dt_data >= DATEADD(DAY, -90, GETDATE());
```

**Resultado Esperado:**
- `total_dias` deve ser próximo de 90
- `dias_com_dados` depende dos dias úteis com apontamentos

---

## 🔧 CONFIGURAÇÃO NO .ENV

```env
# Microsoft Fabric Data Warehouse
FABRIC_ENDPOINT=your-endpoint.datawarehouse.fabric.microsoft.com
FABRIC_DATABASE=your-database-name

# Azure AD Authentication
AZURE_CLIENT_ID=your-azure-ad-client-id
AZURE_CLIENT_SECRET=your-azure-ad-client-secret
AZURE_TENANT_ID=3a78b0cd-7c8e-4929-83d5-190a6cc01365
```

---

## 📝 SCRIPT DE EXTRAÇÃO MODELO (Python)

```python
"""
Script para extrair dados do Microsoft Fabric Data Warehouse
Consulta os últimos 90 dias de apontamentos
"""

import pyodbc
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def extrair_dados_fabric():
    """Extrai dados dos últimos 90 dias do Fabric Data Warehouse"""
    
    # Configurações de conexão
    server = os.getenv('FABRIC_ENDPOINT')
    database = os.getenv('FABRIC_DATABASE')
    
    # String de conexão Microsoft Fabric
    connection_string = f'''
    Driver={{ODBC Driver 18 for SQL Server}};
    Server=tcp:{server},1433;
    Database={database};
    Authentication=ActiveDirectoryInteractive;
    Encrypt=yes;
    TrustServerCertificate=no;
    '''
    
    try:
        print("🔗 Conectando ao Microsoft Fabric...")
        conn = pyodbc.connect(connection_string)
        
        # Query SQL com filtro de 90 dias
        query = """
        SELECT 
            *,
            DATEDIFF(HOUR, d_dt_inicio_apontamento, d_dt_fim_apontamento) AS duracao_horas
        FROM 
            [schema].[tabela_apontamentos]
        WHERE 
            d_dt_data >= DATEADD(DAY, -90, GETDATE())
            AND d_dt_data <= GETDATE()
        ORDER BY 
            d_dt_data DESC
        """
        
        print("📥 Executando consulta SQL...")
        df = pd.read_sql(query, conn)
        
        print(f"✅ {len(df)} registros extraídos")
        
        # Salvar CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'resultados/dados_com_duracao_{timestamp}.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"💾 Dados salvos em: {filename}")
        
        conn.close()
        return df
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

if __name__ == "__main__":
    extrair_dados_fabric()
```

---

## ✅ AÇÕES RECOMENDADAS

### 1. **URGENTE - Atualizar Dados**

```bash
# Executar script de extração
python analise_duracao_trabalho.py
# ou
python extrair_dados_fabric.py
```

### 2. **Verificar Query SQL**

- [ ] Confirmar se a query no script de extração tem o filtro: `DATEADD(DAY, -90, GETDATE())`
- [ ] Verificar se a tabela e schema estão corretos
- [ ] Testar conexão com Microsoft Fabric Data Warehouse

### 3. **Validar Resultado**

```bash
# Após atualizar os dados, executar:
python verificar_90_dias.py
```

**Resultado esperado:**
- Cobertura: > 80% dos últimos 90 dias
- Data mais recente: hoje ou ontem
- Status: COMPLETO

### 4. **Automação (Recomendado)**

Configurar job automático para extrair dados:
- **Periodicidade:** Diária (preferencialmente à noite)
- **Horário:** 23:00 - 01:00
- **Ferramenta:** Azure Data Factory, Airflow, ou Cron Job

---

## 📊 MONITORAMENTO

### Métricas para Acompanhar

1. **Tempo desde última atualização** (deve ser < 24h)
2. **Cobertura dos últimos 90 dias** (deve ser > 80%)
3. **Total de registros** (crescimento esperado)
4. **Usuários ativos** (comparar com mês anterior)

### Script de Monitoramento

```python
# verificar_90_dias.py (já criado)
python verificar_90_dias.py
```

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- **Microsoft Fabric Docs:** https://learn.microsoft.com/fabric/
- **ODBC Driver 18:** https://learn.microsoft.com/sql/connect/odbc/
- **PyODBC:** https://github.com/mkleehammer/pyodbc

---

## 🎯 CONCLUSÃO

### Status Atual
❌ **Os dados NÃO estão trazendo os últimos 90 dias completos**

### Problemas Identificados
1. ❌ Arquivo de extração (`analise_duracao_trabalho.py`) não encontrado
2. ❌ Dados desatualizados (última atualização há 35 dias)
3. ❌ Cobertura parcial (apenas 25.6% dos últimos 90 dias)
4. ⚠️ Lacunas significativas nos dados

### Próximos Passos
1. 🔍 **Localizar ou criar** o script de extração do datalake
2. ✅ **Verificar** a query SQL para garantir filtro de 90 dias
3. 🔄 **Executar** extração atualizada
4. ✔️ **Validar** com `verificar_90_dias.py`
5. 🤖 **Automatizar** processo de extração

---

**Última Atualização:** 17/11/2025  
**Próxima Revisão:** Após atualização dos dados
