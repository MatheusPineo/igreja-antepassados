import reflex as rx
from reflex_google_auth import GoogleAuthState
from .models import Usuario
import hashlib

class AuthState(GoogleAuthState):
    email: str = ""
    senha: str = ""
    confirmar_senha: str = ""
    nome_completo: str = ""
    aceitou_termos: bool = False
    mostrar_senha: bool = False
    mostrar_confirmar_senha: bool = False
    esta_logado: bool = False

    def set_email(self, email: str): self.email = email
    def set_senha(self, senha: str): self.senha = senha
    def set_confirmar_senha(self, senha: str): self.confirmar_senha = senha
    def set_nome_completo(self, nome: str): self.nome_completo = nome
    def set_aceitou_termos(self, val: bool): self.aceitou_termos = val

    @rx.var
    def forca_senha(self) -> str:
        if len(self.senha) < 6: return "Fraca"
        if any(c.isdigit() for c in self.senha) and any(c.isupper() for c in self.senha): return "Forte"
        return "Média"

    def alternar_mostrar_senha(self):
        self.mostrar_senha = not self.mostrar_senha

    def alternar_mostrar_confirmar_senha(self):
        self.mostrar_confirmar_senha = not self.mostrar_confirmar_senha

    def login_email(self):
        with rx.session() as sessao:
            senha_hash = hashlib.sha256(self.senha.encode()).hexdigest()
            user = sessao.exec(Usuario.select().where(Usuario.email == self.email, Usuario.senha_hash == senha_hash)).first()
            if user:
                self.esta_logado = True
                return rx.toast.success("Login realizado!")
            else:
                return rx.toast.error("Credenciais inválidas.")

    def registrar_email(self):
        if not self.aceitou_termos:
            return rx.toast.error("Você deve aceitar os termos.")
        if self.senha != self.confirmar_senha:
            return rx.toast.error("As senhas não coincidem.")

        with rx.session() as sessao:
            exists = sessao.exec(Usuario.select().where(Usuario.email == self.email)).first()
            if exists:
                return rx.toast.error("Email já cadastrado.")

            senha_hash = hashlib.sha256(self.senha.encode()).hexdigest()
            novo_usuario = Usuario(nome_completo=self.nome_completo, email=self.email, senha_hash=senha_hash, aceitou_termos=self.aceitou_termos)
            sessao.add(novo_usuario)
            sessao.commit()
            self.esta_logado = True
            return rx.toast.success("Conta criada! Verifique seu email.")

# ... (restante do código original)


    @rx.var
    def usuario_atual(self) -> Usuario:
        if self.token_is_valid:
            email = self.tokeninfo.get("email")
            nome = self.tokeninfo.get("name")
            gid = self.tokeninfo.get("sub")
            with rx.session() as sessao:
                user = sessao.exec(Usuario.select().where(Usuario.google_id == gid)).first()
                if not user:
                    user = Usuario(nome=nome, email=email, google_id=gid)
                    sessao.add(user)
                    sessao.commit()
                    sessao.refresh(user)
                return user
        
        # Lógica para logado por email (implementação simplificada)
        if self.esta_logado:
             with rx.session() as sessao:
                return sessao.exec(Usuario.select().where(Usuario.email == self.email)).first()
                
        return Usuario(nome="", email="", google_id="")

    @rx.var
    def perfil_incompleto(self) -> bool:
        user = self.usuario_atual
        return user.nome_real == "" or user.tipo_usuario == ""

