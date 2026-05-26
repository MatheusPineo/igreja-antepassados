from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ...core.database import get_session
from ...core.security import get_current_user
from ...models.usuario import Usuario

router = APIRouter()

@router.get("/me")
def get_usuario(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.put("/me")
def update_usuario(
    data: dict, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    db_user = session.get(Usuario, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    for key, value in data.items():
        if hasattr(db_user, key) and key not in ["id", "senha_hash", "email", "google_id"]:
            setattr(db_user, key, value)
            
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
