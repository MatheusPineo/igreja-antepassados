import reflex as rx

class Usuario(rx.Model, table=True):
    nome_completo: str = ""
    email: str = ""
    google_id: str = ""
    senha_hash: str = ""
    aceitou_termos: bool = False
    nome_real: str = ""
    sobrenome: str = ""
    tipo_usuario: str = "" 
    igreja: str = "" 
    foto: str = "" 
    estado_civil: str = "Solteiro(a)"
    sexo: str = "Masculino"

class Antepassado(rx.Model, table=True):
    nome_completo: str
    vinculo: str
    linhagem: str
    familia: str = "Minha Família"
    usuario_id: int
