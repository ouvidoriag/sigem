import os
import sys
import glob
import re
import json
import csv
import html
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

INBOX_DIR = r"C:\Users\501379.PMDC\Desktop\BANCODUQUEIA\00-INBOX"
HTML_DIR = os.path.join(INBOX_DIR, "html")
TXT_DIR = os.path.join(INBOX_DIR, "txt")
JSON_DIR = os.path.join(INBOX_DIR, "json")
SCRAPING_DIR = os.path.join(INBOX_DIR, "web scraping")
LOCAL_DIR = r"c:\Users\501379.PMDC\Desktop\web scraping\educação"

COORD_MAP = {
    "607263": "1º Distrito",
    "607329": "2º Distrito",
    "607388": "3º Distrito",
    "607425": "4º Distrito"
}

def atualizar():
    json_path = os.path.join(SCRAPING_DIR, "escolas_duque_de_caxias.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        coord = item.get("cod_coordenadoria", "")
        if coord in COORD_MAP:
            item["distrito"] = COORD_MAP[coord]

    # Ordenar por nome da escola
    data.sort(key=lambda x: x.get('nome_escola', ''))

    # Salvar JSONs
    for p in [
        os.path.join(SCRAPING_DIR, "escolas_duque_de_caxias.json"),
        os.path.join(LOCAL_DIR, "escolas_duque_de_caxias.json")
    ]:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Salvar CSVs
    campos = [
        'codigo_escola', 'nome_escola', 'distrito', 'endereco', 'bairro',
        'municipio', 'estado', 'cep', 'telefones', 'email', 'diretor',
        'data_funcionamento', 'id_interno_unidade', 'cod_coordenadoria', 'url'
    ]
    for p in [
        os.path.join(SCRAPING_DIR, "escolas_duque_de_caxias.csv"),
        os.path.join(LOCAL_DIR, "escolas_duque_de_caxias.csv")
    ]:
        with open(p, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore', delimiter=';')
            writer.writeheader()
            for r in data:
                writer.writerow(r)

    # Salvar TXTs
    for p in [
        os.path.join(LOCAL_DIR, "escolas_duque_de_caxias.txt"),
        os.path.join(SCRAPING_DIR, "escolas_duque_de_caxias.txt")
    ]:
        with open(p, 'w', encoding='utf-8') as f:
            f.write("CATÁLOGO OFICIAL DE TODAS AS ESCOLAS MUNICIPAIS DE DUQUE DE CAXIAS\n")
            f.write(f"Total de Escolas Catalogadas: {len(data)}\n")
            f.write("Fonte: Auge Educacional / SME Duque de Caxias\n")
            f.write("=" * 80 + "\n\n")
            for i, esc in enumerate(data, 1):
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

    print(f"Atualizado com sucesso! Total: {len(data)} escolas.")

if __name__ == "__main__":
    atualizar()
