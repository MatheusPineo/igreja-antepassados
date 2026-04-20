import reflex as rx
from reflex_google_auth import GoogleAuthState, google_oauth_provider, google_login
import os
from dotenv import load_dotenv
from .models import Usuario, Antepassado
from .ui import renderizar_linha, label_input, form_cadastro_antepassado
from .states import EstadoCadastro
from .auth import AuthState
from .constants import TIPOS_USUARIO, IGREJAS, VINCULOS_ANTEPASSADOS, LINHAGENS, ESTADOS_CIVIS, SEXOS, FAMILIAS

load_dotenv()
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class EasyCropper(rx.NoSSRComponent):
    library = "react-easy-crop"
    tag = "Cropper"
    is_default = True
    image: rx.Var[str]
    crop: rx.Var[dict]
    zoom: rx.Var[float]
    aspect: rx.Var[float] = 1 
    crop_shape: rx.Var[str] = "round"
    on_crop_change: rx.EventHandler[lambda e: [e]]
    on_zoom_change: rx.EventHandler[lambda e: [e]]
    on_crop_complete: rx.EventHandler[lambda c, p: [c, p]]

class EstadoTela(rx.State):
    modo: str = "login"
    def alternar_modo(self):
        self.modo = "cadastro" if self.modo == "login" else "login"

def index():
    return rx.center(
        rx.cond(
            ~AuthState.token_is_valid & ~AuthState.esta_logado,
            # TELA DE LOGIN / CADASTRO
            google_oauth_provider(
                rx.vstack(
                    rx.image(src="/logo.png", width="150px", margin_bottom="1.5em"),
                    rx.heading(rx.cond(EstadoTela.modo == "login", "Bem-vindo de volta", "Crie sua conta"), size="5", margin_bottom="1em"),
                    
                    rx.form(
                        rx.vstack(
                            rx.hstack(
                                rx.input(placeholder="Email", type="email", on_change=AuthState.set_email, width="290px"),
                                rx.box(width="20px"), # Espaçador para compensar o ícone da senha
                                width="320px",
                                justify="center"
                            ),
                            rx.hstack(
                                rx.input(
                                    placeholder="Senha", 
                                    type=rx.cond(AuthState.mostrar_senha, "text", "password"), 
                                    on_change=AuthState.set_senha, 
                                    width="290px"
                                ),
                                rx.icon(
                                    rx.cond(AuthState.mostrar_senha, "eye-off", "eye"), 
                                    cursor="pointer", 
                                    on_click=AuthState.alternar_mostrar_senha,
                                    size=20
                                ),
                                width="320px",
                                justify="between",
                                align="center"
                            ),                            rx.cond(
                                EstadoTela.modo == "cadastro",
                                rx.box(
                                    rx.text("Força da senha", size="1", margin_bottom="0.2em"),
                                    rx.progress(
                                        value=rx.cond(AuthState.forca_senha == "Fraca", 33, rx.cond(AuthState.forca_senha == "Média", 66, 100)),
                                        color_scheme=rx.cond(AuthState.forca_senha == "Fraca", "red", rx.cond(AuthState.forca_senha == "Média", "yellow", "green")),
                                        width="290px"
                                    ), width="320px"
                                )
                            ),
                            rx.hstack(
                                rx.input(
                                    placeholder="Confirme a Senha", 
                                    type=rx.cond(AuthState.mostrar_confirmar_senha, "text", "password"), 
                                    on_change=AuthState.set_confirmar_senha, 
                                    width="290px"
                                ),
                                rx.icon(
                                    rx.cond(AuthState.mostrar_confirmar_senha, "eye-off", "eye"), 
                                    cursor="pointer", 
                                    on_click=AuthState.alternar_mostrar_confirmar_senha,
                                    size=20
                                ),
                                width="320px",
                                justify="between",
                                align="center"
                            ),
                            rx.cond(EstadoTela.modo == "cadastro", rx.box(rx.checkbox("Aceito os Termos de Uso", on_change=AuthState.set_aceitou_termos), width="320px", margin_bottom="1em")),
                            
                            rx.cond(EstadoTela.modo == "login", rx.link("Esqueci a senha?", href="#", size="2", align_self="end", margin_right="40px")),
                            
                            rx.button(
                                rx.cond(EstadoTela.modo == "login", "Entrar", "Cadastrar"),
                                on_click=rx.cond(EstadoTela.modo == "login", AuthState.login_email, AuthState.registrar_email),
                                width="320px", color_scheme="blue", margin_top="0.5em"
                            ),
                            align="center"
                        ),
                        width="100%",
                    ),
                    rx.text(
                        rx.cond(EstadoTela.modo == "login", "Não tem conta? ", "Já tem conta? "),
                        rx.link(rx.cond(EstadoTela.modo == "login", "Cadastre-se", "Faça login"), on_click=EstadoTela.alternar_modo),
                        size="2"
                    ),
                    rx.hstack(
                        rx.divider(width="100px"),
                        rx.text("Ou entre com:", size="1", color="gray"),
                        rx.divider(width="100px"),
                        width="100%", justify="center", align="center"
                    ),
                    rx.hstack(
                        rx.box(google_login(client_id=CLIENT_ID), width="150px"),
                        rx.button(
                            rx.hstack(rx.icon("facebook"), rx.text("Facebook")),
                            variant="outline",
                            width="150px",
                            color_scheme="gray"
                        ),
                        justify="center", spacing="4"
                    ),
                    spacing="4", padding="3em", border_radius="16px", border="1px solid #333", width="400px",
                    background_color="#181818", box_shadow="0 4px 12px rgba(0,0,0,0.3)", align="center"
                ),
                client_id=CLIENT_ID
            ),
            # TELA LOGADA
            rx.cond(
                AuthState.perfil_incompleto,
                rx.vstack(
                    rx.heading("Bem-vindo! Complete seu perfil", size="6", margin_bottom="1em"),
                    rx.form(
                        rx.vstack(
                            label_input("Nome Próprio", rx.input(name="nome_real", placeholder="Ex: Matheus", required=True, width="100%")),
                            label_input("Sobrenome Completo", rx.input(name="sobrenome", placeholder="Ex: Pineo", required=True, width="100%")),
                            label_input("Sexo", rx.select(SEXOS, placeholder="Selecione...", on_change=EstadoCadastro.set_sexo_selecionado, width="100%")),
                            label_input("Estado Civil", rx.select(ESTADOS_CIVIS, placeholder="Selecione...", on_change=EstadoCadastro.set_estado_civil_selecionado, width="100%")),
                            label_input("Seu Vínculo", rx.select(TIPOS_USUARIO, placeholder="Selecione...", on_change=EstadoCadastro.set_tipo_usuario_selecionado, width="100%")),
                            rx.cond(EstadoCadastro.eh_membro, label_input("Sua Igreja", rx.select(IGREJAS, name="igreja", placeholder="Cidade", width="100%"))),
                            rx.button("Começar Agora", type="submit", width="100%", color_scheme="blue", margin_top="1em"),
                            spacing="4",
                        ),
                        on_submit=EstadoCadastro.salvar_perfil, width="100%", max_width="400px",
                    ),
                    align="center", padding="2em", background_color="#181818", border_radius="16px", border="1px solid #333"
                ),
                rx.vstack(
                    rx.dialog.root(
                        rx.dialog.content(
                            rx.dialog.title("Configurações de Perfil"),
                            rx.vstack(
                                rx.hstack(
                                    rx.avatar(src=AuthState.usuario_atual.foto, fallback=AuthState.usuario_atual.nome_real[0], size="5"),
                                    rx.vstack(
                                        rx.text("Sua Foto de Perfil", weight="bold", size="2"),
                                        rx.button(
                                            rx.cond(EstadoCadastro.is_editing_photo, "Cancelar Alteração", "Alterar Foto"),
                                            on_click=EstadoCadastro.alternar_edicao_foto,
                                            size="1", variant="ghost", color_scheme="blue"
                                        ),
                                        spacing="1",
                                        align="start"
                                    ),
                                    width="100%", spacing="4", align="center", padding_bottom="1.5em"
                                ),
                                rx.divider(),
                                rx.form(
                                    rx.vstack(
                                        label_input("Nome Principal", rx.input(name="nome_real", default_value=AuthState.usuario_atual.nome_real, width="100%")),
                                        label_input("Sobrenome", rx.input(name="sobrenome", default_value=AuthState.usuario_atual.sobrenome, width="100%")),
                                        label_input("Sexo", rx.select(SEXOS, value=EstadoCadastro.sexo_selecionado, on_change=EstadoCadastro.set_sexo_selecionado, width="100%")),
                                        label_input("Estado Civil", rx.select(ESTADOS_CIVIS, value=EstadoCadastro.estado_civil_selecionado, on_change=EstadoCadastro.set_estado_civil_selecionado, width="100%")),
                                        label_input("Tipo", rx.select(TIPOS_USUARIO, value=EstadoCadastro.tipo_usuario_selecionado, on_change=EstadoCadastro.set_tipo_usuario_selecionado, width="100%")),
                                        rx.cond(EstadoCadastro.eh_membro, label_input("Igreja", rx.select(IGREJAS, name="igreja", default_value=AuthState.usuario_atual.igreja, width="100%"))),
                                        rx.hstack(
                                            rx.button("Fechar", on_click=EstadoCadastro.fechar_modal_perfil, variant="soft", size="2"),
                                            rx.button("Salvar Dados", type="submit", color_scheme="blue", size="2"),
                                            width="100%", justify="end", spacing="3", padding_top="1em"
                                        ),
                                        spacing="4",
                                    ),
                                    on_submit=EstadoCadastro.salvar_perfil, width="100%",
                                ),
                            ),
                            max_width="450px",
                        ),
                        open=EstadoCadastro.modal_perfil_aberto,
                    ),
                    rx.hstack(
                        rx.avatar(src=AuthState.usuario_atual.foto, fallback=AuthState.usuario_atual.nome_real[0], size="3", cursor="pointer", on_click=EstadoCadastro.abrir_modal_perfil),
                        rx.vstack(
                            rx.hstack(
                                rx.text(f"Olá, {AuthState.usuario_atual.nome_real}", weight="bold"),
                                rx.icon(
                                    "pencil", 
                                    size=14, 
                                    cursor="pointer", 
                                    on_click=EstadoCadastro.abrir_modal_perfil,
                                    color_scheme="blue",
                                    margin_left="0.5em"
                                ),
                                align="center",
                            ),
                            rx.text(f"{AuthState.usuario_atual.tipo_usuario} • {AuthState.usuario_atual.igreja}", size="1"),
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button("Sair", on_click=AuthState.logout, variant="soft", color_scheme="red", size="1"),
                        width="100%", border_bottom="1px solid #333", padding_bottom="1em", margin_bottom="3em", align="center",
                    ),

                    rx.image(src="/logo.png", width="160px", margin_bottom="2.5em"),
                    rx.heading("Registro de Antepassados", size="7", margin_bottom="1.5em"),
                    
                    form_cadastro_antepassado(EstadoCadastro.salvar_antepassado, EstadoCadastro.set_vinculo_selecionado),
                    
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text(f"Total de registos: {EstadoCadastro.total_registos}", weight="bold"),
                                rx.spacer(),
                                rx.button(
                                    rx.icon("file-down"),
                                    "Exportar PDF",
                                    on_click=EstadoCadastro.exportar_pdf,
                                    type="button",
                                    color_scheme="green",
                                    variant="soft",
                                    size="2",
                                ),
                                width="100%",
                                align="center",
                            ),
                            rx.table.root(
                                rx.table.header(rx.table.row(rx.table.column_header_cell("Espírito"), rx.table.column_header_cell("Vínculo"), rx.table.column_header_cell("Linhagem"), rx.table.column_header_cell("Família"), rx.table.column_header_cell("Ações"))),
                                rx.table.body(rx.foreach(EstadoCadastro.lista_antepassados, lambda antepassado: renderizar_linha(antepassado, EstadoCadastro.abrir_modal_edicao, EstadoCadastro.excluir_registo))),
                                width="100%",
                            ),
                            spacing="4",
                        ),
                        width="100%", margin_top="4em",
                    ),
                    align="center", width="100%",
                )
            )
        ),
        min_height="100vh", background_color="#121212"
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="blue"))
app.add_page(index, on_load=EstadoCadastro.carregar_dados)
