# Diário de Bordo Técnico (Changelog)

Todas as alterações notáveis, falhas resolvidas e saltos de versão técnica deste projeto serão documentadas estritamente neste arquivo histórico.

## [v1.2.0] - 2026-05-26
### Changed (Alterado)
- **Expulsão do Reflex (Otimização)**: Removido o framework pesado `reflex` do `requirements.txt`. Como o backend utiliza exclusivamente FastAPI, a remoção do reflex reduziu drasticamente o consumo de memória OOM durante o build e inicialização no Render (limite de 512MB).
- **Monitoramento Ativo de Processos no Dockerfile**: Ajustado o comando `CMD` no Dockerfile para rodar o `uvicorn` e o `caddy` em paralelo usando explicitamente o shell `/bin/bash -c` para suportar a instrução `wait -n` (não compatível com o shell padrão `/bin/sh` do Debian). Isso captura os PIDs de ambos e termina o container imediatamente se qualquer um dos dois processos falhar, impedindo que o Caddy continue ativo mascarando quedas com erros 502 Bad Gateway.
- **Resiliência de Conexão ao Supabase (IPv4 Fallback)**: Desenvolvido um interceptador automático no [database.py](file:///c:/Users/mathe/projeto_messianica/backend/app/core/database.py) que identifica se o host direto do Supabase (`db.ghvnkwiwochirnjeefyh.supabase.co`) está sendo utilizado e converte dinamicamente em tempo de execução para a URL do **Transaction Pooler IPv4** (`aws-1-eu-central-1.pooler.supabase.com:6543`) com o respectivo tenant mapeado. Isso sana permanentemente as quedas por `Network is unreachable` causadas pela falta de suporte a IPv6 na rede do Render.

### Fixed (Corrigido)
- **Conflito de Múltiplas Sessões (Atualização de Perfil)**: Corrigido o erro 500 no endpoint `PUT /usuarios/me` que causava a mensagem "Internal server connection error". O usuário atualizado agora é explicitamente carregado na mesma sessão ativa do banco da rota local, evitando a exceção de colisão de sessões do SQLAlchemy.
- **NameError no Guardião de Autenticação (JWTError)**: Corrigido o erro de NameError onde a variável de tratamento de exceção `JWTError` não existia no escopo devido ao uso da biblioteca `PyJWT` (o correto é `jwt.PyJWTError`). Isso garante que tokens inválidos ou expirados retornem HTTP 401 Unauthorized limpo ao invés de quebrarem o servidor em 500.

## [v1.1.0] - 2026-05-25
### Added (Adicionado)
- **Supabase Data Migration (DB)**: Desenvolvido e executado rotina ETL completa em script Python apartado (`migrate_local_to_supabase.py`) para transporte das contas e dezenas de antepassados do SQLite local (reflex.db) para o cluster avançado Cloud PostgreSQL do Supabase.
- **Global Exception Middleware**: Adicionado guardião no root da API FastAPI (`main.py`) que intercepta falhas de infraestrutura não contidas (crashes totais) disparando um graceful JSON status 500 no lugar de abortar a transação liberando HTML sujos via 502 Bad Gateway Proxy.
- **COOP Header Injections**: Integrados cabeçalhos restritos de `Cross-Origin-Opener-Policy: same-origin-allow-popups` simultaneamente na sub-rotina Frontend Vercel (`vercel.json`) e via Middleware backend (Garantia Redundante) para liberação e sincronia das janelas Pop-up do ecossistema Google.
- **Connection Pool Engine**: Configuração extrema adicionada ao núcleo do SQLAlchemy, contendo regras duras de contenção de fluxos lentos através de `pool_size`, `max_overflow`, `pool_timeout` e `pool_recycle`.

### Fixed (Corrigido)
- **Vercel Serverless Misconfiguration**: Corrigido bloqueio total de compilação da Vercel após heurísticas da plataforma confundirem arquivos do repositório root Python com requisições de Serveless APIs autônomas. Isolação efetuada transpondo todo o bloco operacional para `Frontend/vercel.json` associado a flag Vite.
- **Google FedCM Authentication Drop**: Extintas as interrupções criptográficas em ambiente Chrome e derivados que silenciavam o pop-up ou matavam o envio da promessa assíncrona. Forçado o override do Componente de Login desativando fluxos automáticos invasivos (`ux_mode="popup"`, `useOneTap={false}`).
- **Crash Nativo "Unexpected end of JSON input"**: Reestruturada o interpretador de requisições base no cliente React (`api.ts`). Secreta interceptação de `Content-Type` executada e recusa forçada com throw Exception preventivo sempre que o backend entregar páginas genéricas sujas (HTML) ou vazias, contendo a falha graciosamente.

## [v1.0.0] - 2026-05-25
### Added
- Autenticação e Autorização arquitetural profunda via JWT Bearer Token e hashing Bcrypt.
- Proteção IDOR impenetrável nas rotas restritas de exclusão e extração de PDF do antepassado.
- Motor ultraleve de impressão em memória via ReportLab.
