import reflex as rx
from .models import Usuario, Antepassado
from .auth import AuthState
import base64
import io
from PIL import Image
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from .constants import TIPOS_USUARIO, IGREJAS, VINCULOS_ANTEPASSADOS, LINHAGENS, ESTADOS_CIVIS, SEXOS, FAMILIAS

class EstadoCadastro(rx.State):
    lista_antepassados: list[Antepassado] = []
    vinculo_selecionado: str = "" 
    antepassado_editando: Antepassado = Antepassado() 
    modal_edicao_aberto: bool = False
    
    tipo_usuario_selecionado: str = ""
    estado_civil_selecionado: str = ""
    sexo_selecionado: str = ""
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
        sem_linhagem = ["Pai", "Mãe", "Irmão", "Irmã", "Amigo(a)", "Outro", "Cônjuge", "Filho(a)", "Neto(a)", "Bisneto(a)"]
        return self.vinculo_selecionado in sem_linhagem

    @rx.var
    def eh_membro(self) -> bool:
        return self.tipo_usuario_selecionado == "Membro"

    @rx.var
    def mostrando_editor(self) -> bool:
        return self.temp_img_base64 != ""

    async def abrir_modal_perfil(self):
        from .projeto_messianica import AuthState
        auth = await self.get_state(AuthState)
        self.tipo_usuario_selecionado = auth.usuario_atual.tipo_usuario
        self.estado_civil_selecionado = auth.usuario_atual.estado_civil
        self.sexo_selecionado = auth.usuario_atual.sexo
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
        from .projeto_messianica import AuthState
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
        from .projeto_messianica import AuthState
        auth = await self.get_state(AuthState)
        with rx.session() as sessao:
            user = sessao.exec(Usuario.select().where(Usuario.id == auth.usuario_atual.id)).first()
            if user:
                user.foto = ""
                sessao.add(user)
                sessao.commit()
        yield rx.toast.success("Foto removida.")

    async def salvar_perfil(self, form_data: dict):
        from .projeto_messianica import AuthState
        auth = await self.get_state(AuthState)
        nome_real = form_data.get("nome_real")
        sobrenome = form_data.get("sobrenome")
        tipo = self.tipo_usuario_selecionado
        estado_civil = self.estado_civil_selecionado
        sexo = self.sexo_selecionado
        igreja = form_data.get("igreja", "") if tipo == "Membro" else "Não aplicável"
        with rx.session() as sessao:
            user = sessao.exec(Usuario.select().where(Usuario.id == auth.usuario_atual.id)).first()
            if user:
                user.nome_real = nome_real
                user.sobrenome = sobrenome
                user.tipo_usuario = tipo
                user.estado_civil = estado_civil
                user.sexo = sexo
                user.igreja = igreja
                sessao.add(user)
                sessao.commit()
        self.modal_perfil_aberto = False
        await self.carregar_dados()
        yield rx.toast.success("Perfil atualizado!")

    async def carregar_dados(self):
        from .projeto_messianica import AuthState
        auth = await self.get_state(AuthState)
        if not auth.token_is_valid or auth.perfil_incompleto:
            self.lista_antepassados = []
            return
        with rx.session() as sessao:
            self.lista_antepassados = sessao.exec(
                Antepassado.select().where(Antepassado.usuario_id == auth.usuario_atual.id)
            ).all()

    async def salvar_antepassado(self, form_data: dict):
        from .projeto_messianica import AuthState
        auth = await self.get_state(AuthState)
        nome = form_data.get("nome_completo")
        vinculo = self.vinculo_selecionado
        linhagem = form_data.get("linhagem", "Não aplicável") if not self.desabilita_linhagem else "Não aplicável"
        familia = form_data.get("familia", "Minha Família")
        with rx.session() as sessao:
            novo = Antepassado(nome_completo=nome, vinculo=vinculo, linhagem=linhagem, familia=familia, usuario_id=auth.usuario_atual.id)
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
                reg.familia = form_data.get("familia", "Minha Família")
                sessao.add(reg)
                sessao.commit()
        self.modal_edicao_aberto = False
        await self.carregar_dados()
        yield rx.toast.success("Atualizado!")

    def ordenar_espiritos(self, lista: list[Antepassado], user: Usuario) -> list[Antepassado]:
        # Prioridades de Vínculo conforme as regras
        prioridade_vinculo = {
            "Tataravô": 1, "Tataravó": 1,
            "Bisavô": 2, "Bisavó": 2,
            "Avô": 3, "Avó": 3,
            "Pai": 4, "Mãe": 5,
            "Cônjuge": 6,
            "Filho(a)": 7,
            "Neto(a)": 8,
            "Bisneto(a)": 9,
            "Tio-avô": 10, "Tia-avó": 10,
            "Tio": 11, "Tia": 11,
            "Irmão": 12, "Irmã": 12,
            "Sobrinho(a)": 13,
            "Primo": 14, "Prima": 14,
            "Sogro": 15, "Sogra": 15, "Cunhado(a)": 15, "Padrasto": 15, "Madrasta": 15, "Enteado(a)": 15, "Parente afim": 15,
            "Amigo(a)": 16,
            "Outro": 17
        }
        
        # Prioridade de Linhagem: Paterna -> Materna
        prioridade_linhagem = {"Paterna": 1, "Materna": 2, "Não aplicável": 3}
        
        # Regra de Acoplamento: Marido primeiro
        # Se o usuário for Masculino, "Minha Família" é do marido.
        # Se o usuário for Feminino, "Família do Cônjuge" é do marido.
        prioridade_familia = {}
        if user.sexo == "Masculino":
            prioridade_familia = {"Minha Família": 1, "Família do Cônjuge": 2}
        else:
            prioridade_familia = {"Família do Cônjuge": 1, "Minha Família": 2}

        def chave_ordenacao(ant: Antepassado):
            # 1. Família (Marido antes de Esposa)
            p_fam = prioridade_familia.get(ant.familia, 3)
            # 2. Vínculo (Ancestrais -> Descendentes -> Colaterais)
            p_vin = prioridade_vinculo.get(ant.vinculo, 99)
            # 3. Linhagem (Paterna antes de Materna) dentro de cada nível
            p_lin = prioridade_linhagem.get(ant.linhagem, 3)
            
            return (p_fam, p_vin, p_lin)

        return sorted(lista, key=chave_ordenacao)

    async def exportar_pdf(self):
            print("--- Chamada de exportar_pdf iniciada com nova ordenação ---")
            from .projeto_messianica import AuthState
            from reportlab.pdfgen import canvas
            import io
            auth = await self.get_state(AuthState)
            user = auth.usuario_atual

            # Validação de abreviações e abortos
            avisos = []
            for ant in self.lista_antepassados:
                if "." in ant.nome_completo:
                    avisos.append(f"Aviso: O nome '{ant.nome_completo}' parece conter abreviações. Por favor, corrija para o nome completo.")
                if "aborto" in ant.nome_completo.lower():
                    avisos.append(f"ALERTA CRÍTICO: Menção de 'aborto' encontrada em '{ant.nome_completo}'. Consulte o ministro ou coordenador responsável para a normativa correta.")

            if avisos:
                for aviso in avisos:
                    yield rx.toast.warning(aviso)

            lista_ordenada = self.ordenar_espiritos(self.lista_antepassados, user)

            buffer = io.BytesIO()
            try:
                c = canvas.Canvas(buffer, pagesize=A4)
                image_path = "assets/form_template.png"
                if os.path.exists(image_path):
                    c.drawImage(image_path, 0, 0, width=210*mm, height=297*mm, preserveAspectRatio=True)

                c.setFont("Helvetica", 9)
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                hora_atual = datetime.now().strftime("%H:%M:%S")

                largura_a4, altura_a4 = A4
                centro_x = largura_a4 / 2.0

                c.setFont("Helvetica", 13)
                ano_atual = datetime.now().strftime("%Y")
                cidade = user.igreja if user.igreja and user.igreja != "Não aplicável" else "Cidade"
                c.drawCentredString(centro_x, 20*mm, f"{cidade}, 02 de novembro de {ano_atual}") 

                c.setFont("Helvetica", 9)
                c.drawString(20*mm, 15*mm, f"Nome: {user.nome_real} {user.sobrenome} ({user.estado_civil})")
                c.drawString(20*mm, 10*mm, f"Igreja: {user.igreja}")
                c.drawString(20*mm, 5*mm, f"Enviado em {data_hoje} às {hora_atual}")

                c.drawRightString(195*mm, 5*mm, "Página 1/1")

                c.setFont("Helvetica-Bold", 10)
                c.drawString(20*mm, 218*mm, "Nome Espírito/Família")
                c.drawString(140*mm, 218*mm, "Parentesco / Linhagem / Família")
                
                c.setFont("Helvetica", 10)
                y_pos = 205*mm 
                
                for ant in lista_ordenada:
                    if y_pos < 60*mm:
                        break 
                        
                    c.drawString(20*mm, y_pos, ant.nome_completo)
                    c.drawString(140*mm, y_pos, f"{ant.vinculo} ({ant.linhagem}) - {ant.familia}")
                    y_pos -= 6*mm 

                c.save()
                pdf_data = buffer.getvalue()
                buffer.close()
            except Exception as e:
                print(f"ERRO GERAL na geração: {e}")
                yield rx.toast.error(f"Ocorreu um erro ao gerar o PDF.")
                return
            
            timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            nome_arquivo = f"{user.nome_real}_{user.sobrenome}_{timestamp}.pdf".replace(" ", "_").replace(":", "-")

            yield rx.download(data=pdf_data, filename=nome_arquivo)


