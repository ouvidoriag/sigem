# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import re

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

def clean_address(addr_raw, bairro):
    # Remove CEP, telefones, e ruídos
    cleaned = re.sub(r'CEP\s*[\d\.\-]+', '', addr_raw, flags=re.I)
    cleaned = re.sub(r'Duque de Caxias\s*[-–]?\s*RJ', '', cleaned, flags=re.I)
    # Se tiver " – ", pegar as partes de logradouro
    parts = [p.strip() for p in re.split(r'[-–—]', cleaned) if p.strip()]
    if parts:
        logr = parts[0]
        return f"{logr}, {bairro}, Duque de Caxias, RJ"
    return f"{cleaned}, {bairro}, Duque de Caxias, RJ"

print("Testando primeiros 15 endereços...")
for item in items[:15]:
    bairro = item.get('bairro', '')
    addr = clean_address(item.get('endereco', ''), bairro)
    url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={urllib.parse.quote(addr)}&f=json&outFields=Match_addr,Addr_type,Score"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            cands = data.get('candidates', [])
            if cands and cands[0]['score'] >= 75:
                top = cands[0]
                t = top['attributes'].get('Addr_type')
                print(f"[{item['id']}] {item['nome'][:28]} | Busca: '{addr[:40]}'")
                print(f"    -> {t} ({top['score']}%): {top['address']} -> ({top['location']['y']:.6f}, {top['location']['x']:.6f})")
            else:
                print(f"[{item['id']}] {item['nome'][:28]} | Busca: '{addr[:40]}' -> ❌ NÃO ACHOU")
    except Exception as e:
        print(f"Erro {item['id']}: {e}")
