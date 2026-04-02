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
    echo "    @backend path /_event* /ping* /_upload*" >> Caddyfile && \
    echo "    handle @backend {" >> Caddyfile && \
    echo "        reverse_proxy 127.0.0.1:8000" >> Caddyfile && \
    echo "    }" >> Caddyfile && \
    echo "    handle {" >> Caddyfile && \
    echo "        root * /app/frontend_static" >> Caddyfile && \
    echo "        try_files {path} {path}.html {path}/ /404.html" >> Caddyfile && \
    echo "        file_server" >> Caddyfile && \
    echo "    }" >> Caddyfile && \
    echo "}" >> Caddyfile

# Otimizações Extremas de Memória
ENV NODE_OPTIONS="--max-old-space-size=128"
ENV MALLOC_ARENA_MAX=2
ENV PYTHONUNBUFFERED=1

# Inicializa o Reflex e compila a "Pele" do site
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Proteção de Versões: Copia a interface gerada para uma pasta segura, independentemente da versão do Reflex
RUN mkdir -p /app/frontend_static && \
    cp -r /app/.web/build/client/* /app/frontend_static/ 2>/dev/null || \
    cp -r /app/.web/_static/* /app/frontend_static/ 2>/dev/null || true

# Porta principal que o Render vai escutar
EXPOSE 8080

# Inicia APENAS o backend do Reflex e liga o Caddy
CMD reflex db migrate && reflex run --env prod --backend-only & caddy run --config Caddyfile