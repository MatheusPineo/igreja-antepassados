import sys
import os
from sqlmodel import Session, select

# Adiciona o diretório raiz ao path do Python para permitir imports do backend
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.core.database import engine
from backend.app.models.usuario import Usuario
from backend.app.models.antepassado import Antepassado

TARGET_EMAIL = "marianasvfolharini@gmail.com"

data = [
    {"nome_completo": "FOLHARINI", "vinculo": "tronco paterno marido"},
    {"nome_completo": "DUVA", "vinculo": "tronco paterno marido"},
    {"nome_completo": "AGA", "vinculo": "tronco paterno marido"},
    {"nome_completo": "CESÁRIO", "vinculo": "tronco paterno marido"},
    {"nome_completo": "DE OLIVEIRA", "vinculo": "tronco materno marido"},
    {"nome_completo": "LORCA", "vinculo": "tronco materno marido"},
    {"nome_completo": "LOPES", "vinculo": "tronco materno marido"},
    {"nome_completo": "GIMENES", "vinculo": "tronco materno marido"},
    {"nome_completo": "BAPTISTA FOLHARINI", "vinculo": "avô paterno marido"},
    {"nome_completo": "FÁTIMA AGA FOLHARINI", "vinculo": "avó paterna marido"},
    {"nome_completo": "OSÓRIO MARCELINO DE OLIVEIRA", "vinculo": "avô materno marido"},
    {"nome_completo": "ANA LORCA DE OLIVEIRA", "vinculo": "avó materna marido"},
    {"nome_completo": "MARCO AURÉLIO FAGOTTI", "vinculo": "primo materno marido"},
    {"nome_completo": "VIEIRA", "vinculo": "tronco paterno"},
    {"nome_completo": "CORTAZ", "vinculo": "tronco paterno"},
    {"nome_completo": "MARTINS", "vinculo": "tronco paterno"},
    {"nome_completo": "FLORES", "vinculo": "tronco materno"},
    {"nome_completo": "SILVA", "vinculo": "tronco materno"},
    {"nome_completo": "DOS SANTOS", "vinculo": "tronco materno"},
    {"nome_completo": "FERREIRA", "vinculo": "tronco materno"},
    {"nome_completo": "ANTUNES", "vinculo": "tronco materno"},
    {"nome_completo": "MUNIZ", "vinculo": "tronco afim materno"},
    {"nome_completo": "MARIA ROSA VIEIRA", "vinculo": "tataravó paterna"},
    {"nome_completo": "JACINTHO JOSÉ VIEIRA", "vinculo": "bisavô paterno"},
    {"nome_completo": "MARIA ANTÔNIA VIEIRA", "vinculo": "bisavó paterna"},
    {"nome_completo": "ANTÔNIO JOSÉ CORTAZ", "vinculo": "bisavô paterno"},
    {"nome_completo": "OLYMPIA MARTINS CORTAZ", "vinculo": "bisavó paterna"},
    {"nome_completo": "JOÃO BAPTISTA VIEIRA", "vinculo": "avô paterno"},
    {"nome_completo": "GINETTE CORTAZ VIEIRA", "vinculo": "avó paterna"},
    {"nome_completo": "THOMAZIA SILVA", "vinculo": "tataravó materna"},
    {"nome_completo": "MANOEL MUNIZ", "vinculo": "tataravô afim materno"},
    {"nome_completo": "MARIA ROSA MUNIZ", "vinculo": "tataravó afim materna"},
    {"nome_completo": "ALFREDO FLORES", "vinculo": "bisavô materno"},
    {"nome_completo": "ODETTE SILVA MUNIZ", "vinculo": "bisavó materna"},
    {"nome_completo": "PEDRO MUNIZ", "vinculo": "bisavô afim materno"},
    {"nome_completo": "JOSÉ SILVA", "vinculo": "avô materno"},
    {"nome_completo": "MARIA HELENA SILVA", "vinculo": "avó materna"},
    {"nome_completo": "SASHA VIEIRA SENNA", "vinculo": "filho(a)"},
    {"nome_completo": "ELOÁ SILVA VIEIRA FOLHARINI", "vinculo": "filho(a)"},
    {"nome_completo": "ANGEL SILVA VIEIRA FOLHARINI", "vinculo": "filho(a)"},
    {"nome_completo": "ARIEL SILVA VIEIRA", "vinculo": "irmã(o)"},
    {"nome_completo": "ALEXIS SILVA VIEIRA", "vinculo": "irmã(o)"},
    {"nome_completo": "ANTÔNIO FERREIRA DOS SANTOS", "vinculo": "tio bisavô materno"},
    {"nome_completo": "JUDITH FERREIRA DOS SANTOS", "vinculo": "tia bisavó materna"},
    {"nome_completo": "JÚLIA ANTUNES FERREIRA", "vinculo": "tia bisavó materna"},
    {"nome_completo": "JORGE SILVA", "vinculo": "tio avô materno"},
    {"nome_completo": "HILDA MAGDALENA SILVA", "vinculo": "tia avó materna"},
    {"nome_completo": "MAURA CORTAZ VIEIRA", "vinculo": "tia paterna"},
    {"nome_completo": "GILSON LUIZ DA ROCHA OLIVEIRA", "vinculo": "tio materno/padrinho"},
    {"nome_completo": "JORGE SILVA JUNIOR", "vinculo": "primo 2º grau materno"},
    {"nome_completo": "SENNA", "vinculo": "tronco paterno ex-marido"},
    {"nome_completo": "FERREIRA", "vinculo": "tronco materno ex-marido"},
    {"nome_completo": "JOSÉ SENNA IRMÃO", "vinculo": "pai ex-marido"},
    {"nome_completo": "EUNICE FERREIRA SENNA", "vinculo": "mãe ex-marido"},
    {"nome_completo": "DINORÁ MOREIRA SENNA", "vinculo": "irmã ex-marido"},
    {"nome_completo": "JOSÉ FERREIRA SENNA", "vinculo": "irmão ex-marido"},
    {"nome_completo": "ABÍLIO ALVES DE OLIVEIRA", "vinculo": "\"\"\"avô\"\" afim\""},
    {"nome_completo": "ARMÊNIO TEIXEIRA BRANDÃO", "vinculo": "amigo"},
    {"nome_completo": "SERGIO FERNANDES MOZA DE AGUIAR", "vinculo": "amigo"},
    {"nome_completo": "SERGIO LUIZ DA ROCHA OLIVEIRA", "vinculo": "amigo"},
    {"nome_completo": "FERNANDO LUIZ DA ROCHA OLIVEIRA", "vinculo": "amigo"},
    {"nome_completo": "LUÍSA DE OLIVEIRA NOGUEIRA", "vinculo": "amiga"},
    {"nome_completo": "CARLOS ALBERTO ALVES DE OLIVEIRA", "vinculo": "amigo"},
    {"nome_completo": "AURELI BAPTISTA DE BRITTO", "vinculo": "amiga"},
    {"nome_completo": "HUMBERTO ALVES DE OLIVEIRA", "vinculo": "amigo"},
    {"nome_completo": "CONCEIÇÃO DE OLIVEIRA PEREIRA", "vinculo": "amiga"},
    {"nome_completo": "DOMINGOS MONTAGNER", "vinculo": "amigo"},
    {"nome_completo": "MARCOS LUIZ LANDI", "vinculo": "amigo"},
    {"nome_completo": "AFONSO BELTRAME", "vinculo": "amigo"},
    {"nome_completo": "VALDIM DE SETA", "vinculo": "amigo"},
    {"nome_completo": "JOÃO PEREIRA JOANNOU", "vinculo": "amigo"},
    {"nome_completo": "ANTONIO MENDES", "vinculo": "amigo"},
    {"nome_completo": "LIDIA FARIA COELHO", "vinculo": "amiga"},
    {"nome_completo": "ANDREA DE SOUZA TELLES", "vinculo": "amiga"},
    {"nome_completo": "LÉIA DOS SANTOS OLIVEIRA", "vinculo": "amiga"},
    {"nome_completo": "LUÍS FERNANDO DIAS DE LIMA MARTINS", "vinculo": "amigo"},
    {"nome_completo": "MARLENE DE PAULA QUEIROZ", "vinculo": "amiga"},
    {"nome_completo": "LECY RITA VASQUES ANDRADE", "vinculo": "amiga"},
    {"nome_completo": "ROSINDA DE SOUZA DA CONCEIÇÃO", "vinculo": "amiga"},
    {"nome_completo": "ALOÍSIO MACHADO", "vinculo": "amigo"},
    {"nome_completo": "ALLAN SPENCER MAMEDES E OLIVEIRA", "vinculo": "amigo"},
    {"nome_completo": "MOISÉS GUILHERMINO DE ALMEIDA", "vinculo": "amigo"},
    {"nome_completo": "RICARDO EUGÊNIO BOECHAT", "vinculo": "amigo"},
    {"nome_completo": "RONALDO QUATTRUCCI", "vinculo": "amigo"},
    {"nome_completo": "IVONETE NUNES", "vinculo": "amiga"},
    {"nome_completo": "EDIVALDO MENESES DOS SANTOS", "vinculo": "amigo"},
    {"nome_completo": "MARIA FERNANDA GOMES DE PAULO", "vinculo": "amiga"},
    {"nome_completo": "JOSÉ CARLOS TEIXEIRA", "vinculo": "amigo"},
    {"nome_completo": "PAULO SHUMHITI AWAIHARA", "vinculo": "amigo"},
    {"nome_completo": "IVAN RIBEIRO CÂMARA", "vinculo": "amigo"},
    {"nome_completo": "WALTER NUNES", "vinculo": "amigo"},
    {"nome_completo": "LIANA JOHN", "vinculo": "amiga"},
    {"nome_completo": "CRISTÓVÃO LUIZ DA ROCHA OLIVEIRA", "vinculo": "amigo"},
    {"nome_completo": "MARIA HELOÍSA AMARANTE SAVOY", "vinculo": "amiga"},
    {"nome_completo": "CLÁUDIO VIANNA CAVALCANTE", "vinculo": "amigo"},
    {"nome_completo": "FRANCISCO ANTÔNIO TRIANON DE SOUZA", "vinculo": "amigo"},
    {"nome_completo": "ZELIA CINIRA MONTEFUSCO", "vinculo": "amiga"}
]

def seed_mariana_ancestors():
    print(f"Buscando usuária com e-mail: {TARGET_EMAIL}...")
    with Session(engine) as session:
        user = session.exec(select(Usuario).where(Usuario.email == TARGET_EMAIL)).first()
        if not user:
            print(f"ERRO: Usuária '{TARGET_EMAIL}' não encontrada. Abortando seed.")
            return
        
        print(f"Usuária encontrada! ID: {user.id}. Iniciando inserção dos antepassados...")
        
        count = 0
        for item in data:
            # Verifica se já existe para evitar duplicados
            existing = session.exec(
                select(Antepassado).where(
                    Antepassado.usuario_id == user.id,
                    Antepassado.nome_completo == item["nome_completo"],
                    Antepassado.vinculo == item["vinculo"]
                )
            ).first()
            
            if not existing:
                # Determina linhagem e família com base no vínculo
                vinculo_lower = item["vinculo"].lower()
                linhagem = "Paterna" if "paterna" in vinculo_lower or "paterno" in vinculo_lower else \
                           "Materna" if "materna" in vinculo_lower or "materno" in vinculo_lower else \
                           "Não aplicável"
                           
                familia = "Família do Cônjuge" if "marido" in vinculo_lower or "ex-marido" in vinculo_lower else "Minha Família"
                
                novo_antepassado = Antepassado(
                    nome_completo=item["nome_completo"],
                    vinculo=item["vinculo"],
                    linhagem=linhagem,
                    familia=familia,
                    usuario_id=user.id
                )
                session.add(novo_antepassado)
                count += 1
                
        if count > 0:
            session.commit()
            print(f"Sucesso! {count} novos antepassados adicionados para Mariana.")
        else:
            print("Nenhum novo antepassado para adicionar (todos já existem no banco).")

if __name__ == "__main__":
    # Como solicitado, a execução não será disparada automaticamente nesta fase.
    print("Script preparado. Para rodar a inserção, execute seed_mariana_ancestors() ou chame o script via CLI.")
