# Estágio 1: Construção
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Instala dependências do sistema e Node.js (Atualizado para a versão 20 recomendada pelo log)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -sL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Instala as dependências do Python
RUN pip install -r requirements.txt

# --- BLINDAGEM DE MEMÓRIA PARA SERVIDOR GRATUITO (512MB) ---
# 1. Reduz o consumo máximo do Node.js de 256MB para 128MB
ENV NODE_OPTIONS="--max-old-space-size=128"
# 2. Força o Python a reciclar a memória RAM imediatamente e não fragmentar
ENV MALLOC_ARENA_MAX=2
# 3. Impede que os logs do Python fiquem presos na memória
ENV PYTHONUNBUFFERED=1
# 4. Informa ao Render exatamente onde o site está para ele parar de procurar
ENV PORT=3000

# Inicializa o Reflex e compila o frontend
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Expõe a porta principal
EXPOSE 8000

# Comando final: Migra a base de dados e liga o servidor
CMD reflex db migrate && reflex run --env prod --frontend-port 3000 --backend-port 8000