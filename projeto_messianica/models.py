import reflex as rx

class Usuario(rx.Model, table=True):
    nome: str 
    email: str 
    google_id: str
    nome_real: str = ""
    sobrenome: str = ""
    tipo_usuario: str = "" 
    igreja: str = "" 
    foto: str = "" 

class Antepassado(rx.Model, table=True):
    nome_completo: str
    vinculo: str
    linhagem: str
    usuario_id: int
