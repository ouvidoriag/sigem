# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json

tests = [
    "Rua Nossa Senhora da Glória, Duque de Caxias, RJ",
    "Rua Marquês de Lafaiete, 70, Parque Equitativa, Duque de Caxias, RJ",
    "Av. Brigadeiro Lima e Silva, 131, Parque Duque, Duque de Caxias, RJ",
    "Alameda Esmeralda, 206, Jardim Primavera, Duque de Caxias, RJ"
]

print("=== TESTANDO ESRI ARCGIS WORLD GEOCODER ===")
for q in tests:
    url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={urllib.parse.quote(q)}&f=json&outFields=Match_addr,Addr_type,Score"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            candidates = data.get('candidates', [])
            if candidates:
                best = candidates[0]
                print(f"Busca: '{q}'")
                print(f" -> Encontrado: {best['address']}")
                print(f" -> Score: {best['score']} | Tipo: {best['attributes'].get('Addr_type')}")
                print(f" -> Coords (lat, lon): {best['location']['y']}, {best['location']['x']}")
            else:
                print(f"Busca: '{q}' -> Nenhum resultado")
    except Exception as e:
        print(f"Erro em '{q}': {e}")
