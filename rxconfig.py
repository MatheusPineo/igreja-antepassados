import reflex as rx
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

db_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = rx.Config(
    app_name="projeto_messianica",
    db_url=db_url,
    # Durante o desenvolvimento local, o ideal é deixar o Reflex gerenciar a URL automaticamente
    # api_url="https://igreja-antepassados.onrender.com",
)