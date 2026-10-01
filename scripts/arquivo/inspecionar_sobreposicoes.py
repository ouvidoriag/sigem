import json

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    eqs = json.load(f)

alvo = ['santa cruz da serra', 'capivari', 'parque capivari', 'parque eldorado', 'vila maria helena', 'vila canaã', 'vila canaa']

for e in eqs:
    b = e.get('bairro', '').strip()
    d = str(e.get('distrito', ''))
    if b.lower() in alvo:
        print(f"{e['id']} | Dist:{d} | Bairro:{b} | Nome:{e['nome'][:35]} | End:{e.get('logradouro','')[:35]}")
