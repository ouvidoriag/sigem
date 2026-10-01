import json

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    eqs = json.load(f)

targets = ['rec_esc_119', 'rec_esc_162', 'rec_esc_147', 'rec_esc_153', 'rec_esc_188', 'rec_esc_40', 'rec_esc_76', 'rec_esc_158', 'rec_130', 'rec_100', 'rec_76', 'rec_esc_140', 'rec_364', 'rec_368', 'rec_116', 'rec_esc_125', 'rec_434']

for e in eqs:
    if e['id'] in targets:
        print(f"{e['id']} | Dist:{e.get('distrito')} | Bairro:{e.get('bairro')} | Nome:{e.get('nome')} | End:{e.get('endereco')}")
