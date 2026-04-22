from sqlmodel import SQLModel, Field
from typing import Optional

class Antepassado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome_completo: str
    vinculo: str
    linhagem: str
    familia: str = "Minha Família"
    usuario_id: int
