import os
import sys
from sqlmodel import create_engine, Session, select
import bcrypt
from backend.app.models.usuario import Usuario

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

# URL de Conexão do Supabase Produção
SUPABASE_DB_URL = "postgresql://postgres:wfhknq8abcvzqvi9sh@db.ghvnkwiwochirnjeefyh.supabase.co:5432/postgres"

EMAIL_ALVO = "matheuskrx@gmail.com"

# Senha provisória. Se desejar, sinta-se à vontade para alterar esta string antes de rodar.
NOVA_SENHA = "Mudar@123"

def set_hybrid_password():
    engine = create_engine(SUPABASE_DB_URL)
    
    with Session(engine) as session:
        user = session.exec(select(Usuario).where(Usuario.email == EMAIL_ALVO)).first()
        
        if not user:
            print(f"Erro: Usuário {EMAIL_ALVO} não encontrado no Supabase.")
            sys.exit(1)
            
        print(f"Usuário encontrado! Nome: {user.nome_completo}")
        
        if user.senha_hash:
            print("Aviso: O usuário já possui uma senha hash (talvez já seja híbrido). Sobrescrevendo...")
        
        # 1. Gerar o hash seguro usando o Bcrypt nativo do sistema
        hashed_password = get_password_hash(NOVA_SENHA)
        
        # 2. Injetar o novo Hash
        user.senha_hash = hashed_password
        
        # 3. Commitar transação
        session.add(user)
        session.commit()
        
        print(f"\n✅ SUCESSO! A conta de {EMAIL_ALVO} agora é híbrida.")
        print(f"Você já pode testar o Login Tradicional na aplicação usando a senha: {NOVA_SENHA}")

if __name__ == "__main__":
    set_hybrid_password()
