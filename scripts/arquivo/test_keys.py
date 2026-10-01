# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json

import os

keys = [k.strip() for k in os.getenv('GEMINI_API_KEYS', os.getenv('GEMINI_API_KEY', '')).split(',') if k.strip()]
if not keys:
    keys = ['SUA_CHAVE_AQUI']


print("=== TESTANDO GOOGLE GEOCODING API ===")
for k in keys:
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address=Praca+do+Pacificador,+Duque+de+Caxias,+RJ&key={k}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            status = data.get('status')
            msg = data.get('error_message', '')
            print(f"Key {k[:15]}... -> Geocoding status: {status} | {msg}")
    except Exception as e:
        print(f"Key {k[:15]}... -> Geocoding exception: {e}")

print("\n=== TESTANDO GOOGLE GEMINI API ===")
for k in keys:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={k}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'models' in data:
                print(f"Key {k[:15]}... -> Gemini OK! Modelos: {len(data['models'])}")
            else:
                print(f"Key {k[:15]}... -> Gemini: {data}")
    except Exception as e:
        pass
