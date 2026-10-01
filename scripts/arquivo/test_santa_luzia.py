# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json

queries = [
    "Rua Nossa Senhora da Glória, Parque Equitativa, Duque de Caxias, RJ",
    "Rua Nossa Senhora da Glória, Duque de Caxias, RJ",
    "Rua Marquês de Lafaiete, 70, Parque Equitativa, Duque de Caxias, RJ",
    "Escola Municipal Santa Luzia, Duque de Caxias, RJ"
]

for q in queries:
    url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={urllib.parse.quote(q)}&f=json&outFields=Match_addr,Addr_type,Score"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=8) as resp:
        d = json.loads(resp.read().decode('utf-8'))
        cands = d.get('candidates', [])
        if cands:
            c = cands[0]
            print(f"Busca: '{q}'")
            print(f" -> Score: {c['score']} | Tipo: {c['attributes']['Addr_type']}")
            print(f" -> Endereco: {c['address']}")
            print(f" -> Lat/Lon: {c['location']['y']}, {c['location']['x']}")
        else:
            print(f"Busca: '{q}' -> Nada")
