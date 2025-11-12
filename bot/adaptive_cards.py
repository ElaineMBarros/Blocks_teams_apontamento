"""
Adaptive Cards para Microsoft Teams
Templates de cartões interativos para respostas do bot
"""


def create_welcome_card():
    """Card de boas-vindas"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "Image",
                                        "url": "https://img.icons8.com/color/96/000000/bot.png",
                                        "size": "Medium"
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "size": "Large",
                                        "weight": "Bolder",
                                        "text": "🤖 Agente de Apontamentos",
                                        "wrap": True
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "Seu assistente inteligente para consultas de apontamentos",
                                        "wrap": True,
                                        "isSubtle": True
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "type": "TextBlock",
                "text": "**📊 Consultas Disponíveis:**",
                "weight": "Bolder",
                "spacing": "Medium",
                "separator": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "📊 média", "value": "Ver duração média de trabalho"},
                    {"title": "📅 hoje", "value": "Seus apontamentos de hoje"},
                    {"title": "📈 semana", "value": "Resumo semanal completo"},
                    {"title": "🏆 ranking", "value": "Top 10 funcionários"},
                    {"title": "⚠️ outliers", "value": "Apontamentos fora do padrão"},
                    {"title": "⏱️ total", "value": "Total de horas trabalhadas"},
                    {"title": "🔄 comparar", "value": "Comparar semanas"},
                    {"title": "❓ ajuda", "value": "Ver todos os comandos"}
                ]
            },
            {
                "type": "TextBlock",
                "text": "💡 **Dica:** Faça perguntas naturais como \"Quanto trabalhei hoje?\" ou \"Qual minha média?\"",
                "wrap": True,
                "isSubtle": True,
                "spacing": "Medium"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "📊 Ver Média",
                "data": {"command": "média"}
            },
            {
                "type": "Action.Submit",
                "title": "📅 Hoje",
                "data": {"command": "hoje"}
            },
            {
                "type": "Action.Submit",
                "title": "🏆 Ranking",
                "data": {"command": "ranking"}
            }
        ]
    }


def create_statistics_card(dados):
    """Card para estatísticas gerais"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Large",
                        "weight": "Bolder",
                        "text": "📊 Estatísticas de Apontamento"
                    }
                ]
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Duração Média",
                                "weight": "Bolder",
                                "spacing": "Small"
                            },
                            {
                                "type": "TextBlock",
                                "text": dados.get('formatado', 'N/A'),
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Accent"
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Em Horas Decimais",
                                "weight": "Bolder",
                                "spacing": "Small"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"{dados.get('media_horas', 0):.2f}h",
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Good"
                            }
                        ]
                    }
                ],
                "spacing": "Medium",
                "separator": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {
                        "title": "📈 Mediana:",
                        "value": f"{dados.get('mediana_horas', 0):.2f}h"
                    }
                ],
                "spacing": "Medium"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "🏆 Ver Ranking",
                "data": {"command": "ranking"}
            }
        ]
    }


def create_ranking_card(ranking_data):
    """Card para ranking de funcionários"""
    items = [
        {
            "type": "Container",
            "style": "emphasis",
            "items": [
                {
                    "type": "TextBlock",
                    "size": "Large",
                    "weight": "Bolder",
                    "text": "🏆 Ranking de Horas Trabalhadas"
                }
            ]
        }
    ]
    
    # Top 3 com destaque
    for i, (nome, dados) in enumerate(list(ranking_data.items())[:3], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        color = "Attention" if i == 1 else "Good" if i == 2 else "Accent"
        
        items.append({
            "type": "ColumnSet",
            "separator": i == 1,
            "spacing": "Medium",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [{
                        "type": "TextBlock",
                        "text": medal,
                        "size": "Large"
                    }]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": nome,
                            "weight": "Bolder",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": f"{dados['count']} apontamentos",
                            "isSubtle": True,
                            "size": "Small"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [{
                        "type": "TextBlock",
                        "text": f"{dados['sum']:.2f}h",
                        "weight": "Bolder",
                        "size": "Large",
                        "color": color
                    }]
                }
            ]
        })
    
    # Resto do ranking
    if len(ranking_data) > 3:
        items.append({
            "type": "TextBlock",
            "text": "**Demais Posições:**",
            "weight": "Bolder",
            "spacing": "Medium",
            "separator": True
        })
        
        for i, (nome, dados) in enumerate(list(ranking_data.items())[3:], 4):
            items.append({
                "type": "TextBlock",
                "text": f"{i}. **{nome}**: {dados['sum']:.2f}h ({dados['count']} apontamentos)",
                "wrap": True,
                "spacing": "Small"
            })
    
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": items
    }


def create_user_summary_card(usuario, dados):
    """Card para resumo de usuário específico"""
    diferenca = dados.get('diferenca_media_geral', 0)
    status = "acima ⬆️" if diferenca > 0 else "abaixo ⬇️" if diferenca < 0 else "igual ➡️"
    color = "Good" if diferenca > 0 else "Warning" if diferenca < 0 else "Default"
    
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Large",
                        "weight": "Bolder",
                        "text": f"👤 {usuario}"
                    }
                ]
            },
            {
                "type": "ColumnSet",
                "spacing": "Medium",
                "separator": True,
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Duração Média",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"{dados.get('media_horas', 0):.2f}h",
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Accent"
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Total Apontamentos",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": str(dados.get('total_apontamentos', 0)),
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Good"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "FactSet",
                "spacing": "Medium",
                "separator": True,
                "facts": [
                    {
                        "title": "📊 vs Média Geral:",
                        "value": f"{abs(diferenca):.2f}h {status}"
                    }
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "📅 Ver Hoje",
                "data": {"command": "hoje"}
            },
            {
                "type": "Action.Submit",
                "title": "📈 Ver Semana",
                "data": {"command": "semana"}
            }
        ]
    }


def create_daily_summary_card(dados):
    """Card para resumo do dia"""
    apontamentos = dados.get('apontamentos', [])
    
    items = [
        {
            "type": "Container",
            "style": "emphasis",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [{
                                "type": "TextBlock",
                                "text": "📅",
                                "size": "ExtraLarge"
                            }]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "size": "Large",
                                    "weight": "Bolder",
                                    "text": "Apontamentos de Hoje"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": dados.get('data', ''),
                                    "isSubtle": True
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "spacing": "Medium",
            "separator": True,
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "⏱️ Total Apontado",
                            "weight": "Bolder"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"{dados.get('total_horas', 0):.2f}h",
                            "size": "ExtraLarge",
                            "weight": "Bolder",
                            "color": "Good"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "📝 Quantidade",
                            "weight": "Bolder"
                        },
                        {
                            "type": "TextBlock",
                            "text": str(dados.get('quantidade', 0)),
                            "size": "ExtraLarge",
                            "weight": "Bolder",
                            "color": "Accent"
                        }
                    ]
                }
            ]
        }
    ]
    
    # Lista de apontamentos
    if apontamentos:
        items.append({
            "type": "TextBlock",
            "text": "**Detalhes dos Apontamentos:**",
            "weight": "Bolder",
            "spacing": "Medium",
            "separator": True
        })
        
        for apt in apontamentos[:5]:  # Mostrar no máximo 5
            items.append({
                "type": "ColumnSet",
                "spacing": "Small",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [{
                            "type": "TextBlock",
                            "text": apt.get('operacao', 'N/A'),
                            "wrap": True
                        }]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [{
                            "type": "TextBlock",
                            "text": f"{apt.get('duracao', 0):.2f}h",
                            "weight": "Bolder"
                        }]
                    }
                ]
            })
    
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": items
    }


def create_weekly_summary_card(dados):
    """Card para resumo semanal"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Large",
                        "weight": "Bolder",
                        "text": "📈 Resumo Semanal"
                    }
                ]
            },
            {
                "type": "ColumnSet",
                "spacing": "Medium",
                "separator": True,
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Total da Semana",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"{dados.get('total_horas', 0):.2f}h",
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Good"
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Média Diária",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"{dados.get('media_diaria', 0):.2f}h",
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Accent"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "FactSet",
                "spacing": "Medium",
                "separator": True,
                "facts": [
                    {
                        "title": "📝 Apontamentos:",
                        "value": str(dados.get('quantidade', 0))
                    }
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "🔄 Comparar Semanas",
                "data": {"command": "comparar"}
            }
        ]
    }


def create_comparison_card(dados):
    """Card para comparação de períodos"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Large",
                        "weight": "Bolder",
                        "text": "🔄 Comparação Semanal"
                    }
                ]
            },
            {
                "type": "ColumnSet",
                "spacing": "Medium",
                "separator": True,
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Esta Semana",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"{dados.get('atual', 0):.2f}h",
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Good"
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Semana Passada",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"{dados.get('anterior', 0):.2f}h",
                                "size": "ExtraLarge",
                                "weight": "Bolder",
                                "color": "Accent"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "FactSet",
                "spacing": "Medium",
                "separator": True,
                "facts": [
                    {
                        "title": "📊 Diferença:",
                        "value": f"{dados.get('diferenca', 0):+.2f}h"
                    }
                ]
            }
        ]
    }


def create_outliers_card(outliers_data):
    """Card para outliers"""
    items = [
        {
            "type": "Container",
            "style": "attention",
            "items": [
                {
                    "type": "TextBlock",
                    "size": "Large",
                    "weight": "Bolder",
                    "text": "⚠️ Apontamentos Fora do Padrão"
                }
            ]
        }
    ]
    
    if not outliers_data or len(outliers_data) == 0:
        items.append({
            "type": "Container",
            "style": "good",
            "spacing": "Medium",
            "separator": True,
            "items": [{
                "type": "TextBlock",
                "text": "✅ Nenhum outlier detectado! Todos os apontamentos estão dentro do padrão.",
                "wrap": True,
                "weight": "Bolder"
            }]
        })
    else:
        items.append({
            "type": "TextBlock",
            "text": "Apontamentos que estão significativamente acima ou abaixo da média:",
            "wrap": True,
            "isSubtle": True,
            "spacing": "Medium",
            "separator": True
        })
        
        for item in outliers_data:
            z_score = item.get('z_score', 0)
            color = "Attention" if abs(z_score) > 3 else "Warning"
            
            items.append({
                "type": "ColumnSet",
                "spacing": "Medium",
                "separator": True,
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": item.get('s_nm_recurso', 'N/A'),
                                "weight": "Bolder",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": f"Z-Score: {z_score:.2f}",
                                "size": "Small",
                                "isSubtle": True
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [{
                            "type": "TextBlock",
                            "text": f"{item.get('duracao_horas', 0):.2f}h",
                            "weight": "Bolder",
                            "size": "Large",
                            "color": color
                        }]
                    }
                ]
            })
    
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": items,
        "actions": [
            {
                "type": "Action.Submit",
                "title": "🏆 Ver Ranking",
                "data": {"command": "ranking"}
            }
        ]
    }


def create_error_card(mensagem):
    """Card para erros"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "attention",
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Large",
                        "weight": "Bolder",
                        "text": "❌ Erro"
                    }
                ]
            },
            {
                "type": "TextBlock",
                "text": mensagem,
                "wrap": True,
                "spacing": "Medium"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "❓ Ver Ajuda",
                "data": {"command": "ajuda"}
            }
        ]
    }


def create_text_card(titulo, texto):
    """Card genérico de texto"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": titulo,
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": texto,
                "wrap": True,
                "spacing": "Medium"
            }
        ]
    }


def create_help_card():
    """Card de ajuda completo"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Large",
                        "weight": "Bolder",
                        "text": "❓ Ajuda - Comandos Disponíveis"
                    }
                ]
            },
            {
                "type": "TextBlock",
                "text": "**📊 Estatísticas**",
                "weight": "Bolder",
                "spacing": "Medium",
                "separator": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "média", "value": "Duração média de trabalho"},
                    {"title": "total", "value": "Total de horas trabalhadas"}
                ]
            },
            {
                "type": "TextBlock",
                "text": "**📅 Consultas Temporais**",
                "weight": "Bolder",
                "spacing": "Medium",
                "separator": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "hoje", "value": "Apontamentos do dia atual"},
                    {"title": "semana", "value": "Resumo da semana"},
                    {"title": "comparar", "value": "Comparar semanas"}
                ]
            },
            {
                "type": "TextBlock",
                "text": "**🏆 Rankings e Análises**",
                "weight": "Bolder",
                "spacing": "Medium",
                "separator": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "ranking", "value": "Top 10 funcionários"},
                    {"title": "outliers", "value": "Apontamentos fora do padrão"}
                ]
            },
            {
                "type": "TextBlock",
                "text": "💡 **Dica:** Você também pode fazer perguntas naturais como:\n• \"Quanto trabalhei hoje?\"\n• \"Qual minha média de horas?\"\n• \"Quem trabalhou mais esta semana?\"",
                "wrap": True,
                "isSubtle": True,
                "spacing": "Medium",
                "separator": True
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "📊 Ver Média",
                "data": {"command": "média"}
            },
            {
                "type": "Action.Submit",
                "title": "📅 Hoje",
                "data": {"command": "hoje"}
            },
            {
                "type": "Action.Submit",
                "title": "🏆 Ranking",
                "data": {"command": "ranking"}
            }
        ]
    }
