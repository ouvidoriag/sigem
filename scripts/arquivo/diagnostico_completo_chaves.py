# -*- coding: utf-8 -*-
"""
Diagnóstico Completo de Todas as 20 Chaves de API
Testa cada chave contra:
- Geocoding API
- Places API (Legacy)
- Places API (New)
- Gemini API (AI Studio)
- Maps Static API
"""

import urllib.request
import urllib.parse
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os

env_keys = [k.strip() for k in os.getenv('GOOGLE_API_KEYS', os.getenv('GEMINI_API_KEY', '')).split(',') if k.strip()]
if env_keys:
    all_keys = [(f"Chave {i+1:02d}", k) for i, k in enumerate(env_keys)]
else:
    all_keys = [
        ("Chave 01", "SUA_CHAVE_GEMINI_OU_MAPS_AQUI")
    ]


def test_key(label, k):
    res = {
        'label': label,
        'prefix': k[:15],
        'type': 'Google AI Studio (Gemini)' if k.startswith('AQ.') else 'Google Cloud',
        'geocoding': False,
        'geocoding_msg': '',
        'gemini': False,
        'gemini_msg': '',
        'places': False,
        'places_msg': ''
    }
    
    # 1. Test Geocoding
    url_geo = f"https://maps.googleapis.com/maps/api/geocode/json?address=Duque+de+Caxias&key={k}"
    try:
        req = urllib.request.Request(url_geo, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode('utf-8'))
            if d.get('status') == 'OK':
                res['geocoding'] = True
                res['geocoding_msg'] = 'OK (Ativo e liberado)'
            else:
                msg = d.get('error_message', d.get('status'))
                if 'Billing' in msg:
                    res['geocoding_msg'] = 'API Ativa, mas requer Faturamento (Billing)'
                elif 'not activated' in msg:
                    res['geocoding_msg'] = 'Geocoding não ativado no projeto'
                elif 'invalid' in msg:
                    res['geocoding_msg'] = 'Chave inválida para Google Maps (chave de IA)'
                else:
                    res['geocoding_msg'] = msg[:50]
    except Exception as e:
        res['geocoding_msg'] = str(e)[:50]

    # 2. Test Gemini
    url_gem = f"https://generativelanguage.googleapis.com/v1beta/models?key={k}"
    try:
        req = urllib.request.Request(url_gem, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode('utf-8'))
            if 'models' in d:
                res['gemini'] = True
                res['gemini_msg'] = f"OK ({len(d['models'])} modelos disponíveis)"
            else:
                res['gemini_msg'] = 'Não habilitado'
    except Exception as e:
        res['gemini_msg'] = 'Não habilitado / Erro 403'

    # 3. Test Places
    url_places = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=Duque+de+Caxias&key={k}"
    try:
        req = urllib.request.Request(url_places, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode('utf-8'))
            if d.get('status') == 'OK':
                res['places'] = True
                res['places_msg'] = 'OK (Ativo)'
            else:
                msg = d.get('error_message', d.get('status'))
                if 'Billing' in msg:
                    res['places_msg'] = 'Requer Faturamento'
                elif 'legacy' in msg.lower():
                    res['places_msg'] = 'Requer Places API (New)'
                elif 'invalid' in msg:
                    res['places_msg'] = 'Chave inválida para Maps'
                else:
                    res['places_msg'] = msg[:40]
    except Exception as e:
        res['places_msg'] = str(e)[:40]

    return res

print("=" * 80)
print(f"AUDITORIA COMPLETA DE TODAS AS {len(all_keys)} CHAVES")
print("=" * 80)

results = []
for label, k in all_keys:
    r = test_key(label, k)
    results.append(r)
    status_geo = "✅ LIBERADA" if r['geocoding'] else f"❌ {r['geocoding_msg']}"
    status_gem = "✅ ATIVO" if r['gemini'] else "❌ NÃO"
    print(f"[{r['label']}] {r['prefix']}... ({r['type']})")
    print(f"   ├─ Google Geocoding API: {status_geo}")
    print(f"   ├─ Google Gemini AI:     {status_gem} ({r['gemini_msg']})")
    print(f"   └─ Google Places API:    {r['places_msg']}")

print("=" * 80)
