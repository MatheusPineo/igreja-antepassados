import reflex as rx

class Usuario(rx.Model, table=True):
    """Tabela de usuários para o backup e login social."""
    nome: str
    email: str
    google_id: str

class Antepassado(rx.Model, table=True):
    """Tabela que armazena os espíritos dos antepassados."""
    nome_completo: str
    vinculo: str  # Ex: Avô, Avó, Tio
    linhagem: str  # Ex: Materna, Paterna
    usuario_id: int  # Conecta este antepassado ao ID do usuário que o cadastrou

class EstadoCadastro(rx.State):
    """O Cérebro do formulário: processa e salva os dados no PostgreSQL."""
    
    def salvar_antepassado(self, form_data: dict):
        # 1. Extração: Pega os dados que vieram do formulário na tela
        nome = form_data.get("nome_completo")
        vinculo = form_data.get("vinculo")
        linhagem = form_data.get("linhagem")
        
        # 2. Validação: Impede que o sistema salve linhas em branco no banco
        if not nome or not vinculo or not linhagem:
            return rx.window_alert("Erro: Preencha todos os campos do espírito.")
        
        # 3. Transação (O Túnel com o Banco de Dados)
        # O 'with rx.session()' abre a porta do PostgreSQL, faz a operação e fecha sozinho com segurança.
        with rx.session() as sessao:
            novo_registro = Antepassado(
                nome_completo=nome,
                vinculo=vinculo,
                linhagem=linhagem,
                usuario_id=1  # O Usuário Fantasma temporário
            )
            
            sessao.add(novo_registro)
            sessao.commit() # O 'commit' é o que efetivamente grava no disco
            
        # 4. Feedback: Avisa na tela que deu certo
        return rx.window_alert(f"O registro de {nome} foi salvo com sucesso!")

def index():
    """Esta é a página principal da aplicação."""
    return rx.center(
        rx.vstack(
            rx.heading("Registro de Antepassados", size="7"),
            rx.text("Preencha os dados do espírito para o ofício religioso."),
            
            # O Formulário que conversa com a nossa classe EstadoCadastro
            rx.form(
                rx.vstack(
                    # Campo 1: Nome Livre
                    rx.input(
                        name="nome_completo", 
                        placeholder="Nome Completo do Espírito", 
                        required=True,
                        width="100%"
                    ),
                    
                    # Campo 2: Menu Suspenso (Evita erros de digitação do usuário)
                    rx.select(
                        ["Avô", "Avó", "Pai", "Mãe", "Tio", "Tia", "Irmão", "Irmã", "Bisavô", "Bisavó", "Amigo(a)", "Outro"],
                        name="vinculo",
                        placeholder="Selecione o Vínculo",
                        required=True,
                        width="100%"
                    ),
                    
                    # Campo 3: Botões de Seleção Única
                    rx.radio(
                        ["Materna", "Paterna"],
                        name="linhagem",
                        required=True,
                    ),
                    
                    # Botão de Envio
                    rx.button("Salvar Registro", type="submit", width="100%", color_scheme="blue"),
                    spacing="4",
                ),
                on_submit=EstadoCadastro.salvar_antepassado,
                reset_on_submit=True,  # Limpa a tela automaticamente após salvar
                width="100%",
                max_width="400px"
            ),
            align="center",
            padding="2em",
            border="1px solid #eaeaea",
            border_radius="8px",
            box_shadow="lg"
        ),
        # Centraliza o quadro no meio da tela
        height="100vh",
        background_color="#f9f9f9"
    )
# Inicialização obrigatória do aplicativo Reflex
app = rx.App()
app.add_page(index) # Esta linha conecta a interface ao aplicativo