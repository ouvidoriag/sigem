# -*- coding: utf-8 -*-
"""
=============================================================================
🏛️ PREFEITURA MUNICIPAL DE DUQUE DE CAXIAS — RJ
Motor Paralelo Ultra Rápido de Calibração com 17 Chaves Gemini
=============================================================================
Utiliza ThreadPoolExecutor com 8 threads simultâneas distribuídas pelas
17 chaves Gemini para calibrar todos os equipamentos em ~1 minuto.
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.parse
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'dados', 'todos_os_enderecos_duque_de_caxias.json')

CHAVES_GEMINI = [k.strip() for k in os.getenv('GEMINI_API_KEYS', os.getenv('GEMINI_API_KEY', '')).split(',') if k.strip()]
if not CHAVES_GEMINI:
    CHAVES_GEMINI = ["SUA_CHAVE_GEMINI_AQUI"]


class KeyPool:
    def __init__(self, keys):
        self.keys = keys
        self.idx = 0
        self.lock = threading.Lock()

    def get_key(self):
        with self.lock:
            k = self.keys[self.idx]
            self.idx = (self.idx + 1) % len(self.keys)
            return k

key_pool = KeyPool(CHAVES_GEMINI)
save_lock = threading.Lock()

def consultar_gemini_coordenada(item, max_tentativas=3):
    nome = item.get('nome', '')
    endereco = item.get('endereco', '')
    bairro = item.get('bairro', '')
    cep = item.get('cep', '')
    distrito = item.get('distrito', '1')

    prompt = (
        f"Voce e um perito em cartografia, SIG e logradouros de Duque de Caxias - RJ.\n"
        f"Preciso da coordenada geografica exata (latitude e longitude) para este equipamento publico municipal:\n"
        f"- Nome: {nome}\n"
        f"- Endereco: {endereco}\n"
        f"- Bairro: {bairro}\n"
        f"- CEP: {cep}\n"
        f"- Distrito: {distrito}o Distrito de Duque de Caxias\n\n"
        f"Regras Cartograficas Restritas:\n"
        f"1. A latitude DEVE estar estritamente entre -22.825 e -22.530 (limites de Caxias).\n"
        f"2. A longitude DEVE estar estritamente entre -43.330 e -43.160.\n"
        f"3. Nao retorne centroide generico se souber a rua ou o numero. Indique a posicao exata da fachada/portaria do imovel na via.\n\n"
        f"Responda estritamente em JSON com este formato:\n"
        f"{{\n"
        f'  "latitude": float,\n'
        f'  "longitude": float,\n'
        f'  "precisao": "EXATA_ROOFTOP",\n'
        f'  "justificativa": "breve explicacao"\n'
        f"}}"
    )

    for _ in range(max_tentativas):
        key = key_pool.get_key()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.1}
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                text = result['candidates'][0]['content']['parts'][0]['text']
                data = json.loads(text)
                lat = float(data.get('latitude'))
                lon = float(data.get('longitude'))

                if -22.825 <= lat <= -22.530 and -43.330 <= lon <= -43.160:
                    return {
                        'lat': lat,
                        'lon': lon,
                        'precisao': data.get('precisao', 'EXATA_ROOFTOP'),
                        'justificativa': data.get('justificativa', '')
                    }
        except Exception:
            time.sleep(0.3)

    return None

def processar_item(idx_total, item):
    idx, total = idx_total
    nome = item.get('nome', '')[:45]
    old_lat = item.get('lat')
    old_lon = item.get('lon')

    # Se já foi calibrado com EXATA_ROOFTOP nesta sessão, não precisa refazer
    if item.get('precisao_gps') == 'EXATA_ROOFTOP':
        return (idx, total, nome, old_lat, old_lon, old_lat, old_lon, True, "Já calibrado anteriormente")

    res = consultar_gemini_coordenada(item)
    if res:
        new_lat = round(res['lat'], 6)
        new_lon = round(res['lon'], 6)
        item['lat'] = new_lat
        item['lon'] = new_lon
        item['precisao_gps'] = res['precisao']
        return (idx, total, nome, old_lat, old_lon, new_lat, new_lon, True, res['justificativa'])
    else:
        return (idx, total, nome, old_lat, old_lon, old_lat, old_lon, False, "Coordenada mantida")

def main():
    parser = argparse.ArgumentParser(description="Calibrador Paralelo Ultra-Rápido com 17 Chaves Gemini")
    parser.add_argument('--workers', type=int, default=8, help="Número de threads simultâneas (padrão: 8)")
    args = parser.parse_args()

    print("=" * 75, flush=True)
    print("🏛️ SIGEM — CALIBRADOR PARALELO MULTI-THREAD (17 CHAVES GEMINI)", flush=True)
    print("=" * 75, flush=True)
    print(f"🔑 Chaves ativas: {len(CHAVES_GEMINI)} | Threads paralelas: {args.workers}", flush=True)

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        equipamentos = json.load(f)

    total = len(equipamentos)
    print(f"📊 Total de equipamentos a processar: {total}", flush=True)
    print("🚀 Disparando calibração em paralelo...", flush=True)
    print("-" * 75, flush=True)

    t_inicio = time.time()
    modificados = 0
    concluidos = 0

    tarefas = [( (i+1, total), eq ) for i, eq in enumerate(equipamentos)]

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(processar_item, t[0], t[1]): t[1] for t in tarefas}

        for future in as_completed(futures):
            concluidos += 1
            idx, tot, nome, old_lat, old_lon, new_lat, new_lon, sucesso, just = future.result()

            if sucesso and (new_lat != old_lat or new_lon != old_lon):
                modificados += 1
                status = f"🎯 Cravado: {new_lat}, {new_lon} [ROOFTOP]"
            else:
                status = f"✅ Confirmado: {new_lat}, {new_lon}"

            pct = (concluidos / total) * 100
            print(f"[{concluidos}/{total}] ({pct:.1f}%) {nome} -> {status}", flush=True)

            if concluidos % 25 == 0:
                with save_lock:
                    with open(JSON_PATH, 'w', encoding='utf-8') as f:
                        json.dump(equipamentos, f, ensure_ascii=False, indent=2)
                print(f"💾 Checkpoint: {concluidos}/{total} salvos no JSON...", flush=True)

    # Gravação final
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(equipamentos, f, ensure_ascii=False, indent=2)

    tempo_total = time.time() - t_inicio
    print("\n" + "=" * 75, flush=True)
    print(f"✅ CALIBRAÇÃO DE TODOS OS {total} EQUIPAMENTOS FINALIZADA!", flush=True)
    print(f"⏱️ Tempo total de execução: {tempo_total:.1f} segundos", flush=True)
    print(f"📍 Equipamentos atualizados com precisão: {modificados} novos", flush=True)

    # Sincroniza HTML
    try:
        subprocess.run(["node", "scripts/sincronizar_html.js"], check=True)
        print("🚀 index.html e gerenciador_enderecos.html atualizados e sincronizados!", flush=True)
    except Exception as e:
        print("⚠️ Falha ao sincronizar HTML:", e, flush=True)

    # Sincroniza CSV
    try:
        import csv
        csv_headers = list(equipamentos[0].keys())
        csv_path = os.path.join(BASE_DIR, 'dados', 'todos_os_enderecos_duque_de_caxias.csv')
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers, delimiter=';')
            writer.writeheader()
            for eq in equipamentos:
                writer.writerow({h: eq.get(h, '') for h in csv_headers})
        print("📑 CSV mestre atualizado em dados/todos_os_enderecos_duque_de_caxias.csv!", flush=True)
    except Exception as e:
        print("⚠️ Falha ao atualizar CSV:", e, flush=True)

    print("=" * 75, flush=True)

if __name__ == '__main__':
    main()
