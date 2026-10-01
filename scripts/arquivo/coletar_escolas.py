import os
import sys
import re
import json
import time
import hashlib
import html
import urllib.request
import urllib.parse
import http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://duque.augeeducacional.com.br"
LISTA_URL = f"{BASE_URL}/MapaCoordenadoria/listaEscola.do?actionType=inicializar&exibirQuadro=false&idUnidadeFuncional=607059"
POST_URL = f"{BASE_URL}/MapaCoordenadoria/listaEscola.do"

INBOX_DIR = r"C:\Users\501379.PMDC\Desktop\BANCODUQUEIA\00-INBOX"
HTML_DIR = os.path.join(INBOX_DIR, "html")
TXT_DIR = os.path.join(INBOX_DIR, "txt")
JSON_DIR = os.path.join(INBOX_DIR, "json")
IMG_DIR = os.path.join(INBOX_DIR, "imagens")
SCRAPING_DIR = os.path.join(INBOX_DIR, "web scraping")

LOCAL_OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

for d in [HTML_DIR, TXT_DIR, JSON_DIR, IMG_DIR, SCRAPING_DIR]:
    os.makedirs(d, exist_ok=True)

def get_opener():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    return opener

def sanitize_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = clean.replace(" ", "_").strip()
    return clean[:100]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[\s\-_]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return text.strip('-')[:80]

def coletar_todas_escolas_da_lista():
    print("[*] Conectando à página inicial para obter sessão e total de registros...")
    opener = get_opener()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    req = urllib.request.Request(LISTA_URL, headers=headers)
    resp = opener.open(req)
    raw_html = resp.read()
    charset = resp.headers.get_content_charset() or 'iso-8859-1'
    text_html = raw_html.decode(charset, errors='replace')

    # Detectar numero de páginas e registros
    m_reg = re.search(r'pagEscolas_numeroRegistros\s*=\s*(\d+)', text_html)
    m_pag = re.search(r'pagEscolas_numeroPaginas\s*=\s*(\d+)', text_html)
    
    num_registros = int(m_reg.group(1)) if m_reg else 205
    num_paginas = int(m_pag.group(1)) if m_pag else 21
    print(f"[*] Registros detectados: {num_registros}, Páginas (com 10/pág): {num_paginas}")

    todas_escolas = []
    ids_vistos = set()

    def extrair_linhas_tabela(html_content):
        # Tratar cada linha <tr> da tabela
        linhas = re.findall(r'<tr[^>]*>(.*?)</tr>', html_content, re.DOTALL | re.IGNORECASE)
        coletadas = []
        for l in linhas:
            m_escola = re.search(r'href=[\'"]detEscola\.do\?codUnidade=(\d+)[^\'"]*[\'"][^>]*>(.*?)</a>', l, re.DOTALL | re.IGNORECASE)
            if m_escola:
                cod_unidade = m_escola.group(1)
                nome_escola = html.unescape(re.sub(r'<[^>]+>', '', m_escola.group(2))).strip()
                
                # Coordenadoria / Distrito
                m_coord = re.search(r'href=[\'"][^\'"]*codCoordenadoria=(\d+)[^\'"]*[\'"][^>]*>(.*?)</a>', l, re.DOTALL | re.IGNORECASE)
                distrito = ""
                cod_coord = ""
                if m_coord:
                    cod_coord = m_coord.group(1)
                    distrito = html.unescape(re.sub(r'<[^>]+>', '', m_coord.group(2))).strip()
                
                # Link do site específico da escola (se houver)
                m_site = re.search(r'<td[^>]*style=[\'"][^\'"]*text-align\s*:\s*center[^\'"]*[\'"][^>]*>(.*?)</td>', l, re.DOTALL | re.IGNORECASE)
                site_link = ""
                if m_site:
                    m_href = re.search(r'href=[\'"]([^\'"]+)[\'"]', m_site.group(1))
                    if m_href:
                        site_link = m_href.group(1)

                coletadas.append({
                    "cod_unidade": cod_unidade,
                    "nome": nome_escola,
                    "distrito": distrito,
                    "cod_coordenadoria": cod_coord,
                    "site_link": site_link
                })
        return coletadas

    # Página 1 já carregada
    p1_escolas = extrair_linhas_tabela(text_html)
    for esc in p1_escolas:
        if esc["cod_unidade"] not in ids_vistos:
            ids_vistos.add(esc["cod_unidade"])
            todas_escolas.append(esc)

    print(f"[*] Página 1 coletada: {len(p1_escolas)} escolas (Total acumulado: {len(todas_escolas)})")

    # Páginas 2 a num_paginas
    for pag in range(2, num_paginas + 1):
        time.sleep(0.3)
        post_data = urllib.parse.urlencode({
            'actionType': 'paginar',
            'pagina': str(pag),
            'exibirQuadro': 'false',
            'idPaginaAvulsaNavegacao': '',
            'paginacao': '10'
        }).encode('utf-8')

        req_p = urllib.request.Request(POST_URL, data=post_data, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': LISTA_URL,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        try:
            resp_p = opener.open(req_p)
            text_p = resp_p.read().decode('iso-8859-1', errors='replace')
            p_escolas = extrair_linhas_tabela(text_p)
            adicionadas = 0
            for esc in p_escolas:
                if esc["cod_unidade"] not in ids_vistos:
                    ids_vistos.add(esc["cod_unidade"])
                    todas_escolas.append(esc)
                    adicionadas += 1
            print(f"[*] Página {pag}/{num_paginas} coletada: {len(p_escolas)} encontradas, {adicionadas} novas (Total: {len(todas_escolas)})")
        except Exception as e:
            print(f"[!] Erro ao coletar página {pag}: {e}")

    print(f"[+] Total final de escolas catalogadas na lista: {len(todas_escolas)}")
    return todas_escolas, opener

if __name__ == "__main__":
    escolas, opener = coletar_todas_escolas_da_lista()
    print("Primeiras 3 escolas:")
    for e in escolas[:3]:
        print(e)
