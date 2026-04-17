import reflex as rx
from reflex_google_auth import GoogleAuthState, google_oauth_provider, google_login
import os
from dotenv import load_dotenv
import uuid
from PIL import Image
import io
import base64

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

class Usuario(rx.Model, table=True):
    nome: str 
    email: str 
    google_id: str
    nome_real: str = ""
    sobrenome: str = ""
    tipo_usuario: str = "" 
    igreja: str = "" 
    foto: str = "" 

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

class Antepassado(rx.Model, table=True):
    nome_completo: str
    vinculo: str
    linhagem: str
    usuario_id: int

class EstadoCadastro(rx.State):
    lista_antepassados: list[Antepassado] = []
    vinculo_selecionado: str = "" # Corrigido aqui
    antepassado_editando: Antepassado = Antepassado() 
    modal_edicao_aberto: bool = False
    
    tipo_usuario_selecionado: str = ""
    modal_perfil_aberto: bool = False
    
    is_editing_photo: bool = False
    temp_img_base64: str = ""
    crop_coords: dict = {"x": 0, "y": 0}
    zoom: float = 1.0
    final_pixels: dict = {}
    is_processing: bool = False

    @rx.var
    def total_registos(self) -> int:
        return len(self.lista_antepassados)
        
    @rx.var
    def desabilita_linhagem(self) -> bool:
        sem_linhagem = ["Pai", "Mãe", "Irmão", "Irmã", "Amigo(a)", "Outro"]
        return self.vinculo_selecionado in sem_linhagem

    @rx.var
    def eh_membro(self) -> bool:
        return self.tipo_usuario_selecionado == "Membro"

    @rx.var
    def mostrando_editor(self) -> bool:
        return self.temp_img_base64 != ""

    async def abrir_modal_perfil(self):
        auth = await self.get_state(AuthState)
        self.tipo_usuario_selecionado = auth.usuario_atual.tipo_usuario
        self.is_editing_photo = False
        self.temp_img_base64 = ""
        self.modal_perfil_aberto = True

    def fechar_modal_perfil(self):
        if not self.is_processing:
            self.modal_perfil_aberto = False
            self.is_editing_photo = False

    def alternar_edicao_foto(self):
        self.is_editing_photo = not self.is_editing_photo
        if not self.is_editing_photo:
            self.temp_img_base64 = ""

    async def handle_upload_inicial(self, files: list[rx.UploadFile]):
        if not files: return
        file = files[0]
        upload_data = await file.read()
        encoded = base64.b64encode(upload_data).decode("utf-8")
        self.temp_img_base64 = f"data:{file.content_type};base64,{encoded}"
        self.zoom = 1.0
        self.crop_coords = {"x": 0, "y": 0}
        yield rx.toast.info("Ajuste sua foto.")

    def on_crop_complete(self, crop, pixels):
        self.final_pixels = pixels

    async def finalizar_corte(self):
        if not self.temp_img_base64 or not self.final_pixels:
            yield rx.toast.error("Ajuste a imagem primeiro.")
            return
        self.is_processing = True
        temp_data = self.temp_img_base64
        p = self.final_pixels
        self.temp_img_base64 = ""
        self.is_editing_photo = False
        yield 
        auth = await self.get_state(AuthState)
        try:
            header, encoded = temp_data.split(",", 1)
            img_data = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(img_data))
            img = img.crop((p["x"], p["y"], p["x"] + p["width"], p["y"] + p["height"]))
            img = img.resize((150, 150), Image.LANCZOS)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64_final = base64.b64encode(buffered.getvalue()).decode("utf-8")
            full_base64_string = f"data:image/png;base64,{img_base64_final}"
            with rx.session() as sessao:
                user = sessao.exec(Usuario.select().where(Usuario.id == auth.usuario_atual.id)).first()
                if user:
                    user.foto = full_base64_string
                    sessao.add(user)
                    sessao.commit()
            self.is_processing = False
            yield rx.toast.success("Foto salva!")
        except Exception as e:
            self.is_processing = False
            yield rx.toast.error(f"Erro: {e}")

    async def remover_foto(self):
        auth = await self.get_state(AuthState)
        with rx.session() as sessao:
            user = sessao.exec(Usuario.select().where(Usuario.id == auth.usuario_atual.id)).first()
            if user:
                user.foto = ""
                sessao.add(user)
                sessao.commit()
        yield rx.toast.success("Foto removida.")

    async def salvar_perfil(self, form_data: dict):
        auth = await self.get_state(AuthState)
        nome_real = form_data.get("nome_real")
        sobrenome = form_data.get("sobrenome")
        tipo = self.tipo_usuario_selecionado
        igreja = form_data.get("igreja", "") if tipo == "Membro" else "Não aplicável"
        with rx.session() as sessao:
            user = sessao.exec(Usuario.select().where(Usuario.id == auth.usuario_atual.id)).first()
            if user:
                user.nome_real = nome_real
                user.sobrenome = sobrenome
                user.tipo_usuario = tipo
                user.igreja = igreja
                sessao.add(user)
                sessao.commit()
        self.modal_perfil_aberto = False
        await self.carregar_dados()
        yield rx.toast.success("Perfil atualizado!")

    async def carregar_dados(self):
        auth = await self.get_state(AuthState)
        if not auth.token_is_valid or auth.perfil_incompleto:
            self.lista_antepassados = []
            return
        with rx.session() as sessao:
            self.lista_antepassados = sessao.exec(
                Antepassado.select().where(Antepassado.usuario_id == auth.usuario_atual.id).order_by(Antepassado.id.desc())
            ).all()

    async def salvar_antepassado(self, form_data: dict):
        auth = await self.get_state(AuthState)
        nome = form_data.get("nome_completo")
        vinculo = self.vinculo_selecionado
        linhagem = form_data.get("linhagem", "Não aplicável") if not self.desabilita_linhagem else "Não aplicável"
        with rx.session() as sessao:
            novo = Antepassado(nome_completo=nome, vinculo=vinculo, linhagem=linhagem, usuario_id=auth.usuario_atual.id)
            sessao.add(novo)
            sessao.commit()
        await self.carregar_dados()
        yield rx.toast.success("Salvo!")

    async def excluir_registo(self, id_registo: int):
        with rx.session() as sessao:
            registo = sessao.exec(Antepassado.select().where(Antepassado.id == id_registo)).first()
            if registo:
                sessao.delete(registo)
                sessao.commit()
        await self.carregar_dados()
        yield rx.toast.success("Removido.")

    def abrir_modal_edicao(self, antepassado: Antepassado):
        self.antepassado_editando = antepassado
        self.vinculo_selecionado = antepassado.vinculo
        self.modal_edicao_aberto = True

    def fechar_modal(self):
        self.modal_edicao_aberto = False

    async def editar_antepassado(self, form_data: dict):
        with rx.session() as sessao:
            reg = sessao.exec(Antepassado.select().where(Antepassado.id == self.antepassado_editando.id)).first()
            if reg:
                reg.nome_completo = form_data.get("nome_completo")
                reg.vinculo = self.vinculo_selecionado
                reg.linhagem = form_data.get("linhagem", "Não aplicável")
                sessao.add(reg)
                sessao.commit()
        self.modal_edicao_aberto = False
        await self.carregar_dados()
        yield rx.toast.success("Atualizado!")

def renderizar_linha(antepassado: Antepassado):
    return rx.table.row(
        rx.table.cell(antepassado.nome_completo),
        rx.table.cell(antepassado.vinculo),
        rx.table.cell(antepassado.linhagem),
        rx.table.cell(
            rx.hstack(
                rx.icon("pencil", size=18, cursor="pointer", on_click=lambda: EstadoCadastro.abrir_modal_edicao(antepassado), color="blue"),
                rx.icon("trash-2", size=18, cursor="pointer", on_click=lambda: EstadoCadastro.excluir_registo(antepassado.id), color="red"),
            )
        ),
    )

def label_input(label, component):
    return rx.vstack(
        rx.text(label, size="1", weight="bold", color_scheme="gray", margin_bottom="-0.5em"),
        component, width="100%", spacing="2",
    )

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
                                        # Cabeçalho do Perfil (Com espaçamento corrigido)
                                        rx.hstack(
                                            rx.avatar(src=AuthState.usuario_atual.foto, fallback=AuthState.usuario_atual.nome_real[0], size="5"),
                                            rx.vstack(
                                                rx.text("Sua Foto de Perfil", weight="bold", size="2"),
                                                rx.button(
                                                    rx.cond(EstadoCadastro.is_editing_photo, "Cancelar Alteração", "Alterar Foto"),
                                                    on_click=EstadoCadastro.alternar_edicao_foto,
                                                    size="1", variant="ghost", color_scheme="blue"
                                                ),
                                                spacing="1", # Espaço entre texto e botão
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

                            # Cabeçalho Principal (Com Botão Lápis)
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
                            
                            rx.form(
                                rx.vstack(
                                    rx.input(name="nome_completo", placeholder="Nome do Espírito", width="100%"),
                                    rx.select(["Tataravô", "Tataravó", "Bisavô", "Bisavó", "Avô", "Avó", "Pai", "Mãe", "Tio", "Tia", "Irmão", "Irmã", "Primo", "Prima", "Amigo(a)", "Outro"], placeholder="Selecione o Vínculo", on_change=EstadoCadastro.set_vinculo_selecionado, width="100%"),
                                    rx.center(rx.radio(["Materna", "Paterna"], name="linhagem", direction="row", spacing="4"), width="100%"),
                                    rx.button("Salvar Registro", type="submit", size="3", color_scheme="blue", width="100%", margin_top="1em"),
                                    spacing="4", align="center",
                                ),
                                on_submit=EstadoCadastro.salvar_antepassado, reset_on_submit=True, width="100%", max_width="480px",
                            ),
                            
                            rx.box(
                                rx.vstack(
                                    rx.text(f"Total de registos: {EstadoCadastro.total_registos}", weight="bold", text_align="center"),
                                    rx.table.root(
                                        rx.table.header(rx.table.row(rx.table.column_header_cell("Espírito"), rx.table.column_header_cell("Vínculo"), rx.table.column_header_cell("Linhagem"), rx.table.column_header_cell("Ações"))),
                                        rx.table.body(rx.foreach(EstadoCadastro.lista_antepassados, renderizar_linha)),
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
