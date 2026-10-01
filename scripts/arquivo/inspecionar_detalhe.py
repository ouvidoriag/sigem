import urllib.request
import re
import html
from bs4 import BeautifulSoup

def test_detalhes(cod_unidade):
    url = f"https://duque.augeeducacional.com.br/MapaCoordenadoria/detEscola.do?codUnidade={cod_unidade}&exibirQuadro=false"
    resp = urllib.request.urlopen(url)
    raw = resp.read()
    charset = resp.headers.get_content_charset() or 'iso-8859-1'
    content = raw.decode(charset, errors='replace')

    soup = BeautifulSoup(content, 'html.parser')
    lista_escola = soup.find('div', class_='ListaEscola')
    if lista_escola:
        h1 = lista_escola.find('h1')
        print("H1:", h1.get_text(strip=True) if h1 else "Nenhum")
        
        # Imagens dentro de lista_escola
        imgs = lista_escola.find_all('img')
        print("Imagens na div ListaEscola:", [img.get('src') for img in imgs])

        # Paragrafos
        for p in lista_escola.find_all('p'):
            print("  P:", p.get_text(separator=' ', strip=True))
    else:
        print("Div ListaEscola não encontrada!")

    # Checar divAlunosCurso ou outras tabelas
    alunos = soup.find('div', id='divAlunosCurso')
    if alunos and alunos.get_text(strip=True):
        print("divAlunosCurso:", alunos.get_text(strip=True))

print("=== CIEP Carlos Chagas (607264) ===")
test_detalhes('607264')
print("\n=== CCAIC Gramacho (607266) ===")
test_detalhes('607266')
