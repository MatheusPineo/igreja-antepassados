from sqlmodel import SQLModel, Field
from typing import Optional

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
