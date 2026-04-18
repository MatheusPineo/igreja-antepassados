import reflex as rx
from reflex_google_auth import GoogleAuthState
from .models import Usuario

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
