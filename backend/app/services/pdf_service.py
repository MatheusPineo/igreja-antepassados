import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import logging

logger = logging.getLogger(__name__)

def gerar_pdf_antepassados(dados_lista: list[dict], cidade_solicitacao: str) -> io.BytesIO:
    """
    Gera o PDF de Antepassados usando ReportLab em memória (evitando I/O em disco e economizando RAM).
    :param dados_lista: Lista de dicionários contendo 'nome' e 'parentesco'.
    :param cidade_solicitacao: String com a cidade para o rodapé.
    :return: BytesIO contendo o PDF gerado.
    """
    buffer = io.BytesIO()
    
    try:
        # 1. Configuração de tamanho e canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        center_x = width / 2.0
        
        # Função auxiliar para desenhar o cabeçalho
        def draw_header(c):
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(center_x, height - 20*mm, "IGREJA MESSIÂNICA MUNDIAL DE PORTUGAL")
            c.setFont("Helvetica", 12)
            c.drawCentredString(center_x, height - 27*mm, "SEDE CENTRAL - LISBOA")
            
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(center_x, height - 37*mm, "FORMULÁRIO DE PRECE / SOLICITAÇÃO DE CULTO ÀS ALMAS DOS ANTEPASSADOS")
            
            # Ensinamento (4)
            c.setFont("Helvetica-Oblique", 9)
            quote_lines = [
                '"Nós, que estamos vivos, não somos seres surgidos do nada, sem relação com coisa alguma.',
                'Na verdade, somos a síntese de centenas, talvez de milhares de antepassados e',
                'existimos como seres vivos que respiram na extremidade de uma sequência infinita de vida." - Meishu-Sama'
            ]
            
            y_quote = height - 50*mm
            for line in quote_lines:
                c.drawCentredString(center_x, y_quote, line)
                y_quote -= 4*mm
                
            # Cabeçalho da tabela
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, height - 70*mm, "Nome Espírito/Família")
            c.drawString(140*mm, height - 70*mm, "Parentesco")
            
            # Linha horizontal
            c.line(20*mm, height - 72*mm, width - 20*mm, height - 72*mm)
            
            return height - 80*mm # Retorna Y inicial para os dados
            
        def draw_footer(c):
            c.setFont("Helvetica", 10)
            rodape_texto = f"{cidade_solicitacao}, ____ de ___________________ de 2026"
            c.drawCentredString(center_x, 20*mm, rodape_texto)
            
        # Desenha a primeira página
        current_y = draw_header(c)
        draw_footer(c)
        
        c.setFont("Helvetica", 10)
        
        # 5. Loop dinâmico (Dados)
        for item in dados_lista:
            if current_y <= 50*mm:
                c.showPage() # Nova página
                current_y = draw_header(c)
                draw_footer(c)
                c.setFont("Helvetica", 10)
                
            nome = item.get("nome", "")
            parentesco = item.get("parentesco", "")
            
            c.drawString(20*mm, current_y, nome)
            c.drawString(140*mm, current_y, parentesco)
            
            # Linha horizontal sutil
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.line(20*mm, current_y - 2*mm, width - 20*mm, current_y - 2*mm)
            c.setStrokeColorRGB(0, 0, 0) # reset
            
            current_y -= 7*mm
            
        # Finaliza e salva o PDF no buffer
        c.save()
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF de antepassados: {e}")
        buffer.close()
        raise e
