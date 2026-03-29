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
    
    lista_antepassados: list[Antepassado] = []
    
    # === NOVOS CONTROLADORES DE INTERFACE ===
    vinculo_selecionado: str = ""  # Controla o menu suspenso rigorosamente
    
    @rx.var
    def total_registos(self) -> int:
        """Conta quantos espíritos já foram adicionados."""
        return len(self.lista_antepassados)
        
    @rx.var
    def desabilita_linhagem(self) -> bool:
        """Deteta se o vínculo selecionado não possui linhagem direta."""
        sem_linhagem = ["Irmão", "Irmã", "Amigo(a)", "Outro"]
        # Retorna True (Bloqueado) se a palavra estiver na lista acima
        return self.vinculo_selecionado in sem_linhagem

    def carregar_dados(self):
        """Busca todos os registos e ordena do mais recente para o mais antigo."""
        with rx.session() as sessao:
            # O '.desc()' inverte a ordem da base de dados (Descendente)
            self.lista_antepassados = sessao.exec(
                Antepassado.select().order_by(Antepassado.id.desc())
            ).all()

    def salvar_antepassado(self, form_data: dict):
        nome = form_data.get("nome_completo")
        vinculo = self.vinculo_selecionado  # Agora a informação vem do estado controlado
        linhagem = form_data.get("linhagem")
        
        # Lógica de Proteção: Se a linhagem estava bloqueada no ecrã, forçamos um valor neutro
        if self.desabilita_linhagem:
            linhagem = "Não aplicável"
        
        if not nome or not vinculo or not linhagem:
            # Alerta visual flutuante vermelho em caso de erro
            return rx.toast.error("Preencha todos os campos necessários.")
        
        with rx.session() as sessao:
            novo_registro = Antepassado(
                nome_completo=nome,
                vinculo=vinculo,
                linhagem=linhagem,
                usuario_id=1
            )
            sessao.add(novo_registro)
            sessao.commit()
            
        self.carregar_dados()
        
        # CORREÇÃO DO BUG: Força a variável a esvaziar, limpando o menu suspenso corretamente
        self.vinculo_selecionado = "" 
        
        # Feedback Visual: Notificação flutuante com o ícone de 'check' verde
        return rx.toast.success(f"{nome} salvo com sucesso!", position="top-right")

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
                   # Campo 2: Menu Suspenso (Agora Controlado)
                    rx.select(
                        ["Tataravô", "Tataravó", "Bisavô", "Bisavó", "Avô", "Avó", "Pai", "Mãe", "Tio", "Tia", "Irmão", "Irmã", "Primo", "Prima", "Amigo(a)", "Outro"],
                        placeholder="Selecione o Vínculo",
                        value=EstadoCadastro.vinculo_selecionado,       # O Cérebro dita o que aparece
                        on_change=EstadoCadastro.set_vinculo_selecionado, # O Cérebro é avisado da mudança
                        required=True,
                        width="100%"
                    ),
                    
                    # Campo 3: Botões de Seleção Única (Agora Dinâmicos)
                    rx.radio(
                        ["Materna", "Paterna"],
                        name="linhagem",
                        # Desabilita automaticamente consoante a regra do Cérebro
                        disabled=EstadoCadastro.desabilita_linhagem, 
                    ),
                    rx.button("Salvar Registro", type="submit", width="100%", color_scheme="blue"),
                    spacing="4",
                ),
                on_submit=EstadoCadastro.salvar_antepassado,
                reset_on_submit=True,
                width="100%",
                max_width="400px"
            ),
            
            # BLOCO 2: A Tabela Visual (Saída de Dados)
            # O Contador de Registos
            rx.text(
                f"Total de registos: {EstadoCadastro.total_registos}", 
                weight="bold", 
                margin_top="1em"
            ),
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