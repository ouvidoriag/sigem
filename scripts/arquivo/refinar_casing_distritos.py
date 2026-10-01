import json
import re

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
    eqs = json.load(f)

modificados = 0

for e in eqs:
    old_bairro = e.get('bairro', '')
    old_dist = str(e.get('distrito', ''))
    b = old_bairro.strip()
    d = old_dist.strip()

    # Casing normalization
    if b == 'AMAPÁ':
        b = 'Amapá'
    elif b == 'IMBARIÊ':
        b = 'Imbariê'
    elif b == 'PILAR':
        b = 'Pilar'
    elif b == 'SANTO ANTÔNIO':
        b = 'Santo Antônio'
    elif b == 'Vila leopoldina':
        b = 'Vila Leopoldina'
    elif b == 'XERÉM':
        b = 'Xerém'
    elif b == 'Chácara Arcampo - Vila Maria elena':
        b = 'Chácaras Arcampo'
    elif b == 'Cidade Dos Meninos':
        b = 'Cidade dos Meninos'

    # Specific district alignments based on address reality
    # Santa Cruz da Serra is 3º Distrito
    if b == 'Santa Cruz da Serra':
        d = '3'
    # Parque Eldorado is a locality of Santa Cruz da Serra (3º Distrito)
    elif b == 'Parque Eldorado':
        d = '3'
    # Parque Capivari (Av. Marquês de Barbacena) is 3º Distrito
    elif b == 'Parque Capivari':
        d = '3'
    # rec_434 is Rua Marquês de Barbacena, so it's Parque Capivari, Dist 3
    if e['id'] == 'rec_434':
        b = 'Parque Capivari'
        d = '3'
    # rec_esc_153 is Estrada São Lourenço - Capivari (Distrito 4)
    if e['id'] == 'rec_esc_153':
        d = '4'
    # Vila Canaã: USF Vila Canaã (rec_76) and E M Montese (rec_esc_140) both Bonsucesso / Havana
    if b == 'Vila Canaã':
        d = '3'
    # Vila Maria Helena: CRAS, CREAS, CF e Escola Jornalista Moacyr Padilha
    # In official municipal map, Vila Maria Helena is linked to 2º Distrito (Campos Elíseos)
    if b == 'Vila Maria Helena':
        d = '2'

    if b != old_bairro or d != old_dist:
        e['bairro'] = b
        e['distrito'] = d
        modificados += 1

print(f"Total de registros atualizados nesta etapa de refinamento: {modificados}")

with open('dados/todos_os_enderecos_duque_de_caxias.json', 'w', encoding='utf-8') as f:
    json.dump(eqs, f, indent=2, ensure_ascii=False)

print("Salvo dados/todos_os_enderecos_duque_de_caxias.json refinado.")
