# 👨‍👩‍👧‍👦 Sistema de Cadastro de Antepassados

🚀 **Acesse o projeto ao vivo:** [igreja-antepassados.onrender.com](https://igreja-antepassados.onrender.com/)

*(Nota: O carregamento inicial pode demorar cerca de 60 segundos se o servidor estiver inativo).*
<img width="1476" height="859" alt="Screenshot_2" src="https://github.com/user-attachments/assets/bf38fb9e-388b-4f49-8c1d-88c11a3d8c00" />

Uma aplicação Full-Stack moderna para o gerenciamento de registros genealógicos, desenvolvida para demonstrar proficiência em engenharia de software, manipulação de banco de dados e deploy em nuvem.

### 💻 Apresentação Técnica

Este projeto foi construído para simular um ambiente de produção real, focando em estabilidade, segurança e performance.

**Destaques de Engenharia:**
* **CRUD Completo:** Implementação total de operações de Criar, Ler, Atualizar e Deletar registros, com feedback instantâneo ao usuário (Toasts).
* **Banco de Dados Robusto:** Utilização de **PostgreSQL** gerenciado na nuvem, com controle de esquema via **Alembic** para migrações contínuas.
* **Deploy em Produção:** Configuração de um ambiente conteinerizado com **Docker**, garantindo consistência entre o ambiente de desenvolvimento e produção.
* **Otimização de Infraestrutura:** Para contornar limitações da camada gratuita de PaaS (Render), implementei um **Reverse Proxy com Caddy** dentro do Docker. Isso otimizou o roteamento do tráfego (WebSockets e Arquivos Estáticos), garantindo estabilidade de conexão e reduzindo drasticamente o consumo de memória RAM.

### 🛠️ Stack Tecnológica

* **Linguagem Principal:** Python
* **Framework Full-Stack:** Reflex (Python + Next.js)
* **Banco de Dados:** PostgreSQL & SQLModel (ORM)
* **Migrações:** Alembic
* **Infraestrutura:** Docker & Caddy (Reverse Proxy)

---

# 👨‍👩‍👧‍👦 Ancestry Registry System

🚀 **Live Project:** [igreja-antepassados.onrender.com](https://igreja-antepassados.onrender.com/)

*(Note: Initial load may take ~60 seconds due to server cold start).*

A modern Full-Stack application for genealogical record management, developed to demonstrate proficiency in software engineering, database management, and cloud deployment.

### 💻 Technical Overview

This project was built to simulate a real-world production environment, focusing on stability, security, and performance.

**Engineering Highlights:**
* **Full CRUD Operations:** Complete implementation of Create, Read, Update, and Delete operations with instant user feedback (Toasts).
* **Robust Database:** Utilization of managed cloud **PostgreSQL**, with schema version control via **Alembic** for continuous migrations.
* **Production Deployment:** Configured a containerized environment using **Docker**, ensuring absolute consistency across local and production environments.
* **Infrastructure Optimization:** To overcome the limitations of the free PaaS tier (Render), I implemented a **Caddy Reverse Proxy** within the Docker container. This optimized traffic routing (WebSockets and Static Files), guaranteeing connection stability and significantly reducing RAM consumption.

### 🛠️ Tech Stack

* **Core Language:** Python
* **Full-Stack Framework:** Reflex (Python + Next.js)
* **Database:** PostgreSQL & SQLModel (ORM)
* **Migrations:** Alembic
* **Infrastructure:** Docker & Caddy (Reverse Proxy)

---
*Desenvolvido por / Developed by Matheus Pineo [https://github.com/MatheusPineo]*
