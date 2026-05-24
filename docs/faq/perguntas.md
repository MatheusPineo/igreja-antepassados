# Perguntas Frequentes (FAQ)

## Como evitamos que o sistema fique lento na primeira requisição (Hibernação)?

Foi implementada uma rota interna especial chamada `/ping` que serve como **Endpoint de Aquecimento (Keep-Alive)**.

O que ela faz na prática:
1. **Acorda a API:** Recebe uma solicitação programada a cada 10~14 minutos. Isso impede que o servidor Render considere a aplicação "ociosa" e derrube a nossa instância (o que causaria demora no próximo carregamento).
2. **Acorda o Banco de Dados:** Além de responder, a rota executa uma consulta extremamente leve (`SELECT 1`) no banco de dados. Com isso, evitamos que bancos de dados gratuitos pausem seus clusters e gerem atrasos para os usuários.

### Como configurar os disparos (Para Desenvolvedores)?
Basta cadastrar a URL completa do endpoint de ping (ex: `https://sua-api.onrender.com/ping`) em serviços gratuitos de cron, como o **cron-job.org** ou o **UptimeRobot**, e agendar para disparar solicitações do tipo `GET` a cada 14 minutos.

