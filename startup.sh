#!/bin/bash

# Azure App Service startup script
# Configurar porta (Azure define via variável de ambiente)
PORT=${PORT:-8000}

echo "🚀 Iniciando aplicação na porta $PORT..."
echo "📁 Diretório atual: $(pwd)"
echo "📄 Arquivos disponíveis:"
ls -la

# Verificar se CSV existe
if [ -f "resultados/dados_anonimizados_decupado_20251118_211544.csv" ]; then
    echo "✅ CSV encontrado!"
else
    echo "❌ CSV não encontrado em resultados/"
    ls -la resultados/
fi

# Iniciar gunicorn com uvicorn workers
exec gunicorn -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind=0.0.0.0:$PORT \
    --timeout 600 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    bot.bot_api:app
