# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import re

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

def clean_query(item):
    end = item.get('endereco', '')
    nome = item.get('nome', '')
    bairro = item.get('bairro', '')
    
    # 1. Limpa ruídos comuns do endereço
    end_clean = re.sub(r'CEP\s*[\d\.\-]+', '', end, flags=re.I)
    end_clean = re.sub(r'Duque de Caxias\s*[-–—]?\s*RJ', '', end_clean, flags=re.I)
    end_clean = re.sub(r'\(.*?\)', '', end_clean)
    
    # Pega a primeira parte antes do hífen (geralmente logradouro + número)
    parts = [p.strip() for p in re.split(r'[-–—]', end_clean) if p.strip()]
    logradouro = parts[0] if parts else end_clean.strip()
    
    # Se o logradouro for muito genérico ou vazio, tenta o nome
    query = f"{logradouro}, {bairro}, Duque de Caxias, RJ"
    return query, logradouro

stats = {'StreetAddress': 0, 'StreetName': 0, 'POI': 0, 'Locality': 0, 'Other': 0}

print("Auditando 30 itens com ArcGIS World Geocoder...")
for item in items[:30]:
    q, logr = clean_query(item)
    url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={urllib.parse.quote(q)}&f=json&outFields=Match_addr,Addr_type,Score"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            cands = data.get('candidates', [])
            if cands and cands[0]['score'] >= 75:
                top = cands[0]
                t = top['attributes'].get('Addr_type')
                stats[t] = stats.get(t, 0) + 1
                print(f"[{item['id']}] {item['nome'][:25]} | {logr[:25]} -> {t} ({top['score']}%): {top['address'][:40]} | ({top['location']['y']:.5f}, {top['location']['x']:.5f})")
            else:
                stats['Other'] += 1
                print(f"[{item['id']}] {item['nome'][:25]} | {logr[:25]} -> ❌ Não bateu score")
    except Exception as e:
        print(f"Erro {item['id']}: {e}")

print("Estatísticas:", stats)
