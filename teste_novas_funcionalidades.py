"""
Teste das novas funcionalidades:
1. Contar dias úteis no período
2. Calcular horas esperadas
3. Identificar dias não apontados
"""

from agente_apontamentos import AgenteApontamentos

def main():
    print("\n" + "="*80)
    print("🧪 TESTE DAS NOVAS FUNCIONALIDADES")
    print("="*80 + "\n")
    
    agente = AgenteApontamentos()
    
    if agente.df is None:
        print("❌ Dados não carregados. Execute: python analise_duracao_trabalho.py")
        return
    
    # Período de teste: 01/09 a 30/09
    data_inicio = "01/09/2025"
    data_fim = "30/09/2025"
    
    print("\n📅 PERÍODO DE TESTE: 01/09/2025 a 30/09/2025\n")
    print("="*80)
    
    # TESTE 1: Contar dias úteis
    print("\n1️⃣ TESTE: Quantos dias úteis tem no período?\n")
    resultado1 = agente.contar_dias_uteis_periodo(data_inicio, data_fim)
    print(resultado1['resposta'])
    print(f"\n📊 Detalhes:")
    print(f"   - Dias úteis: {resultado1['dados']['dias_uteis']}")
    print(f"   - Fins de semana: {resultado1['dados']['dias_fim_semana']}")
    print(f"   - Total de dias: {resultado1['dados']['total_dias']}")
    
    print("\n" + "-"*80)
    
    # TESTE 2: Calcular horas esperadas
    print("\n2️⃣ TESTE: Quantas horas o colaborador deveria fazer?\n")
    resultado2 = agente.calcular_horas_esperadas_periodo(data_inicio, data_fim, horas_por_dia=8.0)
    print(resultado2['resposta'])
    print(f"\n📊 Detalhes:")
    print(f"   - Horas esperadas brutas: {resultado2['dados']['horas_esperadas_brutas']}h")
    print(f"   - Desconto almoço: {resultado2['dados']['horas_almoco']}h")
    print(f"   - Horas esperadas líquidas: {resultado2['dados']['horas_esperadas_liquidas']}h")
    
    print("\n" + "-"*80)
    
    # TESTE 3: Dias não apontados (geral - todos os usuários)
    print("\n3️⃣ TESTE: Quem não apontou horas no período?\n")
    resultado3 = agente.dias_nao_apontados(data_inicio, data_fim)
    print(resultado3['resposta'])
    
    if resultado3['dados'].get('usuarios_com_faltas', 0) > 0:
        print(f"\n📊 Resumo:")
        print(f"   - Total de colaboradores: {resultado3['dados']['total_usuarios']}")
        print(f"   - Com dias não apontados: {resultado3['dados']['usuarios_com_faltas']}")
        print(f"   - Apontaram todos os dias: {resultado3['dados']['total_usuarios'] - resultado3['dados']['usuarios_com_faltas']}")
    
    print("\n" + "-"*80)
    
    # TESTE 4: Dias não apontados (usuário específico - se houver)
    if agente.df is not None and len(agente.df) > 0:
        # Pegar o primeiro usuário disponível
        usuario_teste = agente.df['s_nm_recurso'].iloc[0]
        print(f"\n4️⃣ TESTE: Dias não apontados - Usuário Específico ({usuario_teste})\n")
        resultado4 = agente.dias_nao_apontados(data_inicio, data_fim, usuario_teste)
        print(resultado4['resposta'])
        
        if 'dados' in resultado4:
            print(f"\n📊 Resumo do colaborador:")
            print(f"   - Dias úteis no período: {resultado4['dados'].get('dias_uteis_total', 0)}")
            print(f"   - Dias apontados: {resultado4['dados'].get('dias_apontados', 0)}")
            print(f"   - Dias não apontados: {resultado4['dados'].get('dias_nao_apontados', 0)}")
    
    print("\n" + "="*80)
    print("✅ TESTES CONCLUÍDOS!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
