from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ...core.database import get_session
from ...models.usuario import Usuario

router = APIRouter()

@router.get("/{id}")
def get_usuario(id: int, session: Session = Depends(get_session)):
    user = session.get(Usuario, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/{id}")
def update_usuario(id: int, data: dict, session: Session = Depends(get_session)):
    user = session.get(Usuario, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
            
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
