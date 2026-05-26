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
from reportlab.lib.units import cm

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
    
    # 4 linhagens oficiais + outros vínculos
    lineage_titles = {
        1: "1. Linhagem Paterna do Marido (Troncos e Familiares)",
        2: "2. Linhagem Materna do Marido (Troncos e Familiares)",
        3: "3. Linhagem Paterna da Esposa (Troncos e Familiares)",
        4: "4. Linhagem Materna da Esposa (Troncos e Familiares)",
        5: "5. Outros Vínculos e Registros de Afinidade"
    }
    
    blocos = {1: [], 2: [], 3: [], 4: [], 5: []}
    for a in antepassados_ordenados:
        key = get_ancestor_sort_key(a.vinculo, a.nome_completo)
        bloco_id = key[0] if key[0] in [1, 2, 3, 4] else 5
        blocos[bloco_id].append(a)
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor("#1A365D"),
        alignment=1, # Centralizado
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=1,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=15
    )
    
    name_style = ParagraphStyle(
        'AncestorName',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#2D3748")
    )
    
    tronco_name_style = ParagraphStyle(
        'TroncoName',
        parent=styles['Normal'],
        fontName='Helvetica-BoldOblique',
        fontSize=9,
        textColor=colors.HexColor("#1A365D")
    )
    
    normal_cell_style = ParagraphStyle(
        'NormalCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#2D3748")
    )

    story = []
    
    # Cabeçalho da Igreja
    story.append(Paragraph("IGREJA MESSIÂNICA MUNDIAL DE PORTUGAL", header_title_style))
    story.append(Paragraph("Culto de Antepassados - Registro de Linhagens Oficial", subtitle_style))
    
    # Dados do Fiel
    fiel_data = [
        [
            Paragraph(f"<b>Fiel Titular:</b> {user.nome_real} {user.sobrenome}", normal_cell_style),
            Paragraph(f"<b>Igreja / Centro de Difusão:</b> {user.igreja}", normal_cell_style)
        ],
        [
            Paragraph(f"<b>Estado Civil:</b> {user.estado_civil}", normal_cell_style),
            Paragraph(f"<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_cell_style)
        ]
    ]
    fiel_table = Table(fiel_data, colWidths=[9*cm, 9*cm])
    fiel_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(fiel_table)
    story.append(Spacer(1, 15))
    
    # Renderização dos Blocos de Linhagem
    has_records = False
    for bloco_id in [1, 2, 3, 4, 5]:
        lista_bloco = blocos[bloco_id]
        if not lista_bloco:
            continue
            
        has_records = True
        title_text = lineage_titles[bloco_id]
        
        # Cabeçalho da Seção (Divisor azul)
        sec_p = Paragraph(f"<b>{title_text.upper()}</b>", ParagraphStyle('SecText', parent=styles['Normal'], fontName='Helvetica-Bold', textColor=colors.white, fontSize=9))
        section_header = Table([[sec_p]], colWidths=[18*cm])
        section_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1A365D")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        story.append(KeepTogether([
            section_header,
            Spacer(1, 4)
        ]))
        
        # Tabela com dados
        rows = []
        rows.append([
            Paragraph("<b>Nome Completo</b>", ParagraphStyle('ColH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#4A5568"))),
            Paragraph("<b>Parentesco / Vínculo</b>", ParagraphStyle('ColH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#4A5568"))),
            Paragraph("<b>Linhagem / Família</b>", ParagraphStyle('ColH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#4A5568")))
        ])
        
        for a in lista_bloco:
            nome = a.nome_completo
            alerta = " [ALERTA: Nome abreviado]" if any(p.endswith('.') for p in nome.split()) else ""
            nome_completo_com_alerta = f"{nome}{alerta}"
            
            is_tronco = "tronco" in a.vinculo.lower()
            if is_tronco:
                name_p = Paragraph(f"<b>{nome_completo_com_alerta}</b> <i>(Tronco)</i>", tronco_name_style)
            else:
                name_p = Paragraph(nome_completo_com_alerta, name_style)
                
            vinculo_p = Paragraph(a.vinculo, normal_cell_style)
            familia_p = Paragraph(f"{a.linhagem} ({a.familia})", normal_cell_style)
            
            rows.append([name_p, vinculo_p, familia_p])
            
        t = Table(rows, colWidths=[8.5*cm, 4.5*cm, 5.0*cm])
        
        t_styles = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Colorir linhas dos Troncos
        for idx, a in enumerate(lista_bloco, 1):
            if "tronco" in a.vinculo.lower():
                t_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor("#EBF8FF")))
                
        t.setStyle(TableStyle(t_styles))
        story.append(t)
        story.append(Spacer(1, 12))
        
    if not has_records:
        story.append(Paragraph("Nenhum antepassado cadastrado até o momento.", ParagraphStyle('NoRec', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#718096"), alignment=1)))
        
    # Aviso de Aborto
    has_aborto = any("aborto" in a.nome_completo.lower() or "aborto" in a.vinculo.lower() for a in antepassados)
    if has_aborto:
        warn_text = "<b>AVISO IMPORTANTE:</b> Para registros de aborto, é recomendado consultar um ministro da Sede para orientação correta sobre o preenchimento espiritual do formulário."
        warn_box = Table([[Paragraph(warn_text, ParagraphStyle('WarnText', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#744210")))]], colWidths=[18*cm])
        warn_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEFCBF")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F6E05E")),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(Spacer(1, 10))
        story.append(warn_box)
        
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#718096"))
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        canvas.drawString(1.5*cm, 1.0*cm, f"Gerado em: {date_str} | Fiel: {user.nome_real} {user.sobrenome}")
        canvas.drawRightString(A4[0] - 1.5*cm, 1.0*cm, f"Página {doc.page}")
        canvas.restoreState()
        
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
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
