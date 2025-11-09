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
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "🤖 Agente de Apontamentos",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": "Olá! Sou seu assistente para consultas de apontamentos.",
                "wrap": True,
                "spacing": "Medium"
            },
            {
                "type": "TextBlock",
                "text": "**Comandos disponíveis:**",
                "weight": "Bolder",
                "spacing": "Medium"
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "📊", "value": "média - Ver duração média de trabalho"},
                    {"title": "📅", "value": "hoje - Apontamentos do dia"},
                    {"title": "📈", "value": "semana - Resumo semanal"},
                    {"title": "🏆", "value": "ranking - Top funcionários"},
                    {"title": "⚠️", "value": "outliers - Apontamentos fora do padrão"},
                    {"title": "❓", "value": "ajuda - Mostrar todos os comandos"}
                ]
            }
        ]
    }


def create_statistics_card(dados):
    """Card para estatísticas"""
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "📊 Estatísticas de Apontamento"
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
                                "text": "Duração Média:",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": dados.get('formatado', 'N/A'),
                                "size": "ExtraLarge",
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
                                "text": "Total de Horas:",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"{dados.get('media_horas', 0):.2f}h",
                                "size": "ExtraLarge",
                                "color": "Good"
                            }
                        ]
                    }
                ]
            }
        ]
    }


def create_ranking_card(ranking_data):
    """Card para ranking de funcionários"""
    items = [
        {
            "type": "TextBlock",
            "size": "Large",
            "weight": "Bolder",
            "text": "🏆 Ranking de Horas Trabalhadas"
        }
    ]
    
    for i, (nome, dados) in enumerate(ranking_data.items(), 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        items.append({
            "type": "TextBlock",
            "text": f"{medal} **{nome}**: {dados['sum']:.2f}h ({dados['count']} apontamentos)",
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
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": f"👤 {usuario}"
            },
            {
                "type": "FactSet",
                "facts": [
                    {
                        "title": "📊 Duração Média:",
                        "value": f"{dados.get('media_horas', 0):.2f}h"
                    },
                    {
                        "title": "📋 Total de Apontamentos:",
                        "value": str(dados.get('total_apontamentos', 0))
                    },
                    {
                        "title": "📈 vs Média Geral:",
                        "value": f"{dados.get('diferenca_media_geral', 0):+.2f}h"
                    }
                ]
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
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "❌ Erro",
                "color": "Attention"
            },
            {
                "type": "TextBlock",
                "text": mensagem,
                "wrap": True,
                "spacing": "Medium"
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
                "text": titulo
            },
            {
                "type": "TextBlock",
                "text": texto,
                "wrap": True,
                "spacing": "Medium"
            }
        ]
    }


def create_outliers_card(outliers_data):
    """Card para outliers"""
    items = [
        {
            "type": "TextBlock",
            "size": "Large",
            "weight": "Bolder",
            "text": "⚠️ Apontamentos Fora do Padrão"
        }
    ]
    
    if not outliers_data:
        items.append({
            "type": "TextBlock",
            "text": "✅ Nenhum outlier detectado!",
            "color": "Good",
            "wrap": True
        })
    else:
        for item in outliers_data:
            items.append({
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [{
                            "type": "TextBlock",
                            "text": f"**{item['s_nm_recurso']}**",
                            "wrap": True
                        }]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [{
                            "type": "TextBlock",
                            "text": f"{item['duracao_horas']:.2f}h",
                            "color": "Attention"
                        }]
                    }
                ],
                "spacing": "Small"
            })
    
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": items
    }
