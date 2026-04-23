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
    try:
        antepassados = session.exec(select(Antepassado).where(Antepassado.usuario_id == usuario_id)).all()
        return antepassados
    except Exception as e:
        raise e

@router.post("/")
def create_antepassado(data: Antepassado, session: Session = Depends(get_session)):
    if data.vinculo in ["Amigo", "Amiga", "Outro"]:
        data.linhagem = "Não aplicável"
        data.familia = "Não aplicável"
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
    
    hierarquia = [
        "Tataravô", "Tataravó", "Bisavô", "Bisavó", "Avô", "Avó", "Pai", "Mãe", "Cônjuge",
        "Filhos(as)", "Netos(as)", "Tio-avô", "Tia-avó", "Tio", "Tia",
        "Irmão", "Irmã", "Sobrinho", "Sobrinha", "Primo", "Prima",
        "Parentes afins", "Amigo", "Amiga", "Outro"
    ]

    def processar_lote(lista_bruta):
        lote_ordenado = []
        for cat in hierarquia:
            itens = [a for a in lista_bruta if a.vinculo == cat]
            for ant in itens:
                nome = ant.nome_completo
                alerta = " [ALERTA: Nome abreviado]" if any(p.endswith('.') for p in nome.split()) else ""
                lote_ordenado.append({"ant": ant, "nome": f"{nome}{alerta}"})
        return lote_ordenado

    lote_titular = processar_lote([a for a in antepassados if a.familia == "Minha Família"])
    lote_outro = processar_lote([a for a in antepassados if a.familia != "Minha Família"])

    final_list = []
    if user.estado_civil in ["Casado(a)", "Viúvo(a)"]:
        final_list = lote_titular + [{"separador": "--- LINHAGEM DO CÔNJUGE ---"}] + lote_outro
    elif user.estado_civil == "Separado(a)":
        final_list = lote_titular + [{"separador": "--- LINHAGEM DO EX-CÔNJUGE ---"}] + lote_outro
    else:
        final_list = lote_titular

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    image_path = os.path.join(os.getcwd(), "assets", "form_template.png")
    
    def draw_page_base(page_num, total):
        if os.path.exists(image_path):
            c.drawImage(image_path, 0, 0, width=210*mm, height=297*mm, preserveAspectRatio=True)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20*mm, 218*mm, "Nome Espírito")
        c.drawString(140*mm, 218*mm, "Vinculo / Linhagem / Família")
        c.setFont("Helvetica", 9)
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        hora_atual = datetime.now().strftime("%H:%M:%S")
        c.drawCentredString(105*mm, 21*mm, f"{user.igreja}, 02 de novembro de 2026")
        c.drawString(20*mm, 15*mm, f"Nome: {user.nome_real} {user.sobrenome} - {user.estado_civil}")
        c.drawString(20*mm, 10*mm, f"Igreja: {user.igreja}")
        c.drawString(20*mm, 5*mm, f"Enviado em {data_hoje} às {hora_atual}")
        c.drawRightString(195*mm, 5*mm, f"Página {page_num}/{total}")

    y_pos = 212*mm
    page_num = 1
    total = (len(final_list) // 31) + 1
    
    draw_page_base(page_num, total)
    c.setFont("Helvetica", 10)
    for item in final_list:
        if y_pos < 30*mm:
            c.showPage()
            page_num += 1
            draw_page_base(page_num, total)
            y_pos = 212*mm
        
        if "separador" in item:
            y_pos -= 6*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, y_pos, item["separador"])
            y_pos -= 6*mm
            c.setFont("Helvetica", 10)
        elif "ant" in item:
            ant = item["ant"]
            c.drawString(20*mm, y_pos, item.get("nome", ""))
            c.drawString(140*mm, y_pos, f"{ant.vinculo} ({ant.linhagem})")
            y_pos -= 6*mm

    if any("aborto" in a.nome_completo.lower() for a in antepassados):
        y_pos -= 10*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20*mm, y_pos, "AVISO CRÍTICO: Consulte o ministro sobre nomes de abortos.")

    c.save()
    return Response(content=buffer.getvalue(), media_type="application/pdf")
