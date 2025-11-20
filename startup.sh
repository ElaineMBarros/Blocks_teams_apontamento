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

# Testar import antes de iniciar
echo "🧪 Testando imports..."
python -c "import bot.bot_api; print('✅ Import OK')" || { echo "❌ Erro no import!"; python -c "import bot.bot_api" 2>&1; exit 1; }

echo "🚀 Iniciando gunicorn..."
# Iniciar gunicorn com uvicorn workers
exec gunicorn -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind=0.0.0.0:$PORT \
    --timeout 600 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --preload \
    bot.bot_api:app
