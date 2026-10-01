# -*- coding: utf-8 -*-
"""
Script de Calibração GIS Profissional usando ArcGIS World Geocoding Engine
Geocodifica todos os 449 equipamentos municipais de Duque de Caxias com precisão de malha viária real.
"""

import json
import csv
import re
import time
import os
import sys
import subprocess
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

JSON_PATH = os.path.join("dados", "todos_os_enderecos_duque_de_caxias.json")
CSV_PATH = os.path.join("dados", "todos_os_enderecos_duque_de_caxias.csv")

# Bounding box seguro de Duque de Caxias
LAT_MIN, LAT_MAX = -22.840, -22.500
LON_MIN, LON_MAX = -43.380, -43.130

def in_caxias_bbox(lat, lon):
    return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX

def clean_address_parts(end_raw, bairro, cep):
    """Extrai logradouro, número e bairro limpos"""
    if not end_raw:
        return "", "", bairro
    
    # Remove ruídos
    cleaned = end_raw
    cleaned = re.sub(r'CEP\s*[\d\.\-]+', '', cleaned, flags=re.I)
    cleaned = re.sub(r'Duque de Caxias\s*[-–—]?\s*RJ', '', cleaned, flags=re.I)
    cleaned = re.sub(r'\(.*?\)', '', cleaned) # remove parenteses
    
    # Divide por travessão ou hífen
    parts = [p.strip() for p in re.split(r'[-–—]', cleaned) if p.strip()]
    main_part = parts[0] if parts else cleaned.strip()
    
    # Remove "ao lado de...", "próximo a..."
    main_part = re.sub(r',?\s*(ao lado|próximo|em frente|esquina).*$', '', main_part, flags=re.I)
    
    return main_part, bairro, cep

def query_arcgis(query_str):
    url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={urllib.parse.quote(query_str)}&f=json&outFields=Match_addr,Addr_type,Score&maxLocations=3"
    req = urllib.request.Request(url, headers={'User-Agent': 'PrefeituraDuqueDeCaxiasGIS/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            candidates = data.get('candidates', [])
            return candidates
    except Exception as e:
        return []

def query_nominatim(query_str):
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query_str)}&format=json&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'PrefeituraDuqueDeCaxiasGIS/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                return float(data[0]['lat']), float(data[0]['lon']), data[0].get('display_name', '')
    except Exception:
        pass
    return None

def geocode_item(item):
    item_id = item.get('id', '')
    nome = item.get('nome', '')
    bairro = item.get('bairro', '')
    endereco = item.get('endereco', '')
    cep = item.get('cep', '')
    
    main_part, b_clean, c_clean = clean_address_parts(endereco, bairro, cep)
    
    # Tentativa 1: Logradouro limpo + Bairro + Duque de Caxias
    queries_to_try = [
        f"{main_part}, {b_clean}, Duque de Caxias, RJ",
        f"{main_part}, Duque de Caxias, RJ"
    ]
    
    # Se tiver CEP válido
    if c_clean and len(c_clean.replace('-', '').replace('.', '')) == 8:
        queries_to_try.append(f"{main_part}, {c_clean}, Duque de Caxias, RJ")
    
    # Tentativa com nome do equipamento (ótimo para POIs como hospitais, teatros, escolas conhecidas)
    nome_curto = re.sub(r'^(E M |CIEP |HOSPITAL |SECRETARIA MUNICIPAL DE |POSTO DE SAÚDE |UBS |UPA )', '', nome, flags=re.I).strip()
    if len(nome_curto) > 3:
        queries_to_try.append(f"{nome}, Duque de Caxias, RJ")
        queries_to_try.append(f"{nome_curto}, Duque de Caxias, RJ")
        
    # Se o logradouro tiver "S/N", tenta só a rua sem o S/N
    if "s/n" in main_part.lower():
        rua_pura = re.sub(r',?\s*s/n[º°]?', '', main_part, flags=re.I).strip()
        queries_to_try.append(f"{rua_pura}, {b_clean}, Duque de Caxias, RJ")
        queries_to_try.append(f"{rua_pura}, Duque de Caxias, RJ")
    
    best_candidate = None
    best_score = 0
    
    for q in queries_to_try:
        cands = query_arcgis(q)
        for cand in cands:
            score = cand.get('score', 0)
            t = cand.get('attributes', {}).get('Addr_type', '')
            lat = cand['location']['y']
            lon = cand['location']['x']
            
            # Validação geográfica rígida em Caxias
            if not in_caxias_bbox(lat, lon):
                continue
                
            # Pontuação por tipo de precisão GIS
            # StreetAddress/PointAddress = endereço exato com número
            # StreetName = no meio da rua correta
            # POI = prédio público exato
            type_weight = {
                'PointAddress': 100,
                'StreetAddress': 100,
                'StreetAddressExt': 100,
                'BuildingName': 98,
                'POI': 95,
                'StreetName': 90,
                'StreetInt': 85
            }.get(t, 60)
            
            combined_score = (score * 0.5) + (type_weight * 0.5)
            
            if combined_score > best_score:
                best_score = combined_score
                best_candidate = {
                    'lat': round(lat, 6),
                    'lon': round(lon, 6),
                    'tipo': t,
                    'score': score,
                    'addr_match': cand.get('address', ''),
                    'query': q
                }
                # Se achou endereço exato com score >= 90, já é perfeito
                if t in ['PointAddress', 'StreetAddress', 'StreetAddressExt'] and score >= 90:
                    break
        if best_candidate and best_candidate['score'] >= 90 and best_candidate['tipo'] in ['PointAddress', 'StreetAddress', 'StreetAddressExt']:
            break

    # Fallback Nominatim se ArcGIS não achou nada acima de 70
    if not best_candidate or best_score < 70:
        rua_busca = re.sub(r',?\s*s/n[º°]?', '', main_part, flags=re.I).strip()
        nom = query_nominatim(f"{rua_busca}, Duque de Caxias, RJ")
        if nom and in_caxias_bbox(nom[0], nom[1]):
            best_candidate = {
                'lat': round(nom[0], 6),
                'lon': round(nom[1], 6),
                'tipo': 'StreetName_OSM',
                'score': 85,
                'addr_match': nom[2],
                'query': rua_busca
            }

    return item_id, best_candidate

def main():
    print("=" * 75)
    print("🚀 INICIANDO RECALIBRAÇÃO GIS COM ARCGIS WORLD GEOCODER")
    print("=" * 75)
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        items = json.load(f)
        
    total = len(items)
    print(f"📦 Total de equipamentos para calibrar: {total}")
    
    t0 = time.time()
    results = {}
    
    # Usar ThreadPoolExecutor para requisições paralelas rápidas e suaves
    workers = 6
    print(f"⚡ Disparando geocodificação paralela com {workers} workers...")
    
    completed_count = 0
    exact_count = 0
    street_count = 0
    fallback_count = 0
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_item = {executor.submit(geocode_item, it): it for it in items}
        
        for future in as_completed(future_to_item):
            orig_item = future_to_item[future]
            completed_count += 1
            try:
                item_id, match = future.result()
                if match:
                    results[item_id] = match
                    t = match['tipo']
                    if t in ['PointAddress', 'StreetAddress', 'StreetAddressExt']:
                        exact_count += 1
                        icon = "🏠 [NÚMERO EXATO]"
                    elif t in ['StreetName', 'StreetInt', 'StreetName_OSM']:
                        street_count += 1
                        icon = "🛣️ [NA RUA]"
                    else:
                        fallback_count += 1
                        icon = "📍 [LOCALIDADE]"
                        
                    nome_str = orig_item['nome'][:38]
                    print(f"[{completed_count:03d}/{total:03d}] {nome_str} -> {icon} ({match['lat']:.5f}, {match['lon']:.5f}) - {match['tipo']}")
                else:
                    fallback_count += 1
                    print(f"[{completed_count:03d}/{total:03d}] {orig_item['nome'][:38]} -> ⚠️ Mantido sem alteração")
            except Exception as e:
                print(f"[{completed_count:03d}/{total:03d}] Erro em {orig_item['id']}: {e}")
                
            # Checkpoint a cada 50
            if completed_count % 50 == 0 or completed_count == total:
                # Atualizar JSON em memória e salvar
                for it in items:
                    iid = it.get('id')
                    if iid in results:
                        m = results[iid]
                        it['lat'] = m['lat']
                        it['lon'] = m['lon']
                        if m['tipo'] in ['PointAddress', 'StreetAddress', 'StreetAddressExt']:
                            it['precisao_gps'] = 'EXATA_ROOFTOP'
                        elif 'Street' in m['tipo']:
                            it['precisao_gps'] = 'LOGRADOURO_CENTRO'
                        else:
                            it['precisao_gps'] = 'APROXIMADA'
                            
                with open(JSON_PATH, 'w', encoding='utf-8') as f_out:
                    json.dump(items, f_out, ensure_ascii=False, indent=2)
                print(f"💾 Checkpoint: {completed_count}/{total} salvos no JSON...")

    # Gerar CSV atualizado
    print("\n📄 Gerando CSV mestre atualizado...")
    fieldnames = [
        "id", "nome", "categoria", "distrito", "bairro", "endereco",
        "cep", "predio_sala", "telefone", "email", "lat", "lon",
        "hub_id", "hub_nome", "horario_funcionamento", "descricao", "precisao_gps"
    ]
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for it in items:
            row = {k: it.get(k, '') for k in fieldnames}
            writer.writerow(row)
    print(f"✅ CSV atualizado salvo em: {CSV_PATH}")

    # Sincronizar HTMLs
    print("\n🔄 Sincronizando index.html e gerenciador_enderecos.html...")
    try:
        subprocess.run(["node", "scripts/sincronizar_html.js"], check=True)
    except Exception as e:
        print(f"Erro ao sincronizar HTMLs: {e}")

    elapsed = time.time() - t0
    print("\n" + "=" * 75)
    print(f"🎉 CALIBRAÇÃO GIS CONCLUÍDA EM {elapsed:.1f} SEGUNDOS!")
    print(f"🏠 Número Predial / Fachada Exata: {exact_count}")
    print(f"🛣️ Eixo da Rua Correta: {street_count}")
    print(f"📍 Demais / Fallbacks: {fallback_count}")
    print(f"🎯 Total Calibrados com Sucesso: {len(results)}/{total} ({len(results)/total*100:.1f}%)")
    print("=" * 75)

if __name__ == '__main__':
    main()
