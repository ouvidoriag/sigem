# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json

overpass_url = "https://overpass-api.de/api/interpreter"
query = """[out:json][timeout:25];
area["name"="Duque de Caxias"]->.a;
(
  way["name"~"Nossa Senhora da Glória",i](area.a);
  way["name"~"Lafaiete",i](area.a);
  nwr["name"~"Santa Luzia",i](area.a);
);
out center;
"""

req = urllib.request.Request(
    overpass_url, 
    data=urllib.parse.urlencode({'data': query}).encode('utf-8'),
    headers={'User-Agent': 'PrefeituraDuqueDeCaxiasGeo/1.0'}
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Elementos encontrados:", len(data.get('elements', [])))
        for el in data.get('elements', [])[:10]:
            name = el.get('tags', {}).get('name')
            center = el.get('center') or {'lat': el.get('lat'), 'lon': el.get('lon')}
            print(f"- {name}: {center}")
except Exception as e:
    print("Erro Overpass:", e)
