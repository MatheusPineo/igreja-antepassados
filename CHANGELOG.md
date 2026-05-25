# Diário de Bordo Técnico (Changelog)

Todas as alterações notáveis, falhas resolvidas e saltos de versão técnica deste projeto serão documentadas estritamente neste arquivo histórico.

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
