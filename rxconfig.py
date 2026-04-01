import reflex as rx
import os

db_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = rx.Config(
    app_name="projeto_messianica",
    db_url=db_url,
    api_url="https://igreja-antepassados.onrender.com",
    deploy_url="https://igreja-antepassados.onrender.com",
)