# Arquitetura do Sistema de Gestão de Antepassados

## Visão Geral
Este sistema foi desenhado para digitalizar e organizar registros genealógicos em contextos institucionais/religiosos. O foco primordial é a integridade dos dados e a rastreabilidade da linhagem familiar.

## Stack Tecnológica Core
- **Linguagem**: Python 3.11+
- **Web Framework Backend**: FastAPI (base estrutural do projeto Reflex original)
- **Frontend**: React + Vite + TypeScript
- **Banco de Dados**: PostgreSQL / SQLite (ambiente dev)
- **ORM**: SQLModel (SQLAlchemy)
- **Infraestrutura**: Docker (Multi-stage com Caddy Server)

## Decisões Arquiteturais e Restrições

### Limite de Memória (Render)
O ambiente de produção possui um teto de **512MB de RAM**. Devido a isso, funcionalidades críticas como a geração de PDFs foram arquitetadas para consumir o mínimo de memória possível.

- **Serviço de PDF (pdf_service.py)**: Utiliza a biblioteca `ReportLab` com geração direta em um buffer na memória (`io.BytesIO`). Evitamos bibliotecas baseadas em headless browsers (como Selenium) e bibliotecas de layout pesado em HTML/CSS (WeasyPrint), focando na precisão das coordenadas (Canvas X/Y) para prevenir Out-Of-Memory (OOM) no servidor.

### Organização de Diretórios
- `/backend/app/api`: Controladores de endpoints.
- `/backend/app/services`: Regras de negócio e processamento de dados (ex: `pdf_service.py`).
- `/backend/app/core/security.py`: Motor de Segurança gerenciando OAuth2PasswordBearer, Bcrypt hashing (passlib) e assinatura de tokens JWT. Prevenção ativa de IDOR nas rotas.
- `/backend/app/models`: Definições de tabelas de banco de dados (SQLModel).
- `/tests`: Suíte de testes unitários (Pytest).
