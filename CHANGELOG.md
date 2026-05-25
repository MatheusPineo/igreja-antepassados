# Changelog

## [Unreleased]
### Adicionado
- **Autenticação JWT e Hashing Bcrypt**: Substituição do hashing SHA-256 legado por Bcrypt (`passlib`). Adicionada geração de *JSON Web Tokens (JWT)* nas rotas de login/registro. O frontend agora envia cabeçalhos `Authorization: Bearer <token>` dinamicamente.
- **Proteção Anti-IDOR**: Adicionada função de dependência de segurança (`get_current_user`) para proteger todas as rotas `/antepassados` e `/usuarios`. Os IDs na URL foram removidos e o sistema agora identifica o escopo do usuário ativo via token, resolvendo a vulnerabilidade de IDOR.
- **Serviço de Exportação de PDF (`pdf_service.py`)**: Implementado motor gerador de PDF utilizando a biblioteca `ReportLab`. Gera os formulários de culto às almas dos antepassados seguindo restritamente os padrões da Sede Central de Lisboa.
- **Testes Unitários**: Criado arquivo `tests/test_pdf_service.py` para garantir a funcionalidade de paginação e validação do buffer de memória (OOM prevention).

### Modificado
- `README.md` e `ARCHITECTURE.md` documentados com as atualizações arquiteturais sobre o módulo de Segurança Core e motor gerador de PDF em memória.
