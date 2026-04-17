# 📑 Especificações Técnicas: Sistema de Gestão de Antepassados

## 1. Visão Geral do Sistema
Este sistema é uma plataforma Full-Stack voltada para a digitalização e organização de registros genealógicos em contextos institucionais/religiosos. O foco principal é a integridade dos dados e a rastreabilidade da linhagem familiar.

## 2. Stack Tecnológica (Core)
- **Linguagem:** Python 3.11+ (Foco em POO e Tipagem Estática).
- **Framework Web:** Reflex (Frontend reativo em Next.js/React compilatdo via Python).
- **Banco de Dados:** PostgreSQL (Instância em nuvem no Render).
- **ORM:** SQLModel (Abstração sobre SQLAlchemy).
- **Migrações:** Alembic (Controle de versão de esquema).
- **Infraestrutura:** Docker (Containerização Multi-stage).

## 3. Arquitetura de Rede e Deploy (Estratégia Caddy)
Para otimizar o consumo de memória e resolver gargalos de latência (especificamente erros 502 no Render), o sistema utiliza a seguinte topologia:
- **Reverse Proxy:** Caddy Server atuando na porta 80.
- **Frontend:** Arquivos estáticos servidos diretamente pelo Caddy.
- **Backend:** Processo Python isolado rodando na porta 8000.
- **Comunicação:** O Caddy faz o roteamento dinâmico para o backend e gerencia conexões de WebSockets Seguros (WSS).
- **Otimização de RAM:** Uso de variáveis de ambiente (`MALLOC_ARENA_MAX=2`) para prevenir vazamento de memória em ambientes restritos (512MB RAM).

## 4. Regras de Negócio e Lógica de Domínio
- **Validação de Linhagem:** O campo de linhagem (Materno/Paterno) deve ser desabilitado para vínculos diretos ou externos que não compõem a árvore de sangue imediata (ex: Pai, Mãe, Irmão, Amigo, Outro).
- **Exceção de Rastreio:** O vínculo "Primo/Prima" **deve** manter a seleção de linhagem habilitada para fins de mapeamento genealógico preciso.
- **Feedback:** Todas as operações de CRUD devem disparar notificações (Toasts) de sucesso ou erro para o usuário.

## 5. Estrutura de Dados (Esquema)
- **Entidade Principal:** `Pessoa` (ou `Antepassado`).
- **Campos Críticos:** Nome, Vínculo, Linhagem, Status de Cadastro.
- **Persistência:** Atualmente via PostgreSQL. (Nota: Base de dados gratuita expira em 01/05/2026 - plano de migração para Neon.tech ou Supabase em pauta).

## 6. Padrões de Código e Preferências
- **Nomenclatura:** Variáveis e funções em snake_case (Padrão Python).
- **Interface:** Componentes Reflex (Radix UI).
- **Segurança:** Variáveis sensíveis (URLs de banco) devem ser lidas via `os.getenv` a partir de um arquivo `.env` (não versionado).

---
*Documento de Referência Técnica - Desenvolvido por Matheus Pineo*