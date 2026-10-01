# -*- coding: utf-8 -*-
import json

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    equips = json.load(f)

print("Verificando registros com bairro ou distrito indefinidos/anômalos...")
anomalias = []
for e in equips:
    b = str(e.get('bairro', '')).strip()
    d = str(e.get('distrito', '')).strip()
    if b in ['-', '', 'None'] or d in ['-', '', 'None'] or 'esquina' in b.lower():
        anomalias.append((e['id'], b, d, e['nome'], e.get('endereco', '')))

print(f"Total de anomalias encontradas: {len(anomalias)}")
for aid, ab, ad, anome, aend in anomalias:
    print(f"[{aid}] Bairro: '{ab}' | Dist: '{ad}' | Nome: {anome} | End: {aend}")
