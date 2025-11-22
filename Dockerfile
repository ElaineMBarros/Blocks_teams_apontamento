# Dockerfile para Railway
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (cache de layers)
COPY requirements_railway.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements_railway.txt

# Copiar código da aplicação
COPY . .

# Porta padrão (Railway define dinamicamente via variável PORT)
ENV PORT=8000

# Comando de inicialização usando api_simples.py
CMD ["python", "api_simples.py"]
