from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import auth, antepassados, usuarios
from .core.database import engine
from sqlmodel import SQLModel
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Igreja Messiânica - API")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server connection error"}
    )

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_coop_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    return response

# Criar tabelas ao iniciar (simples para este projeto)
# No Vercel, eventos on_startup podem não disparar de forma confiável no adaptador ASGI.
# Vamos garantir a criação das tabelas no import ou na conexão.
SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    pass

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
