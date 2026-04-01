# Estágio 1: Construção
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Instala dependências do sistema e Node.js
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Instala as dependências do Python
RUN pip install -r requirements.txt

# Força o Node.js a consumir no máximo 256 MB de RAM
ENV NODE_OPTIONS="--max-old-space-size=256"

# Inicializa o Reflex e compila o frontend
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Porta padrão do Reflex
EXPOSE 3000
EXPOSE 8000

# Comando para rodar a aplicação em produção
CMD reflex db migrate && reflex run --env prod