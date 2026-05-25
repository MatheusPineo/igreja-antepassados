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
  - *Mitigação Anti-Queda (Crash 502)*: Middleware de Exceção Global foi imbuído na aplicação central para capturar explosões de memória ou banco de dados originadas no SQLAlchemy. Isso evita o encerramento do worker Uvicorn (salvando o container Docker de um reset fatal) e devolve respostas sãs com 500 JSON.
  - *Mitigação de OOM (Out Of Memory na Exportação)*: Geração de Relatórios (PDF) utilizando buffers lógicos matemáticos (`io.BytesIO`) através da biblioteca de baixo-nível ReportLab, banindo componentes pesados renderizadores baseados em Headless Webkit/Chromium ou geradores HTML2PDF nativos.
