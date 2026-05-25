import os
import sys
from sqlmodel import create_engine, Session, select, SQLModel
from backend.app.models.usuario import Usuario
from backend.app.models.antepassado import Antepassado

LOCAL_DB_URL = "sqlite:///reflex.db"
SUPABASE_DB_URL = "postgresql://postgres:wfhknq8abcvzqvi9sh@db.ghvnkwiwochirnjeefyh.supabase.co:5432/postgres"

local_engine = create_engine(LOCAL_DB_URL)
supabase_engine = create_engine(SUPABASE_DB_URL)

def migrate():
    print("Iniciando migração...")
    
    print("Criando tabelas no Supabase...")
    SQLModel.metadata.create_all(supabase_engine)
    
    with Session(local_engine) as local_session, Session(supabase_engine) as supabase_session:
        local_user = local_session.exec(select(Usuario).where(Usuario.email == "matheuskrx@gmail.com")).first()
        
        if not local_user:
            print("Usuário local não encontrado.")
            sys.exit(1)
            
        print(f"Usuário local encontrado: {local_user.email} (ID: {local_user.id})")
        
        supabase_user = supabase_session.exec(select(Usuario).where(Usuario.email == local_user.email)).first()
        
        if not supabase_user:
            print("Inserindo usuário no Supabase...")
            supabase_user = Usuario(
                nome_completo=local_user.nome_completo,
                email=local_user.email,
                google_id=local_user.google_id,
                senha_hash=local_user.senha_hash,
                aceitou_termos=local_user.aceitou_termos,
                nome_real=local_user.nome_real,
                sobrenome=local_user.sobrenome,
                tipo_usuario=local_user.tipo_usuario,
                igreja=local_user.igreja,
                foto=local_user.foto,
                estado_civil=local_user.estado_civil,
                sexo=local_user.sexo
            )
            supabase_session.add(supabase_user)
            supabase_session.commit()
            supabase_session.refresh(supabase_user)
            print(f"Usuário migrado com sucesso. Novo ID Supabase: {supabase_user.id}")
        else:
            print(f"Usuário já existe no Supabase (ID: {supabase_user.id}).")
            
        local_antepassados = local_session.exec(select(Antepassado).where(Antepassado.usuario_id == local_user.id)).all()
        print(f"Encontrados {len(local_antepassados)} antepassados no banco local.")
        
        count = 0
        for local_ant in local_antepassados:
            existing_ant = supabase_session.exec(
                select(Antepassado).where(
                    Antepassado.usuario_id == supabase_user.id,
                    Antepassado.nome_completo == local_ant.nome_completo,
                    Antepassado.vinculo == local_ant.vinculo
                )
            ).first()
            
            if not existing_ant:
                new_ant = Antepassado(
                    nome_completo=local_ant.nome_completo,
                    vinculo=local_ant.vinculo,
                    linhagem=local_ant.linhagem,
                    familia=local_ant.familia,
                    usuario_id=supabase_user.id
                )
                supabase_session.add(new_ant)
                count += 1
                
        if count > 0:
            supabase_session.commit()
            print(f"Sucesso! {count} antepassados migrados para o Supabase.")
        else:
            print("Nenhum novo antepassado para migrar (provavelmente já foram migrados).")
            
    print("Migração concluída com sucesso!")

if __name__ == "__main__":
    migrate()
