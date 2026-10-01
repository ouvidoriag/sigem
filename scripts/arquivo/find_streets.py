# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json

overpass_url = "https://overpass-api.de/api/interpreter"
query = """[out:json][timeout:20];
(
  way(around:800, -22.636966, -43.264961)["highway"];
);
out tags;
"""
req = urllib.request.Request(
    overpass_url,
    data=urllib.parse.urlencode({'data': query}).encode('utf-8'),
    headers={'User-Agent': 'CaxiasMapAudit/1.0'}
)
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        d = json.loads(resp.read().decode('utf-8'))
        streets = set()
        for el in d.get('elements', []):
            name = el.get('tags', {}).get('name')
            if name:
                streets.add(name)
        print("Ruas ao redor de (-22.636966, -43.264961):")
        for s in sorted(list(streets)):
            print(" -", s)
except Exception as e:
    print("err:", e)
