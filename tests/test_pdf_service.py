import pytest
import io
import os
import sys

# Adiciona o diretorio root ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.pdf_service import gerar_pdf_antepassados

def test_gerar_pdf_antepassados():
    dados = [
        {"nome": "João da Silva", "parentesco": "Avô"},
        {"nome": "Maria da Silva", "parentesco": "Avó"}
    ]
    
    # Gera mais dados para forçar quebra de página
    for i in range(50):
        dados.append({"nome": f"Antepassado {i}", "parentesco": "Parente"})
        
    pdf_buffer = gerar_pdf_antepassados(dados, "Lisboa")
    
    assert isinstance(pdf_buffer, io.BytesIO)
    pdf_content = pdf_buffer.read()
    
    # O PDF deve iniciar com o cabeçalho PDF
    assert pdf_content.startswith(b"%PDF-")
    assert len(pdf_content) > 1000  # Deve ter um tamanho razoável
