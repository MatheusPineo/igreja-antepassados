# Diário de Bordo Técnico (Changelog)

Todas as alterações notáveis, falhas resolvidas e saltos de versão técnica deste projeto serão documentadas estritamente neste arquivo histórico.

## [v1.4.1] - 2026-05-26
### Changed (Alterado)
- **Alinhamento do PDF com Pauta Física (`form_template.png`)**: Refatorada a função `generate_pdf_flowable` para mapear estritamente o layout de 2 colunas ("Nome Espírito/Família" na esquerda e "Parentesco/Vínculo" na direita) correspondente ao template físico da Igreja Messiânica.
  - A tabela agora possui larguras exatas (`120mm` e `55mm`) para coincidir com a divisória vertical impressa.
  - Fixada a altura das linhas (`rowHeights=6mm`) com espaçamentos internos zerados para assentar o texto perfeitamente sobre as pautas físicas.
  - As bordas e fundos da tabela foram definidos como transparentes (`None`) para deixar o fundo original da folha intacto.
  - O cabeçalho de títulos ("Nome Espírito" e "Vinculo") e as informações do fiel no rodapé foram desacoplados da tabela de Flowables e posicionados estaticamente via callback de canvas para evitar desalinhamento nas quebras de página.

## [v1.4.0] - 2026-05-26
### Added (Adicionado)
- **Endpoint Protegido `GET /antepassados/pdf`**: Implementado novo endpoint protegido que expõe a exportação de antepassados para PDF em conformidade com o formato oficial da Igreja Messiânica.
- **Nova Arquitetura de Layout do PDF (SimpleDocTemplate & Flowables)**: Migração do sistema antigo baseado em coordenadas físicas de Canvas para uma arquitetura baseada em Flowables (`SimpleDocTemplate`, `Table`, `Spacer` e `Paragraph`). A nova implementação realiza a quebra automática de páginas para listas grandes (64+ antepassados) sem estouros de layout ou sobreposição de textos, estiliza de forma destacada as linhas do tipo "Tronco" (em itálico/negrito e fundo com destaque azul claro) e agrupa os antepassados rigorosamente sob as seções de linhagem hierárquicas oficiais.
- **Download Seguro de PDF com JWT no Frontend**: Implementado o método `exportarPdf` no cliente de API utilizando o `fetch` nativo com `responseType: 'blob'`, protegendo a requisição com o token JWT ativo nos cabeçalhos de autorização. No `Dashboard.tsx`, foi adicionada a lógica de download local via criação e revogação temporária de Object URLs, juntamente com o indicador de estado de carregamento animado no botão de exportação da interface.

## [v1.3.1] - 2026-05-26
### Added (Adicionado)
- **Script de Sementeira de Produção (`seed_mariana_ancestors.py`)**: Criado um script Python autônomo e resiliente na raiz do projeto para semear em lote 97 registros de antepassados oficiais associados à conta da usuária Mariana (`marianasvfolharini@gmail.com`) no Supabase de produção. O script implementa validações robustas de duplicidade, mapeamento automático de linhagens/famílias e usa o Transaction Pooler IPv4 para conexão em nuvem a partir do ambiente local.

## [v1.3.0] - 2026-05-26
### Changed (Alterado)
- **Ordenação Hierárquica Estrita de Antepassados (Regras do Culto)**: Adicionado um algoritmo dinâmico de chaves (`get_ancestor_sort_key`) em `antepassados.py` para classificar os registros em 4 blocos de linhagem estritos (Paterno/Materno do Marido, seguido por Paterno/Materno da Esposa), aplicando a regra oficial onde os "Troncos" (nomes de linhagem) precedem obrigatoriamente os membros individuais. O desempate secundário e final dentro de cada subcategoria foi tornado determinístico através de ordenação alfabética pelo campo `nome_completo`. Esse critério foi integrado na listagem REST da API e na geração de lotes do formulário em PDF.
- **Seccionamento e Destaque Visual no Frontend**: Refatorada a tabela de registros no [Dashboard.tsx](file:///c:/Users/mathe/projeto_messianica/Frontend/src/pages/Dashboard.tsx) para renderizar cabeçalhos de seção estilizados de forma dinâmica nas transições dos blocos de linhagens oficiais. Adicionado realce visual com borda colorida do tema, fonte em itálico e o badge "Tronco" para destacar os registros de linhagem familiar primária.
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
