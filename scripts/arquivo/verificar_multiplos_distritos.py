import json

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    eqs = json.load(f)

bairro_dist = {}
for e in eqs:
    b = e.get('bairro', '').strip()
    d = str(e.get('distrito', ''))
    if b not in bairro_dist:
        bairro_dist[b] = set()
    bairro_dist[b].add(d)

for b, dists in sorted(bairro_dist.items()):
    if len(dists) > 1:
        print(f"Bairro em múltiplos distritos: '{b}' -> Distritos: {sorted(list(dists))}")
