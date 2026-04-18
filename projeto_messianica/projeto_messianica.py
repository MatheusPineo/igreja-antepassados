import reflex as rx
from reflex_google_auth import GoogleAuthState, google_oauth_provider, google_login
import os
from dotenv import load_dotenv
from .models import Usuario, Antepassado
from .ui import renderizar_linha, label_input, form_cadastro_antepassado
from .states import EstadoCadastro
from .auth import AuthState

# 1. Carregar variáveis de ambiente
load_dotenv()
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# --- COMPONENTE CUSTOMIZADO REACT ---
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

class AuthState(GoogleAuthState):
    @rx.var
    def usuario_atual(self) -> Usuario:
        if not self.token_is_valid:
            return Usuario(nome="", email="", google_id="")
        email = self.tokeninfo.get("email")
        nome = self.tokeninfo.get("name")
        gid = self.tokeninfo.get("sub")
        try:
            with rx.session() as sessao:
                user = sessao.exec(Usuario.select().where(Usuario.google_id == gid)).first()
                if not user:
                    user = Usuario(nome=nome, email=email, google_id=gid)
                    sessao.add(user)
                    sessao.commit()
                    sessao.refresh(user)
                return user
        except Exception as e:
            return Usuario(nome="Erro", email=str(e), google_id="")

    @rx.var
    def perfil_incompleto(self) -> bool:
        user = self.usuario_atual
        return user.nome_real == "" or user.tipo_usuario == ""

def index():
    return google_oauth_provider(
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.spacer(),
                    rx.hstack(
                        rx.icon("sun", size=16),
                        rx.switch(checked=rx.color_mode == "dark", on_change=rx.toggle_color_mode),
                        rx.icon("moon", size=16),
                        spacing="2", align="center",
                    ),
                    width="100%", padding_bottom="1em",
                ),

                rx.cond(
                    ~AuthState.token_is_valid,
                    rx.vstack(
                        rx.image(src="/logo.png", width="180px", margin_bottom="3em"),
                        rx.heading("Acesso Restrito", size="8"),
                        google_login(client_id=CLIENT_ID),
                        align="center", padding="4em", border_radius="12px", border="1px solid #333", width="100%",
                        background_color=rx.color_mode_cond(light="white", dark="#1E1E1E"),
                    ),
                    rx.cond(
                        AuthState.perfil_incompleto,
                        rx.vstack(
                            rx.heading("Bem-vindo!", size="6", margin_bottom="1.5em"),
                            rx.form(
                                rx.vstack(
                                    label_input("Nome Próprio", rx.input(name="nome_real", placeholder="Ex: Matheus", required=True, width="100%")),
                                    label_input("Sobrenome Completo", rx.input(name="sobrenome", placeholder="Ex: Pineo", required=True, width="100%")),
                                    label_input("Seu Vínculo", rx.select(["Membro", "Frequentador"], placeholder="Selecione...", on_change=EstadoCadastro.set_tipo_usuario_selecionado, width="100%")),
                                    rx.cond(EstadoCadastro.eh_membro, label_input("Sua Igreja", rx.select(["Coimbra", "Lisboa", "Braga", "Guimarães"], name="igreja", placeholder="Cidade", width="100%"))),
                                    rx.button("Começar Agora", type="submit", width="100%", color_scheme="blue", margin_top="1em"),
                                    spacing="4",
                                ),
                                on_submit=EstadoCadastro.salvar_perfil, width="100%", max_width="480px",
                            ),
                            align="center", padding="2em", width="100%",
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
                                        rx.cond(
                                            EstadoCadastro.is_editing_photo,
                                            rx.vstack(
                                                rx.box(
                                                    rx.cond(
                                                        ~EstadoCadastro.mostrando_editor,
                                                        rx.vstack(
                                                            rx.upload(rx.button("Escolher Arquivo", size="2", variant="outline"), id="nova_foto", border="1px dashed #ccc", padding="2em", width="100%"),
                                                            rx.button("Abrir Editor", on_click=EstadoCadastro.handle_upload_inicial(rx.upload_files(upload_id="nova_foto")), size="1", color_scheme="blue"),
                                                            align="center", width="100%", spacing="3",
                                                        ),
                                                        rx.vstack(
                                                            rx.box(
                                                                EasyCropper.create(
                                                                    image=EstadoCadastro.temp_img_base64,
                                                                    crop=EstadoCadastro.crop_coords,
                                                                    zoom=EstadoCadastro.zoom,
                                                                    on_crop_change=EstadoCadastro.set_crop_coords,
                                                                    on_zoom_change=EstadoCadastro.set_zoom,
                                                                    on_crop_complete=EstadoCadastro.on_crop_complete,
                                                                ),
                                                                width="100%", height="200px", position="relative", overflow="hidden", border_radius="8px",
                                                            ),
                                                            rx.slider(value=[EstadoCadastro.zoom * 100], on_change=lambda v: EstadoCadastro.set_zoom(v[0] / 100), min=100, max=300, width="100%"),
                                                            rx.button(
                                                                rx.cond(EstadoCadastro.is_processing, rx.spinner(size="1"), "Finalizar Corte"),
                                                                on_click=EstadoCadastro.finalizar_corte, 
                                                                color_scheme="green", size="2", width="100%", disabled=EstadoCadastro.is_processing
                                                            ),
                                                            width="100%", spacing="3"
                                                        ),
                                                    ),
                                                    width="100%", padding="1em", background_color=rx.color_mode_cond(light="#f9f9f9", dark="#252525"), border_radius="8px"
                                                ),
                                                padding_bottom="1.5em", width="100%"
                                            )
                                        ),
                                        rx.divider(),
                                        rx.form(
                                            rx.vstack(
                                                label_input("Nome Principal", rx.input(name="nome_real", default_value=AuthState.usuario_atual.nome_real, width="100%")),
                                                label_input("Sobrenome", rx.input(name="sobrenome", default_value=AuthState.usuario_atual.sobrenome, width="100%")),
                                                label_input("Tipo", rx.select(["Membro", "Frequentador"], value=EstadoCadastro.tipo_usuario_selecionado, on_change=EstadoCadastro.set_tipo_usuario_selecionado, width="100%")),
                                                rx.cond(EstadoCadastro.eh_membro, label_input("Igreja", rx.select(["Coimbra", "Lisboa", "Braga", "Guimarães"], name="igreja", default_value=AuthState.usuario_atual.igreja, width="100%"))),
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
                                        rx.table.header(rx.table.row(rx.table.column_header_cell("Espírito"), rx.table.column_header_cell("Vínculo"), rx.table.column_header_cell("Linhagem"), rx.table.column_header_cell("Ações"))),
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
                padding="2em", border_radius="8px", box_shadow="lg", width="100%", max_width="800px",
                background_color=rx.color_mode_cond(light="white", dark="#1E1E1E"),
                color=rx.color_mode_cond(light="black", dark="white"),
                border="1px solid", border_color=rx.color_mode_cond(light="#E5E5E5", dark="#333"),
            ),
            min_height="100vh", padding_y="4em",
            background_color=rx.color_mode_cond(light="#F5F5F5", dark="#121212"),
        ),
        client_id=CLIENT_ID
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="blue"))
app.add_page(index, on_load=EstadoCadastro.carregar_dados)
