# Dockerfile para Azure App Service
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (cache de layers)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Porta padrão
ENV PORT=8000

# Comando de inicialização
CMD gunicorn -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind=0.0.0.0:$PORT \
    --timeout 600 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    bot.bot_api:app
