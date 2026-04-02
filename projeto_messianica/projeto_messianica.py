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
    """O Cérebro do formulário: processa, salva, edita e exclui dados no PostgreSQL."""
    
    lista_antepassados: list[Antepassado] = []
    vinculo_selecionado: str = ""
    
    # === VARIÁVEIS PARA CONTROLE DE EDIÇÃO ===
    antepassado_editando: Antepassado = Antepassado() # Guarda temporariamente o registro que será editado
    modal_edicao_aberto: bool = False # Controla se a janela de edição está visível

    @rx.var
    def total_registos(self) -> int:
        return len(self.lista_antepassados)
        
    @rx.var
    def desabilita_linhagem(self) -> bool:
        sem_linhagem = ["Pai", "Mãe", "Irmão", "Irmã", "Amigo(a)", "Outro"]
        return self.vinculo_selecionado in sem_linhagem

    def carregar_dados(self):
        """Busca todos os registros e ordena do mais recente para o mais antigo."""
        with rx.session() as sessao:
            self.lista_antepassados = sessao.exec(
                Antepassado.select().order_by(Antepassado.id.desc())
            ).all()

    def salvar_antepassado(self, form_data: dict):
        nome = form_data.get("nome_completo")
        vinculo = self.vinculo_selecionado
        linhagem = form_data.get("linhagem")
        
        if self.desabilita_linhagem:
            linhagem = "Não aplicável"
        
        if not nome or not vinculo or not linhagem:
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
        self.vinculo_selecionado = "" 
        return rx.toast.success(f"{nome} salvo com sucesso!", position="top-right")

    # === LOGICA DE EXCLUSÃO (DELETE) ===
    def excluir_registo(self, id_registo: int):
        """Remove um registro do banco de dados pelo ID."""
        with rx.session() as sessao:
            registo = sessao.exec(Antepassado.select().where(Antepassado.id == id_registo)).first()
            if registo:
                sessao.delete(registo)
                sessao.commit()
        self.carregar_dados()
        return rx.toast.success("Registro removido com sucesso.")

    # === LOGICA DE EDIÇÃO (UPDATE) ===
    def abrir_modal_edicao(self, antepassado: Antepassado):
        """Prepara o estado e abre a janela de edição."""
        self.antepassado_editando = antepassado
        self.vinculo_selecionado = antepassado.vinculo
        self.modal_edicao_aberto = True

    def fechar_modal(self):
        """Fecha a janela de edição sem salvar."""
        self.modal_edicao_aberto = False

    def editar_antepassado(self, form_data: dict):
        """Grava as alterações do registro no banco de dados."""
        # 1. Extração segura da linhagem
        linhagem = form_data.get("linhagem")
        
        # 2. Lógica de Proteção: Força um valor neutro se o campo estava desabilitado na tela
        if self.desabilita_linhagem:
            linhagem = "Não aplicável"
            
        # 3. Trava final de segurança para evitar o erro NotNullViolation no banco
        if not linhagem:
            return rx.toast.error("Erro: A linhagem não pode ficar em branco.")

        # 4. Transação com o banco de dados
        with rx.session() as sessao:
            registo = sessao.exec(
                Antepassado.select().where(Antepassado.id == self.antepassado_editando.id)
            ).first()
            if registo:
                registo.nome_completo = form_data.get("nome_completo")
                registo.vinculo = self.vinculo_selecionado
                registo.linhagem = linhagem  # <-- Agora usamos a nossa variável protegida
                sessao.add(registo)
                sessao.commit()
        
        self.modal_edicao_aberto = False
        self.carregar_dados()
        return rx.toast.success("Dados atualizados com sucesso!")

def renderizar_linha(antepassado: Antepassado):
    return rx.table.row(
        rx.table.cell(antepassado.nome_completo),
        rx.table.cell(antepassado.vinculo),
        rx.table.cell(antepassado.linhagem),
        rx.table.cell(
            rx.hstack(
                # Botão Editar
                rx.icon(
                    "pencil", 
                    size=18, 
                    cursor="pointer", 
                    on_click=lambda: EstadoCadastro.abrir_modal_edicao(antepassado),
                    color="blue"
                ),
                # Botão Excluir
                rx.icon(
                    "trash-2", 
                    size=18, 
                    cursor="pointer", 
                    on_click=lambda: EstadoCadastro.excluir_registo(antepassado.id),
                    color="red"
                ),
                spacing="3"
            )
        ),
    )
def index():
    """Esta é a página principal da aplicação."""
    return rx.center(
        rx.vstack(
            
            # === O MODAL DE EDIÇÃO (Janela Oculta) ===
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Editar Antepassado"),
                    rx.form(
                        rx.vstack(
                            rx.input(
                                name="nome_completo", 
                                default_value=EstadoCadastro.antepassado_editando.nome_completo,
                                width="100%"
                            ),
                            rx.select(
                                ["Tataravô", "Tataravó", "Bisavô", "Bisavó", "Avô", "Avó", "Pai", "Mãe", "Tio", "Tia", "Irmão", "Irmã", "Primo", "Prima", "Amigo(a)", "Outro"],
                                value=EstadoCadastro.vinculo_selecionado,
                                on_change=EstadoCadastro.set_vinculo_selecionado,
                                width="100%"
                            ),
                            rx.radio(
                                ["Materna", "Paterna"],
                                name="linhagem",
                                default_value=EstadoCadastro.antepassado_editando.linhagem,
                                disabled=EstadoCadastro.desabilita_linhagem,
                            ),
                            rx.hstack(
                                rx.button("Cancelar", on_click=EstadoCadastro.fechar_modal, variant="soft"),
                                rx.button("Salvar Alterações", type="submit", color_scheme="blue"),
                            ),
                        ),
                        on_submit=EstadoCadastro.editar_antepassado,
                    ),
                ),
                open=EstadoCadastro.modal_edicao_aberto,
            ),

            # === O LOGOTIPO DA IGREJA ===
            rx.image(
                src="/logo.png", 
                width="150px",   
                height="auto",
                margin_bottom="1em"
            ),
            rx.heading("Registro de Antepassados", size="7"),
            rx.text("Preencha os dados do espírito para o ofício religioso."),
            
            # === BLOCO 1: O Formulário (Entrada de Dados) ===
            rx.form(
                rx.vstack(
                    rx.input(name="nome_completo", placeholder="Nome Completo do Espírito", required=True, width="100%"),
                    rx.select(
                        ["Tataravô", "Tataravó", "Bisavô", "Bisavó", "Avô", "Avó", "Pai", "Mãe", "Tio", "Tia", "Irmão", "Irmã", "Primo", "Prima", "Amigo(a)", "Outro"],
                        placeholder="Selecione o Vínculo",
                        value=EstadoCadastro.vinculo_selecionado,      
                        on_change=EstadoCadastro.set_vinculo_selecionado,
                        required=True,
                        width="100%"
                    ),
                    rx.radio(
                        ["Materna", "Paterna"],
                        name="linhagem",
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
            
            # === BLOCO 2: A Tabela Visual (Saída de Dados) ===
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
                        rx.table.column_header_cell("Ações"), 
                    ),
                ),
                rx.table.body(
                    rx.foreach(EstadoCadastro.lista_antepassados, renderizar_linha)
                ),
                width="100%",
                margin_top="2em"
            ),

            # === CONFIGURAÇÕES DE COR E CONTRASTE ===
            align="center",
            padding="2em",
            border="1px solid #333333",
            border_radius="8px",
            box_shadow="lg",
            width="100%",
            max_width="800px",
            background_color="#1E1E1E",
            color="white"
        ),
        min_height="100vh",
        padding_y="4em",
        background_color="#121212"
    ) 
# Inicialização obrigatória do aplicativo Reflex
app = rx.App()
app.add_page(index, on_load=EstadoCadastro.carregar_dados) # Esta linha conecta a interface ao aplicativo