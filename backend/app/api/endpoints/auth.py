from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from ...core.database import get_session
from ...core.security import verify_password, get_password_hash, create_access_token
from ...models.usuario import Usuario

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "983253662992-bqhudth57f6kq9cdu2s7kli29t23rb5h.apps.googleusercontent.com")

@router.post("/google")
def google_auth(token_data: dict, session: Session = Depends(get_session)):
    token = token_data.get("credential")
    if not token:
        raise HTTPException(status_code=400, detail="Token não fornecido")

    try:
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        except ValueError:
            raise HTTPException(status_code=401, detail="Token do Google inválido")
            
        google_id = idinfo.get('sub')
        email = idinfo.get('email')
        name = idinfo.get('name', '')

        if not google_id or not email:
            raise HTTPException(status_code=400, detail="O token do Google não contém as informações necessárias (email/sub)")

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

        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "nome_real": user.nome_real,
                "igreja": user.igreja,
                "tipo_usuario": user.tipo_usuario
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"CRITICAL ERROR IN AUTH GOOGLE: {e}", flush=True)
        logger.error(f"Google Auth Database Crash: {str(e)}")
        raise HTTPException(status_code=500, detail="DB_CRASH")

@router.post("/login")
def login(data: dict, session: Session = Depends(get_session)):
    email = data.get("email")
    senha = data.get("password")
    user = session.exec(select(Usuario).where(Usuario.email == email)).first()
    
    if not user or not verify_password(senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
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
        senha_hash=get_password_hash(data.get("password")),
        aceitou_termos=data.get("aceitou_termos", True)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome_completo": user.nome_completo,
            "email": user.email,
            "nome_real": user.nome_real,
            "igreja": user.igreja,
            "tipo_usuario": user.tipo_usuario
        }
    }
