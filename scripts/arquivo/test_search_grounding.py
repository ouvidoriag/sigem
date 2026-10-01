# -*- coding: utf-8 -*-
import urllib.request
import json

import os

k = os.getenv('GEMINI_API_KEY', 'SUA_CHAVE_GEMINI_AQUI')
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={k}'


prompt = """
Pesquise no Google o endereço oficial e as coordenadas de satélite (latitude e longitude) da:
Escola Municipal Santa Luzia no Parque Equitativa, Duque de Caxias - RJ.
Endereço registrado: Rua Nossa Senhora da Glória (ou Rua Marquês de Lafaiete, 70), Parque Equitativa.
Retorne um JSON com:
{
  "nome": "...",
  "endereco_correto": "...",
  "lat": -22.xxxxxx,
  "lon": -43.xxxxxx,
  "como_encontrou": "..."
}
"""

payload = json.dumps({
    'contents': [{'parts': [{'text': prompt}]}],
    'tools': [{'google_search': {}}]
}).encode('utf-8')

req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        text = res['candidates'][0]['content']['parts'][0]['text']
        print('RESULTADO:')
        print(text)
except Exception as e:
    print('Erro:', e)
