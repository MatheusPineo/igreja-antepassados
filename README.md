# Projeto Messianica - Sistema de Gestão de Antepassados

Este projeto foi desenhado sob uma arquitetura moderna e desacoplada, separando Backend e Frontend.

## Links de Produção
- **Frontend (Interface do Usuário)**: [https://projetomessianica.vercel.app](https://projetomessianica.vercel.app) (Hospedado na Vercel)
- **Backend (API)**: Hospedado no Render (Auto-Deploy via GitHub).
- **Banco de Dados**: Hospedado no Supabase (PostgreSQL).

## Como Instalar e Rodar Localmente

### 1. Configurar Variáveis de Ambiente (.env)
Você precisará de um arquivo `.env` configurado.

**Backend (raiz do projeto):**
```env
DATABASE_URL=postgresql://postgres:sua_senha_aqui@db.url-do-supabase.co:5432/postgres
GOOGLE_CLIENT_ID=seu-google-client-id
SECRET_KEY=sua-chave-secreta-do-jwt
```

**Frontend (`Frontend/.env`):**
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=seu-google-client-id
```

### 2. Backend (FastAPI API)
Abra um terminal na raiz do projeto. Recomenda-se utilizar o ambiente virtual Python.
```bash
# Instalar as dependências do Python
pip install -r requirements.txt

# Iniciar o servidor backend localmente
python run.py
```
A API ficará disponível em `http://localhost:8000`.

### 3. Frontend (React / Vite)
Abra **um novo terminal** e navegue até a pasta do Frontend.
```bash
cd Frontend

# Instalar as dependências do Node
npm install

# Iniciar o servidor de desenvolvimento
npm run dev
```
O Frontend estará rodando em `http://localhost:8080`.

## Principais Funcionalidades
- **Autenticação Segura (JWT + Bcrypt + OAuth2)**: Sessões protegidas e seguras integradas ao banco.
- **Autorização Robusta**: Proteção Ativa contra ataques IDOR (Insecure Direct Object References).
- **Gestão de Dados**: CRUD completo gerenciado de ponta-a-ponta por um cliente blindado contra falhas transacionais.
- **Exportação de PDF em Memória**: Sistema ultraleve de emissão de formulários oficiais sem estouros de memória.
