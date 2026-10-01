import os
import sys
import re
import json
import csv
import time
import html
import hashlib
import urllib.request
import urllib.parse
import http.cookiejar
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Configurar encoding padrão
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://duque.augeeducacional.com.br"
LISTA_URL = f"{BASE_URL}/MapaCoordenadoria/listaEscola.do?actionType=inicializar&exibirQuadro=false&idUnidadeFuncional=607059"
POST_URL = f"{BASE_URL}/MapaCoordenadoria/listaEscola.do"

# Diretórios de destino conforme Regra de Web Scraping DUQUE IA
INBOX_DIR = r"C:\Users\501379.PMDC\Desktop\BANCODUQUEIA\00-INBOX"
HTML_DIR = os.path.join(INBOX_DIR, "html")
TXT_DIR = os.path.join(INBOX_DIR, "txt")
JSON_DIR = os.path.join(INBOX_DIR, "json")
IMG_DIR = os.path.join(INBOX_DIR, "imagens")
SCRAPING_DIR = os.path.join(INBOX_DIR, "web scraping")

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

for d in [HTML_DIR, TXT_DIR, JSON_DIR, IMG_DIR, SCRAPING_DIR, LOCAL_DIR]:
    os.makedirs(d, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def gerar_slug(texto):
    texto = texto.lower()
    # Remover acentos básicos
    mapa = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o', 'ú': 'u', 'ü': 'u', 'ç': 'c'
    }
    for k, v in mapa.items():
        texto = texto.replace(k, v)
    texto = re.sub(r'[^a-z0-9]+', '-', texto)
    return texto.strip('-')[:60]

def coletar_catalogo():
    print("[*] 1/3 - Coletando lista de todas as escolas no portal da SME...")
    opener = get_opener()
    req = urllib.request.Request(LISTA_URL, headers=HEADERS)
    resp = opener.open(req)
    raw = resp.read()
    text = raw.decode('utf-8', errors='replace')

    m_reg = re.search(r'pagEscolas_numeroRegistros\s*=\s*(\d+)', text)
    m_pag = re.search(r'pagEscolas_numeroPaginas\s*=\s*(\d+)', text)
    num_registros = int(m_reg.group(1)) if m_reg else 205
    num_paginas = int(m_pag.group(1)) if m_pag else 21
    print(f"[*] Registros detectados: {num_registros} em {num_paginas} páginas")

    escolas_catalogo = []
    ids_vistos = set()

    def extrair_linhas(html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        tabela = soup.find('table', class_='ListagemPadrao')
        if not tabela:
            return []
        linhas = []
        for tr in tabela.find_all('tr'):
            link_escola = tr.find('a', href=lambda h: h and 'detEscola.do?codUnidade=' in h)
            if link_escola:
                m = re.search(r'codUnidade=(\d+)', link_escola['href'])
                cod_unidade = m.group(1) if m else ''
                nome_escola = link_escola.get_text(strip=True)

                link_distrito = tr.find('a', href=lambda h: h and 'codCoordenadoria=' in h)
                distrito = link_distrito.get_text(strip=True) if link_distrito else ''
                m_coord = re.search(r'codCoordenadoria=(\d+)', link_distrito['href']) if link_distrito else None
                cod_coord = m_coord.group(1) if m_coord else ''

                linhas.append({
                    'cod_unidade': cod_unidade,
                    'nome_lista': nome_escola,
                    'distrito': distrito,
                    'cod_coordenadoria': cod_coord,
                    'url_detalhe': f"{BASE_URL}/MapaCoordenadoria/detEscola.do?codUnidade={cod_unidade}&exibirQuadro=false"
                })
        return linhas

    # Página 1
    p1 = extrair_linhas(text)
    for item in p1:
        if item['cod_unidade'] not in ids_vistos:
            ids_vistos.add(item['cod_unidade'])
            escolas_catalogo.append(item)
    print(f"[*] Página 1 carregada: {len(p1)} escolas.")

    # Demais páginas
    for pag in range(2, num_paginas + 1):
        post_data = urllib.parse.urlencode({
            'actionType': 'paginar',
            'pagina': str(pag),
            'exibirQuadro': 'false',
            'idPaginaAvulsaNavegacao': '',
            'paginacao': '10'
        }).encode('utf-8')
        req_p = urllib.request.Request(POST_URL, data=post_data, headers={
            **HEADERS,
            'Referer': LISTA_URL,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        try:
            resp_p = opener.open(req_p)
            text_p = resp_p.read().decode('utf-8', errors='replace')
            p_itens = extrair_linhas(text_p)
            for item in p_itens:
                if item['cod_unidade'] not in ids_vistos:
                    ids_vistos.add(item['cod_unidade'])
                    escolas_catalogo.append(item)
            print(f"[*] Página {pag}/{num_paginas}: +{len(p_itens)} escolas (Total: {len(escolas_catalogo)})")
        except Exception as e:
            print(f"[!] Erro ao buscar página {pag}: {e}")
        time.sleep(0.15)

    print(f"[+] Total de escolas catalogadas: {len(escolas_catalogo)}")
    return escolas_catalogo

def raspar_detalhe_escola(item):
    url = item['url_detalhe']
    cod_unidade = item['cod_unidade']
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:10]

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw_bytes = resp.read()
            html_content = raw_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"[!] Erro ao baixar escola {cod_unidade}: {e}")
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    lista = soup.find('div', class_='ListaEscola')

    nome_detalhe = ""
    dados_extraidos = {
        'id_interno_unidade': cod_unidade,
        'url': url,
        'distrito': item['distrito'],
        'cod_coordenadoria': item['cod_coordenadoria'],
        'coleta_timestamp': datetime.now().isoformat()
    }

    if lista:
        h1 = lista.find('h1')
        if h1:
            nome_detalhe = h1.get_text(strip=True)
        dados_extraidos['nome_escola'] = nome_detalhe or item['nome_lista']

        # Extrair todos os campos <p><strong>Chave:</strong> Valor</p>
        for p in lista.find_all('p'):
            strong = p.find('strong')
            if strong:
                label = strong.get_text(strip=True)
                strong.extract()
                val = p.get_text(strip=True)

                # Limpar pontuação da label e valor
                label_clean = re.sub(r'[:\s]+$', '', label).strip()
                val_clean = re.sub(r'^[:\s]+', '', val).strip()

                # Normalizar nomes de chaves padrão
                lbl_lower = label_clean.lower()
                if 'código' in lbl_lower or 'codigo' in lbl_lower:
                    dados_extraidos['codigo_escola'] = val_clean
                elif 'endereço' in lbl_lower or 'endereco' in lbl_lower:
                    dados_extraidos['endereco'] = val_clean
                elif 'bairro' in lbl_lower:
                    dados_extraidos['bairro'] = val_clean
                elif 'estado' in lbl_lower:
                    dados_extraidos['estado'] = val_clean
                elif 'município' in lbl_lower or 'municipio' in lbl_lower:
                    dados_extraidos['municipio'] = val_clean
                elif 'cep' in lbl_lower:
                    dados_extraidos['cep'] = val_clean
                elif 'telefone' in lbl_lower:
                    dados_extraidos['telefones'] = val_clean.rstrip('-').strip()
                elif 'e-mail' in lbl_lower or 'email' in lbl_lower:
                    dados_extraidos['email'] = val_clean
                elif 'diretor' in lbl_lower:
                    dados_extraidos['diretor'] = val_clean
                elif 'data de funcionamento' in lbl_lower:
                    dados_extraidos['data_funcionamento'] = val_clean
                else:
                    dados_extraidos[label_clean] = val_clean
    else:
        dados_extraidos['nome_escola'] = item['nome_lista']

    # Garantir campos chave mesmo se vazios
    for k in ['codigo_escola', 'endereco', 'bairro', 'estado', 'municipio', 'cep', 'telefones', 'email', 'diretor', 'data_funcionamento']:
        if k not in dados_extraidos:
            dados_extraidos[k] = ""

    # Slug para o arquivo
    slug = gerar_slug(f"{dados_extraidos['nome_escola']}-{cod_unidade}")
    file_id = f"{slug}_{url_hash}"

    # Salvar HTML integral
    html_file = os.path.join(HTML_DIR, f"{file_id}.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Gerar texto limpo legível
    txt_lines = [
        f"Nome da Escola: {dados_extraidos['nome_escola']}",
        f"Código da Escola: {dados_extraidos['codigo_escola']}",
        f"Distrito / Coordenadoria: {dados_extraidos['distrito']}",
        f"Endereço: {dados_extraidos['endereco']}",
        f"Bairro: {dados_extraidos['bairro']}",
        f"Município: {dados_extraidos['municipio']}",
        f"Estado: {dados_extraidos['estado']}",
        f"CEP: {dados_extraidos['cep']}",
        f"Telefone(s): {dados_extraidos['telefones']}",
        f"E-mail: {dados_extraidos['email']}",
        f"Diretor: {dados_extraidos['diretor']}",
        f"Data de funcionamento: {dados_extraidos['data_funcionamento']}",
        f"URL Fonte: {url}",
        f"Data de Coleta: {dados_extraidos['coleta_timestamp']}"
    ]
    txt_content = "\n".join(txt_lines) + "\n"

    txt_file = os.path.join(TXT_DIR, f"{file_id}.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_content)

    # Salvar JSON individual
    json_meta = {
        "id": file_id,
        "cod_unidade": cod_unidade,
        "titulo": dados_extraidos['nome_escola'],
        "url": url,
        "data_coleta": dados_extraidos['coleta_timestamp'],
        "dados": dados_extraidos,
        "arquivos": {
            "html": f"html/{file_id}.html",
            "txt": f"txt/{file_id}.txt",
            "json": f"json/{file_id}.json"
        }
    }
    json_file = os.path.join(JSON_DIR, f"{file_id}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_meta, f, ensure_ascii=False, indent=2)

    return dados_extraidos

def main():
    catalogo = coletar_catalogo()
    print(f"\n[*] 2/3 - Extraindo detalhes e gerando acervo para {len(catalogo)} escolas...")

    todas_escolas_detalhes = []
    
    # Processar com 6 threads
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_item = {executor.submit(raspar_detalhe_escola, item): item for item in catalogo}
        concluidos = 0
        total = len(catalogo)
        for future in as_completed(future_to_item):
            res = future.result()
            concluidos += 1
            if res:
                todas_escolas_detalhes.append(res)
            if concluidos % 25 == 0 or concluidos == total:
                print(f"[*] Progresso: {concluidos}/{total} escolas processadas ({len(todas_escolas_detalhes)} com sucesso)")

    # Ordenar por nome da escola
    todas_escolas_detalhes.sort(key=lambda x: x.get('nome_escola', ''))

    print(f"\n[*] 3/3 - Salvando arquivos consolidados e relatórios...")

    # Salvar JSON consolidado no BANCODUQUEIA e na pasta local
    json_banco = os.path.join(SCRAPING_DIR, "escolas_duque_de_caxias.json")
    json_local = os.path.join(LOCAL_DIR, "escolas_duque_de_caxias.json")

    with open(json_banco, 'w', encoding='utf-8') as f:
        json.dump(todas_escolas_detalhes, f, ensure_ascii=False, indent=2)
    with open(json_local, 'w', encoding='utf-8') as f:
        json.dump(todas_escolas_detalhes, f, ensure_ascii=False, indent=2)

    # Salvar CSV consolidado
    campos = [
        'codigo_escola', 'nome_escola', 'distrito', 'endereco', 'bairro',
        'municipio', 'estado', 'cep', 'telefones', 'email', 'diretor',
        'data_funcionamento', 'id_interno_unidade', 'url'
    ]
    csv_banco = os.path.join(SCRAPING_DIR, "escolas_duque_de_caxias.csv")
    csv_local = os.path.join(LOCAL_DIR, "escolas_duque_de_caxias.csv")

    def salvar_csv(caminho):
        with open(caminho, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore', delimiter=';')
            writer.writeheader()
            for row in todas_escolas_detalhes:
                writer.writerow(row)

    salvar_csv(csv_banco)
    salvar_csv(csv_local)

    # Salvar TXT formatado consolidado no estilo solicitado pelo usuário
    txt_consolidado_local = os.path.join(LOCAL_DIR, "escolas_duque_de_caxias.txt")
    with open(txt_consolidado_local, 'w', encoding='utf-8') as f:
        f.write(f"RELATÓRIO CONSOLIDADO DE TODAS AS ESCOLAS MUNICIPAIS DE DUQUE DE CAXIAS\n")
        f.write(f"Total de Unidades: {len(todas_escolas_detalhes)}\n")
        f.write(f"Data da Extração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        for i, esc in enumerate(todas_escolas_detalhes, 1):
            f.write(f"[{i}] {esc.get('nome_escola', '')}\n")
            f.write(f"Código da Escola: {esc.get('codigo_escola', '')}\n")
            f.write(f"Distrito: {esc.get('distrito', '')}\n")
            f.write(f"Endereço: {esc.get('endereco', '')}\n")
            f.write(f"Bairro: {esc.get('bairro', '')}\n")
            f.write(f"Município: {esc.get('municipio', '')}\n")
            f.write(f"Estado: {esc.get('estado', '')}\n")
            f.write(f"CEP: {esc.get('cep', '')}\n")
            f.write(f"Telefone(s): {esc.get('telefones', '')}\n")
            f.write(f"E-mail: {esc.get('email', '')}\n")
            f.write(f"Diretor: {esc.get('diretor', '')}\n")
            f.write(f"Data de funcionamento: {esc.get('data_funcionamento', '')}\n")
            f.write(f"URL: {esc.get('url', '')}\n")
            f.write("-" * 50 + "\n\n")

    print("\n" + "=" * 60)
    print(f"[SUCESSO] Processamento de {len(todas_escolas_detalhes)} escolas concluído!")
    print(f"Arquivos gerados:")
    print(f"  - Banco Central HTML: {HTML_DIR} ({len(todas_escolas_detalhes)} arquivos)")
    print(f"  - Banco Central TXT: {TXT_DIR} ({len(todas_escolas_detalhes)} arquivos)")
    print(f"  - Banco Central JSON: {JSON_DIR} ({len(todas_escolas_detalhes)} arquivos)")
    print(f"  - Consolidado JSON: {json_banco}")
    print(f"  - Consolidado CSV: {csv_banco}")
    print(f"  - Cópia Local JSON: {json_local}")
    print(f"  - Cópia Local CSV: {csv_local}")
    print(f"  - Cópia Local TXT: {txt_consolidado_local}")
    print("=" * 60)

if __name__ == "__main__":
    main()
