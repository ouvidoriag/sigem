# -*- coding: utf-8 -*-
import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os

keys = [k.strip() for k in os.getenv('GOOGLE_MAPS_API_KEYS', os.getenv('GOOGLE_MAPS_API_KEY', '')).split(',') if k.strip()]
if not keys:
    keys = ['SUA_CHAVE_AQUI']


print("=" * 75)
print("TESTANDO AS 17 CHAVES NA GOOGLE GEOCODING API")
print("=" * 75)

ativas = []

for idx, k in enumerate(keys, 1):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address=Praca+do+Pacificador,+Duque+de+Caxias,+RJ&key={k}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            status = data.get('status')
            err_msg = data.get('error_message', '')
            results = data.get('results', [])
            
            if status == 'OK':
                loc = results[0]['geometry']['location']
                lat = loc.get('lat')
                lng = loc.get('lng')
                print(f"Chave #{idx:02d} [{k[:16]}...] -> ✅ ATIVADA E FUNCIONANDO! Coords: {lat}, {lng}")
                ativas.append(k)
            elif status == 'REQUEST_DENIED':
                print(f"Chave #{idx:02d} [{k[:16]}...] -> ❌ REQUEST_DENIED: {err_msg}")
            else:
                print(f"Chave #{idx:02d} [{k[:16]}...] -> ❌ Status: {status} | {err_msg}")
    except Exception as e:
        print(f"Chave #{idx:02d} [{k[:16]}...] -> ❌ Falha na requisição: {e}")

print("=" * 75)
if ativas:
    print(f"🎉 TOTAL DE CHAVES COM GOOGLE GEOCODING ATIVADA: {len(ativas)}")
    for a in ativas:
        print(f"  - {a}")
else:
    print("⚠️ NENHUMA das 17 chaves está com a Google Geocoding API ativada.")
print("=" * 75)
