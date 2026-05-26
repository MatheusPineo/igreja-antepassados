from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Caminho absoluto para o banco de dados na raiz do projeto (se for SQLite)
# Para SQLite no Render ou local, é melhor garantir o caminho correto.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/reflex.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Conversão automática e transparente do host direto IPv6 do Supabase para o Pooler IPv4 no Render
if "db.ghvnkwiwochirnjeefyh.supabase.co" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        "db.ghvnkwiwochirnjeefyh.supabase.co:5432", 
        "aws-1-eu-central-1.pooler.supabase.com:6543"
    )
    if "postgres:" in DATABASE_URL and "postgres.ghvnkwiwochirnjeefyh" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgres:", "postgres.ghvnkwiwochirnjeefyh:", 1)

engine_kwargs = {}
if "sqlite" not in DATABASE_URL:
    engine_kwargs = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    }
else:
    engine_kwargs = {
        "connect_args": {"check_same_thread": False}
    }

engine = create_engine(DATABASE_URL, echo=True, **engine_kwargs)

def get_session():
    with Session(engine) as session:
        yield session
