# Projeto Messianica - Nova Arquitetura (React + FastAPI)

Este projeto foi migrado de uma arquitetura baseada em Reflex para uma stack moderna desacoplada.

## Estrutura

- `backend/`: Servidor API construído com **FastAPI** e **SQLModel**.
- `Frontend/`: Aplicação web moderna construída com **React**, **Vite**, **TypeScript**, **Tailwind CSS** e **Shadcn/UI**.
- `reflex.db`: Banco de dados SQLite compartilhado.

## Como Executar

### 1. Backend (API)

Certifique-se de ter o Python instalado. Recomenda-se usar um ambiente virtual.

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor
python run.py
```
O backend ficará disponível em `http://localhost:8000`.

### 2. Frontend (React)

Navegue até a pasta do frontend e instale as dependências usando Bun (recomendado) ou NPM.

```bash
cd Frontend

# Instalar dependências
bun install # ou npm install

# Iniciar o ambiente de desenvolvimento
bun dev # ou npm run dev
```
O frontend ficará disponível em `http://localhost:8080` (conforme configurado no `vite.config.ts`).

## Funcionalidades

- **Autenticação**: Login e Cadastro integrados ao banco de dados existente.
- **Gestão de Antepassados**: CRUD completo de registros.
- **Exportação de PDF**: Geração de formulário PDF formatado com base nos registros do usuário.
- **Design Moderno**: Interface responsiva e elegante baseada no sistema de design da Igreja Messiânica.
