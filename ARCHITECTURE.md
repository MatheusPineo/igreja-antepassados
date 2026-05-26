# Arquitetura do Sistema de Gestão de Antepassados

## O Mapa do Tesouro (Design Pattern e Estrutura)

O sistema foi reconstruído baseando-se no modelo puro de **Arquitetura Desacoplada (Client-Server)**. O Frontend é um Single Page Application (SPA) reativo que consome estritamente uma API RESTful governada pelo Backend.

### Regras Rígidas e Inquebráveis do Sistema
1. **Nunca chame o banco de dados direto no front-end**: O React não tem conhecimento sobre SQL ou Supabase. Todas as consultas de dados obrigatoriamente passam pelo cliente HTTP encapsulado (`services/api.ts`), que chama a API do FastAPI (Backend).
2. **Segurança Centralizada (Single Source of Truth)**: A validação de identidade (JWT), descriptografia de dados e a prevenção contra vazamento cruzado (IDOR) ocorrem puramente no Backend através da injeção da dependência `get_current_user`.
3. **Gerenciamento de Estado Otimizado**: O Frontend delega a busca, gestão de cache e mutação dos dados ao motor avançado `@tanstack/react-query`. O uso global e indiscriminado de `useState`/`useEffect` para buscar APIs e gerir grandes estados locais é desencorajado e obsoleto.

### Estrutura Explicada de Pastas
- `backend/app/api/endpoints/`: Concentra os controladores unificados de domínio das rotas (Auth, Usuários, Antepassados). 
- `backend/app/core/`: O "cérebro" das conexões. Realiza as configurações vitais de banco de dados (`database.py`) definindo Connection Pooling tunado com limites físicos e controle transacional, além do motor criptográfico (`security.py`).
- `backend/app/models/`: Declarações restritas das entidades de banco de dados (ORM SQLModel). Define implicitamente o esquema. A tabela `Antepassado` tem forte amarração One-to-Many via Foreign Key `usuario_id` para a tabela `Usuario`.
- `Frontend/src/pages/`: Camada visual e fluxos unificados do usuário.
- `Frontend/src/services/`: Camada de comunicação estrita com a API atuando de interceptadora e sanitizadora de cabeçalhos.
- `Frontend/src/components/`: Componentes reutilizáveis puros da interface (via framework genérico Shadcn/UI).

## Infraestrutura, Defesas de Integridade e Restrições
- **Frontend Estrito (Vercel)**: A Vercel atua no projeto de modo enjaulado. Configurações restritas do diretório `Frontend/vercel.json` forçam-na a atuar sob o framework `Vite` gerando estáticos puros (`dist`). É vetada a interpretação Serverless ou a presença de APIs para impedir interceptação indesejada de fluxos Python.
- **Backend Limitado (Render)**: Limitado severamente a 512MB RAM em sua camada gratuita.
  - *Otimização de Recursos*: O framework pesado `reflex` (não utilizado) foi completamente expurgado do `requirements.txt`, reduzindo significativamente a pegada de memória na compilação e inicialização do container no Render.
  - *Monitoramento Ativo de Container (Resiliência 502/Crash)*: O comando de inicialização `CMD` no Dockerfile monitora ativamente e em paralelo o `uvicorn` e o `caddy` através de controle de PID (`wait -n`). Se qualquer um dos processos morrer ou falhar ao inicializar (como conexões de banco de dados intermitentes), o container é encerrado imediatamente, forçando o Render a reiniciar o container de forma limpa e registrar a falha de imediato.
  - *Mitigação de OOM (Out Of Memory na Exportação)*: Geração de Relatórios (PDF) utilizando buffers lógicos matemáticos (`io.BytesIO`) através da biblioteca de baixo-nível ReportLab, banindo componentes pesados renderizadores baseados em Headless Webkit/Chromium ou geradores HTML2PDF nativos.
