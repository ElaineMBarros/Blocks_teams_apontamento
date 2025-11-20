import pandas as pd

# Ler o CSV
csv_file = 'resultados/dados_20251117_170227_corrigido.csv'
df = pd.read_csv(csv_file, encoding='utf-8')

# Filtrar registros que contenham "Jaime" em qualquer coluna de texto
# Procurar em colunas de nome de recurso, usuário e validador
mask = (
    df['s_nm_recurso'].str.contains('Jaime', case=False, na=False) |
    df['s_nm_usuario'].str.contains('Jaime', case=False, na=False) |
    df['s_nm_usuario_valida'].str.contains('Jaime', case=False, na=False)
)

registros_jaime = df[mask].head(100)

# Criar arquivo de saída formatado
output_file = 'registros_jaime_100.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 150 + "\n")
    f.write("100 PRIMEIROS REGISTROS COM 'JAIME'\n")
    f.write("=" * 150 + "\n\n")
    
    f.write("LEGENDA DAS COLUNAS:\n")
    f.write("-" * 150 + "\n")
    f.write("s_id_apontamento         = ID do Apontamento\n")
    f.write("s_ds_operacao            = Operação/Empresa\n")
    f.write("s_nr_contrato            = Número do Contrato\n")
    f.write("s_nr_cpf                 = CPF do Recurso\n")
    f.write("s_id_recurso             = ID do Recurso\n")
    f.write("s_nm_recurso             = Nome do Recurso (Funcionário)\n")
    f.write("s_id_cargo               = ID do Cargo\n")
    f.write("s_ds_cargo               = Descrição do Cargo\n")
    f.write("d_dt_data                = Data do Apontamento\n")
    f.write("d_dt_data_fim            = Data Fim\n")
    f.write("d_dt_inicio_apontamento  = Data/Hora Início\n")
    f.write("d_dt_fim_apontamento     = Data/Hora Fim\n")
    f.write("f_hr_hora_inicio         = Hora Início (decimal)\n")
    f.write("f_hr_hora_fim            = Hora Fim (decimal)\n")
    f.write("n_fl_abatimento          = Flag Abatimento\n")
    f.write("b_fl_validado            = Validado? (1=Sim)\n")
    f.write("s_id_usuario_valida      = ID do Validador\n")
    f.write("s_nm_usuario_valida      = Nome do Validador\n")
    f.write("s_id_usuario             = ID do Usuário\n")
    f.write("s_nm_usuario             = Nome do Usuário\n")
    f.write("s_id_tipo_jornada        = ID Tipo Jornada\n")
    f.write("s_ds_tipo_jornada        = Descrição Tipo Jornada\n")
    f.write("s_id_divisao             = ID da Divisão\n")
    f.write("s_ds_divisao             = Descrição da Divisão\n")
    f.write("s_nm_sigla               = Sigla\n")
    f.write("s_nm_cliente_operacional = Cliente Operacional\n")
    f.write("=" * 150 + "\n\n")
    
    # Escrever cada registro
    for idx, row in registros_jaime.iterrows():
        f.write(f"\n{'=' * 150}\n")
        f.write(f"REGISTRO {idx + 1}\n")
        f.write(f"{'=' * 150}\n")
        
        # Colunas principais
        f.write(f"\n🔹 IDENTIFICAÇÃO:\n")
        f.write(f"   ID Apontamento: {row['s_id_apontamento']}\n")
        f.write(f"   Operação: {row['s_ds_operacao']}\n")
        f.write(f"   Contrato: {row['s_nr_contrato']}\n")
        
        f.write(f"\n👤 RECURSO (FUNCIONÁRIO):\n")
        f.write(f"   ID: {row['s_id_recurso']}\n")
        f.write(f"   Nome: {row['s_nm_recurso']}\n")
        f.write(f"   CPF: {row['s_nr_cpf']}\n")
        f.write(f"   Cargo: {row['s_ds_cargo']}\n")
        
        f.write(f"\n📅 DATA E HORÁRIO:\n")
        f.write(f"   Data: {row['d_dt_data']}\n")
        f.write(f"   Data Fim: {row['d_dt_data_fim']}\n")
        f.write(f"   Início: {row['d_dt_inicio_apontamento']}\n")
        f.write(f"   Fim: {row['d_dt_fim_apontamento']}\n")
        f.write(f"   Hora Início: {row['f_hr_hora_inicio']}\n")
        f.write(f"   Hora Fim: {row['f_hr_hora_fim']}\n")
        
        f.write(f"\n✅ VALIDAÇÃO:\n")
        f.write(f"   Validado: {'SIM' if row['b_fl_validado'] == 1 else 'NÃO'}\n")
        f.write(f"   ID Validador: {row['s_id_usuario_valida']}\n")
        f.write(f"   Nome Validador: {row['s_nm_usuario_valida']}\n")
        
        f.write(f"\n👥 USUÁRIO:\n")
        f.write(f"   ID: {row['s_id_usuario']}\n")
        f.write(f"   Nome: {row['s_nm_usuario']}\n")
        
        f.write(f"\n🏢 DIVISÃO/GERÊNCIA:\n")
        f.write(f"   ID Divisão: {row['s_id_divisao']}\n")
        f.write(f"   Divisão: {row['s_ds_divisao']}\n")
        f.write(f"   Sigla: {row['s_nm_sigla']}\n")
        f.write(f"   Cliente: {row['s_nm_cliente_operacional']}\n")
        
        f.write(f"\n⏰ JORNADA:\n")
        f.write(f"   Tipo: {row['s_ds_tipo_jornada']}\n")

print(f"✅ Arquivo criado: {output_file}")
print(f"📊 Total de registros com 'Jaime': {len(registros_jaime)}")
