# Dockerfile para Railway
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

# Declarar ARGs que virão do Railway (build-time)
ARG MICROSOFT_APP_ID
ARG MICROSOFT_APP_PASSWORD
ARG MICROSOFT_APP_TENANTID
ARG MICROSOFT_APP_TYPE
ARG OPENAI_API_KEY
ARG OPENAI_MODEL
ARG PORT

# Converter ARGs em ENVs (runtime)
ENV MICROSOFT_APP_ID=${MICROSOFT_APP_ID}
ENV MICROSOFT_APP_PASSWORD=${MICROSOFT_APP_PASSWORD}
ENV MICROSOFT_APP_TENANTID=${MICROSOFT_APP_TENANTID}
ENV MICROSOFT_APP_TYPE=${MICROSOFT_APP_TYPE:-SingleTenant}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV OPENAI_MODEL=${OPENAI_MODEL:-gpt-4o-mini}
ENV PORT=${PORT:-8080}

# Comando de inicialização usando bot_api.py
CMD ["python", "bot/bot_api.py"]
