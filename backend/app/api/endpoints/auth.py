from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import hashlib
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from ...core.database import get_session
from ...models.usuario import Usuario

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "983253662992-bqhudth57f6kq9cdu2s7kli29t23rb5h.apps.googleusercontent.com")

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/google")
def google_auth(token_data: dict, session: Session = Depends(get_session)):
    token = token_data.get("credential")
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')

        user = session.exec(select(Usuario).where(Usuario.google_id == google_id)).first()
        if not user:
            user = session.exec(select(Usuario).where(Usuario.email == email)).first()
            if user:
                user.google_id = google_id
            else:
                user = Usuario(
                    nome_completo=name,
                    email=email,
                    google_id=google_id,
                    aceitou_termos=True
                )
            session.add(user)
            session.commit()
            session.refresh(user)

        return {
            "user": {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "nome_real": user.nome_real,
                "igreja": user.igreja,
                "tipo_usuario": user.tipo_usuario
            }
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Token do Google inválido")

@router.post("/login")
def login(data: dict, session: Session = Depends(get_session)):
    email = data.get("email")
    senha = data.get("password")
    user = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not user or user.senha_hash != hash_password(senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {
        "user": {
            "id": user.id,
            "nome_completo": user.nome_completo,
            "email": user.email,
            "nome_real": user.nome_real,
            "igreja": user.igreja,
            "tipo_usuario": user.tipo_usuario
        }
    }

@router.post("/register")
def register(data: dict, session: Session = Depends(get_session)):
    email = data.get("email")
    # Verificar se já existe
    existing = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
        
    user = Usuario(
        nome_completo=data.get("nome_completo"),
        email=email,
        senha_hash=hash_password(data.get("password")),
        aceitou_termos=data.get("aceitou_termos", True)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Usuário criado com sucesso"}
