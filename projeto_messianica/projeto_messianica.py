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
    """O Cérebro do formulário: processa, salva e lê os dados do PostgreSQL."""
    
    # Esta variável vai guardar a lista de espíritos para mostrar na tela
    lista_antepassados: list[Antepassado] = []

    def carregar_dados(self):
        """Busca todos os registros salvos no banco de dados."""
        with rx.session() as sessao:
            # Comando oficial atualizado do Reflex para ler a tabela inteira
            self.lista_antepassados = sessao.exec(Antepassado.select()).all()

    def salvar_antepassado(self, form_data: dict):
        nome = form_data.get("nome_completo")
        vinculo = form_data.get("vinculo")
        linhagem = form_data.get("linhagem")
        
        if not nome or not vinculo or not linhagem:
            return rx.window_alert("Erro: Preencha todos os campos do espírito.")
        
        with rx.session() as sessao:
            novo_registro = Antepassado(
                nome_completo=nome,
                vinculo=vinculo,
                linhagem=linhagem,
                usuario_id=1  # Usuário Fantasma temporário
            )
            sessao.add(novo_registro)
            sessao.commit()
            
        # Recarrega a lista automaticamente logo após salvar
        self.carregar_dados()
        return rx.window_alert(f"O registro de {nome} foi salvo com sucesso!")

def renderizar_linha(antepassado: Antepassado):
    """Desenha uma linha individual na tabela visual."""
    return rx.table.row(
        rx.table.cell(antepassado.nome_completo),
        rx.table.cell(antepassado.vinculo),
        rx.table.cell(antepassado.linhagem),
    )  
def index():
    """Esta é a página principal da aplicação."""
    return rx.center(
        rx.vstack(
            # === NOVO: O LOGOTIPO DA IGREJA ===
            rx.image(
                src="/logo.png",  # O nome exato do arquivo que você colocou na pasta assets
                width="150px",    # Tamanho controlado para não distorcer a tela
                height="auto",
                margin_bottom="1em" # Dá um pequeno espaço entre a logo e o título
            ),
            rx.heading("Registro de Antepassados", size="7"),
            rx.text("Preencha os dados do espírito para o ofício religioso."),
            
            # BLOCO 1: O Formulário (Entrada de Dados)
            rx.form(
                rx.vstack(
                    rx.input(name="nome_completo", placeholder="Nome Completo do Espírito", required=True, width="100%"),
                    rx.select(["Avô", "Avó", "Pai", "Mãe", "Tio", "Tia", "Irmão", "Irmã", "Bisavô", "Bisavó", "Amigo(a)", "Outro"], name="vinculo", placeholder="Selecione o Vínculo", required=True, width="100%"),
                    rx.radio(["Materna", "Paterna"], name="linhagem", required=True),
                    rx.button("Salvar Registro", type="submit", width="100%", color_scheme="blue"),
                    spacing="4",
                ),
                on_submit=EstadoCadastro.salvar_antepassado,
                reset_on_submit=True,
                width="100%",
                max_width="400px"
            ),
            
            # BLOCO 2: A Tabela Visual (Saída de Dados)
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nome do Espírito"),
                        rx.table.column_header_cell("Vínculo"),
                        rx.table.column_header_cell("Linhagem"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(EstadoCadastro.lista_antepassados, renderizar_linha)
                ),
                width="100%",
                margin_top="2em"
            ),

            # === NOVAS CONFIGURAÇÕES DE COR E CONTRASTE ===
            align="center",
            padding="2em",
            border="1px solid #333333",  # Borda mais escura para não ofuscar
            border_radius="8px",
            box_shadow="lg",
            width="100%",
            max_width="800px",
            background_color="#1E1E1E",  # Fundo da caixa de cadastro (Cinza Escuro)
            color="white"                # Força todo o texto de dentro a ser branco
        ),
        # === COR DE FUNDO DA TELA INTEIRA ===
        min_height="100vh",
        padding_y="4em",
        background_color="#121212"       # Fundo da página inteira (Cinza Quase Preto)
    )
# Inicialização obrigatória do aplicativo Reflex
app = rx.App()
app.add_page(index, on_load=EstadoCadastro.carregar_dados) # Esta linha conecta a interface ao aplicativo