import json

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    eqs = json.load(f)

bairros = set(e.get('bairro', '').strip() for e in eqs)

# Check case insensitivity
lower_map = {}
for b in sorted(bairros):
    low = b.lower()
    if low not in lower_map:
        lower_map[low] = []
    lower_map[low].append(b)

for low, blist in lower_map.items():
    if len(blist) > 1:
        print(f"Divergência de caixa: {blist}")
