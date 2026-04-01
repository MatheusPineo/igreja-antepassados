# 1: Construção
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Instalar as dependências do sistema e Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Instalar as dependências do Python
RUN pip install -r requirements.txt

# Inicializar o Reflex e compilar o frontend
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Porta padrão do Reflex
EXPOSE 3000
EXPOSE 8000

# Comando para rodar a aplicação em produção
CMD ["reflex", "run", "--env", "prod"]