from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Caminho absoluto para o banco de dados na raiz do projeto (se for SQLite)
# Para SQLite no Render ou local, é melhor garantir o caminho correto.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reflex.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
