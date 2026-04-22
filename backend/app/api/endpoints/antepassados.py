from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from typing import List
import io
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from ...core.database import get_session
from ...models.usuario import Usuario
from ...models.antepassado import Antepassado

router = APIRouter()

@router.get("/{usuario_id}", response_model=List[Antepassado])
def list_antepassados(usuario_id: int, session: Session = Depends(get_session)):
    antepassados = session.exec(select(Antepassado).where(Antepassado.usuario_id == usuario_id)).all()
    return antepassados

@router.post("/")
def create_antepassado(data: Antepassado, session: Session = Depends(get_session)):
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

@router.delete("/{id}")
def delete_antepassado(id: int, session: Session = Depends(get_session)):
    item = session.get(Antepassado, id)
    if not item:
        raise HTTPException(status_code=404, detail="Não encontrado")
    session.delete(item)
    session.commit()
    return {"message": "Removido"}

@router.get("/exportar-pdf/{usuario_id}")
def export_pdf(usuario_id: int, session: Session = Depends(get_session)):
    user = session.get(Usuario, usuario_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    antepassados = session.exec(select(Antepassado).where(Antepassado.usuario_id == usuario_id)).all()
    
    def get_sort_key(ant: Antepassado):
        prioridade_vinculo = {
            "Tataravô": 1, "Tataravó": 1, "Bisavô": 2, "Bisavó": 2, "Avô": 3, "Avó": 3,
            "Pai": 4, "Mãe": 5, "Cônjuge": 6, 
            "Filho": 7, "Filha": 7, "Neto": 8, "Neta": 8, "Bisneto": 9, "Bisneta": 9,
            "Tio-avô": 10, "Tia-avó": 10, "Tio": 11, "Tia": 11, "Irmão": 12, "Irmã": 12,
            "Sobrinho": 13, "Sobrinha": 13, "Primo": 14, "Prima": 14, 
            "Sogro": 15, "Sogra": 15, "Cunhado": 16, "Cunhada": 16, 
            "Padrasto": 17, "Madrasta": 17, "Enteado": 18, "Enteada": 18,
            "Parente afim": 19, "Amigo": 20, "Amiga": 20, "Outro": 21
        }
        prioridade_linhagem = {"Paterna": 1, "Materna": 2, "Não aplicável": 3}
        
        if user.sexo == "Masculino":
            prioridade_familia = {"Minha Família": 1, "Família do Cônjuge": 2}
        else:
            prioridade_familia = {"Família do Cônjuge": 1, "Minha Família": 2}
            
        p_fam = prioridade_familia.get(ant.familia, 3)
        p_vin = prioridade_vinculo.get(ant.vinculo, 99)
        p_lin = prioridade_linhagem.get(ant.linhagem, 3)
        return (p_fam, p_vin, p_lin)

    lista_ordenada = sorted(antepassados, key=get_sort_key)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Busca a imagem na raiz do projeto
    image_path = os.path.join(os.getcwd(), "assets", "form_template.png")
    if os.path.exists(image_path):
        c.drawImage(image_path, 0, 0, width=210*mm, height=297*mm, preserveAspectRatio=True)

    c.setFont("Helvetica", 9)
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M:%S")

    largura_a4, altura_a4 = A4
    centro_x = largura_a4 / 2.0

    c.setFont("Helvetica", 13)
    ano_atual = datetime.now().strftime("%Y")
    cidade = user.igreja if user.igreja and user.igreja != "Não aplicável" else "Guimarães"
    c.drawCentredString(centro_x, 20*mm, f"{cidade}, 02 de novembro de {ano_atual}") 

    c.setFont("Helvetica", 9)
    c.drawString(20*mm, 15*mm, f"Nome: {user.nome_real} {user.sobrenome} ({user.estado_civil})")
    c.drawString(20*mm, 10*mm, f"Igreja: {user.igreja}")
    c.drawString(20*mm, 5*mm, f"Enviado em {data_hoje} às {hora_atual}")

    c.drawRightString(195*mm, 5*mm, "Página 1/1")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, 218*mm, "Nome Espírito/Família")
    c.drawString(140*mm, 218*mm, "Parentesco / Linhagem / Família")
    
    c.setFont("Helvetica", 10)
    y_pos = 205*mm 
    
    for ant in lista_ordenada:
        if y_pos < 60*mm:
            break 
        c.drawString(20*mm, y_pos, ant.nome_completo)
        c.drawString(140*mm, y_pos, f"{ant.vinculo} ({ant.linhagem}) - {ant.familia}")
        y_pos -= 6*mm 

    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    
    headers = {
        'Content-Disposition': f'attachment; filename="registro_{usuario_id}.pdf"'
    }
    return Response(content=pdf_data, media_type="application/pdf", headers=headers)
