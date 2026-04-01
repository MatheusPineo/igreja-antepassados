# Estágio 1: Construção
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Instala dependências do sistema, Node.js e Caddy (via GitHub Oficial para evitar falhas)
RUN apt-get update && apt-get install -y curl unzip wget \
    && curl -sL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && wget -qO caddy.tar.gz "https://github.com/caddyserver/caddy/releases/download/v2.7.6/caddy_2.7.6_linux_amd64.tar.gz" \
    && tar -xzf caddy.tar.gz caddy \
    && mv caddy /usr/local/bin/ \
    && chmod +x /usr/local/bin/caddy \
    && apt-get clean

# Instala as dependências do Python
RUN pip install -r requirements.txt

# Cria o arquivo de configuração do Caddy (Roteador Interno)
RUN echo ":8080 {" > Caddyfile && \
    echo "    @backend path /_event* /ping* /_upload*" >> Caddyfile && \
    echo "    handle @backend {" >> Caddyfile && \
    echo "        reverse_proxy 127.0.0.1:8000" >> Caddyfile && \
    echo "    }" >> Caddyfile && \
    echo "    handle {" >> Caddyfile && \
    echo "        reverse_proxy 127.0.0.1:3000" >> Caddyfile && \
    echo "    }" >> Caddyfile && \
    echo "}" >> Caddyfile

# Otimizações de Memória para a Camada Gratuita
ENV NODE_OPTIONS="--max-old-space-size=128"
ENV MALLOC_ARENA_MAX=2
ENV PYTHONUNBUFFERED=1

# Inicializa o Reflex e compila o frontend
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Porta principal que o Render vai escutar
EXPOSE 8080

# Inicia o Banco, o Reflex e o Proxy Caddy simultaneamente
CMD reflex db migrate && reflex run --env prod & caddy run --config Caddyfile