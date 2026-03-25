import reflex as rx

class Usuario(rx.Model, table=True):
    """Tabela de usuários para o backup e login social."""
    nome: str
    email: str
    google_id: str

class Antepassado(rx.Model, table=True):
    """Tabela que armazena os espíritos dos antepassados."""
    nome_completo: str
    vinculo: str  # Ex: Avô, Avó, Tio
    linhagem: str  # Ex: Materna, Paterna
    usuario_id: int  # Conecta este antepassado ao ID do usuário que o cadastrou

# Inicialização obrigatória do aplicativo Reflex
app = rx.App()