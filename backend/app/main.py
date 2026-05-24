from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import auth, antepassados, usuarios
from .core.database import engine
from sqlmodel import SQLModel

app = FastAPI(title="Igreja Messiânica - API")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar tabelas ao iniciar (simples para este projeto)
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Inclusão das rotas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(antepassados.router, prefix="/antepassados", tags=["antepassados"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API da Igreja Messiânica"}

@app.get("/ping")
def ping():
    """Endpoint público leve que realiza uma consulta rápida no banco para manter a infraestrutura ativa."""
    from sqlalchemy import text
    from fastapi.responses import PlainTextResponse
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return PlainTextResponse("ok", status_code=200)
    except Exception as e:
        return PlainTextResponse(f"error: {str(e)}", status_code=500)
