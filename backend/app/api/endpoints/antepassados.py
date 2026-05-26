from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import List
import io
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm

from ...core.database import get_session
from ...core.security import get_current_user
from ...models.usuario import Usuario
from ...models.antepassado import Antepassado

def get_ancestor_sort_key(vinculo: str, nome_completo: str = "") -> tuple:
    if not vinculo:
        return (9, 9, 999, "", "")
    
    vinculo_lower = vinculo.lower()
    nome_completo_lower = nome_completo.lower() if nome_completo else ""
    
    # 1. Determinação do bloco de linhagem (block_weight)
    is_marido = "marido" in vinculo_lower
    is_paterno = "paterno" in vinculo_lower
    is_materno = "materno" in vinculo_lower
    
    if is_marido:
        if is_paterno:
            block = 1  # 1. Linhagem Paterna do Marido
        elif is_materno:
            block = 2  # 2. Linhagem Materna do Marido
        else:
            block = 5
    else:
        if is_paterno:
            block = 3  # 3. Linhagem Paterna da Esposa
        elif is_materno:
            block = 4  # 4. Linhagem Materna da Esposa
        else:
            block = 5
            
    # 2. Categoria (category_weight): Tronco (Lineage Name) = 0 vs Membro Individual = 1
    # Regra de ouro: "Troncos" sempre antes dos membros individuais do bloco.
    is_tronco = "tronco" in vinculo_lower
    category = 0 if is_tronco else 1
    
    # 3. Hierarquia tradicional para desempate secundário (hierarchy_weight)
    parentescos = [
        "tataravô", "tataravó", "bisavô", "bisavó", "avô", "avó", "pai", "mãe", "cônjuge",
        "filhos(as)", "netos(as)", "tio-avô", "tia-avó", "tio", "tia",
        "irmão", "irmã", "sobrinho", "sobrinha", "primo", "prima",
        "parentes afins", "amigo", "amiga", "outro"
    ]
    
    hierarchy_weight = 999
    for idx, p in enumerate(parentescos):
        if p in vinculo_lower:
            hierarchy_weight = idx
            break
            
    return (block, category, hierarchy_weight, vinculo_lower, nome_completo_lower)

router = APIRouter()

@router.get("/", response_model=List[Antepassado])
def list_antepassados(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        antepassados = session.exec(select(Antepassado).where(Antepassado.usuario_id == current_user.id)).all()
        return sorted(antepassados, key=lambda a: get_ancestor_sort_key(a.vinculo, a.nome_completo))
    except Exception as e:
        raise e

@router.post("/")
def create_antepassado(
    data: Antepassado,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    if data.vinculo in ["Amigo", "Amiga", "Outro"]:
        data.linhagem = "Não aplicável"
        data.familia = "Não aplicável"
        
    data.usuario_id = current_user.id
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

@router.delete("/{id}")
def delete_antepassado(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    item = session.get(Antepassado, id)
    if not item:
        raise HTTPException(status_code=404, detail="Não encontrado")
    
    if item.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado a excluir este registro")
        
    session.delete(item)
    session.commit()
    return {"message": "Removido"}

def generate_pdf_flowable(session: Session, user: Usuario) -> io.BytesIO:
    antepassados = session.exec(select(Antepassado).where(Antepassado.usuario_id == user.id)).all()
    antepassados_ordenados = sorted(antepassados, key=lambda a: get_ancestor_sort_key(a.vinculo, a.nome_completo))
    
    buffer = io.BytesIO()
    
    # A4 tem dimensões 210 x 297 mm.
    # Ajustamos topMargin para 79mm e bottomMargin para 24mm para maximizar a utilização das pautas físicas
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=15*mm,
        topMargin=79*mm,
        bottomMargin=24*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilo de parágrafo único, preto puro e peso regular
    normal_style = ParagraphStyle(
        'AncestorNormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.black
    )

    story = []
    data_rows = []
    
    for a in antepassados_ordenados:
        nome = a.nome_completo
        alerta = " [ALERTA: Nome abreviado]" if any(p.endswith('.') for p in nome.split()) else ""
        nome_completo_com_alerta = f"{nome}{alerta}"
        
        name_p = Paragraph(nome_completo_com_alerta, normal_style)
        vinculo_p = Paragraph(a.vinculo, normal_style)
        data_rows.append([name_p, vinculo_p])
        
    if data_rows:
        # colWidths: Coluna 1 (Nome) tem 120mm. Coluna 2 (Vínculo) ocupa o restante da largura útil (55mm).
        # rowHeights: Fixados em exatamente 6mm por linha para coincidir com as pautas físicas do papel.
        t = Table(data_rows, colWidths=[120*mm, 55*mm], rowHeights=6*mm)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("Nenhum antepassado cadastrado.", normal_style))
        
    image_path = os.path.join(os.getcwd(), "assets", "form_template.png")
    
    def draw_background_and_footer(canvas, doc):
        canvas.saveState()
        # Desenha a folha de fundo em A4 completo
        if os.path.exists(image_path):
            canvas.drawImage(image_path, 0, 0, width=210*mm, height=297*mm, preserveAspectRatio=True)
            
        # Títulos estáticos das colunas logo acima da tabela (a 218mm de altura)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(20*mm, 218*mm, "Nome Espírito")
        canvas.drawString(140*mm, 218*mm, "Vinculo / Linhagem / Família")
        
        # Dados do Fiel desenhados estaticamente na parte inferior
        canvas.setFont("Helvetica", 9)
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        hora_atual = datetime.now().strftime("%H:%M:%S")
        canvas.drawCentredString(105*mm, 21*mm, f"{user.igreja}, 02 de novembro de 2026")
        canvas.drawString(20*mm, 15*mm, f"Nome: {user.nome_real} {user.sobrenome} - {user.estado_civil}")
        canvas.drawString(20*mm, 10*mm, f"Igreja: {user.igreja}")
        canvas.drawString(20*mm, 5*mm, f"Enviado em {data_hoje} às {hora_atual}")
        canvas.drawRightString(195*mm, 5*mm, f"Página {doc.page}")
        canvas.restoreState()
        
    doc.build(story, onFirstPage=draw_background_and_footer, onLaterPages=draw_background_and_footer)
    buffer.seek(0)
    return buffer

@router.get("/pdf")
def export_pdf_new(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    pdf_buffer = generate_pdf_flowable(session, current_user)
    headers = {
        'Content-Disposition': 'attachment; filename="antepassados.pdf"'
    }
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)

@router.get("/exportar-pdf")
def export_pdf(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    pdf_buffer = generate_pdf_flowable(session, current_user)
    headers = {
        'Content-Disposition': 'attachment; filename="antepassados.pdf"'
    }
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
