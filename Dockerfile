# Estágio 1: Construção
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Instala dependências do sistema e Caddy (O Node.js só é instalado para a fase de compilação)
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

# Roteamento Inteligente: O Caddy entrega a interface (HTML) de imediato e protege o Backend
RUN echo ":8080 {" > Caddyfile && \
    echo "    encode gzip" >> Caddyfile && \
    echo "    @backend path /auth* /antepassados* /usuarios* /ping* /docs* /openapi.json*" >> Caddyfile && \
    echo "    handle @backend {" >> Caddyfile && \
    echo "        reverse_proxy 127.0.0.1:8000" >> Caddyfile && \
    echo "    }" >> Caddyfile && \
    echo "    handle {" >> Caddyfile && \
    echo "        root * /app/Frontend/dist" >> Caddyfile && \
    echo "        try_files {path} {path}.html {path}/ /index.html" >> Caddyfile && \
    echo "        file_server" >> Caddyfile && \
    echo "    }" >> Caddyfile && \
    echo "}" >> Caddyfile

# Compila o Frontend (React)
RUN cd Frontend && npm install && npm run build

# Otimizações de Memória
ENV NODE_OPTIONS="--max-old-space-size=128"
ENV MALLOC_ARENA_MAX=2
ENV PYTHONUNBUFFERED=1

# Porta principal que o Render vai escutar
EXPOSE 8080

# Inicia o backend do FastAPI e liga o Caddy
CMD uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 & uvicorn_pid=$!; caddy run --config Caddyfile & caddy_pid=$!; wait -n; exit $?