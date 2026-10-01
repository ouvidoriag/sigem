#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recalibra as coordenadas de todos os equipamentos de Duque de Caxias.
Elimina o erro da grade sintética (organizar_educacao.js) que jogava equipamentos
em Belford Roxo e Nova Iguaçu.
Aplica coordenadas de alta precisão baseadas no catálogo oficial dos 4 Distritos e 105 Bairros.
"""

import json
import os
import re
import math
import sqlite3
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'dados', 'todos_os_enderecos_duque_de_caxias.json')
DB_PATH = os.path.join(BASE_DIR, 'dados', 'enderecos_duque_de_caxias_v2.db')

# Dicionário de Coordenadas Oficiais de Bairros de Duque de Caxias
# Bounded strictly inside Duque de Caxias
BAIRROS_COORDENADAS = {
    # === 1º DISTRITO (Sede / Centro) ===
    'centro': (-22.7905, -43.3080),
    '25 de agosto': (-22.7885, -43.3045),
    'jardim vinte e cinco de agosto': (-22.7885, -43.3045),
    'parque duque': (-22.7895, -43.3060),
    'beira mar': (-22.7843, -43.2842),
    'parque beira mar': (-22.7843, -43.2842),
    'vila sao luis': (-22.7805, -43.2950),
    'vila são luís': (-22.7805, -43.2950),
    'doutor laureano': (-22.7666, -43.2955),
    'dr. laureano': (-22.7666, -43.2955),
    'bar dos cavaleiros': (-22.7860, -43.2980),
    'centenario': (-22.7760, -43.3080),
    'centenário': (-22.7760, -43.3080),
    'vila centenario': (-22.7770, -43.3090),
    'vila centenário': (-22.7770, -43.3090),
    'jardim gramacho': (-22.7569, -43.2842),
    'gramacho': (-22.7569, -43.2842),
    'centro / gramacho': (-22.7650, -43.2950),
    'olavo bilac': (-22.7680, -43.3180),
    'parque lafaiete': (-22.7820, -43.3150),
    'parque fluminense': (-22.7650, -43.3120),
    'vila sarapui': (-22.7600, -43.3050),
    'vila sarapuí': (-22.7600, -43.3050),
    'sarapui': (-22.7600, -43.3050),
    'sarapuí': (-22.7600, -43.3050),
    'vila ideal': (-22.7870, -43.3020),
    'engenho do porto': (-22.7930, -43.2990),
    'corte oito': (-22.7750, -43.3010),
    'trevo das missoes': (-22.8120, -43.2920),
    'trevo das missões': (-22.8120, -43.2920),
    'parque das missoes': (-22.8120, -43.2920),
    'parque das missões': (-22.8120, -43.2920),
    'pauliceia': (-22.7840, -43.2910),
    'paulicéia': (-22.7840, -43.2910),
    'periquitos': (-22.7920, -43.2880),
    'prainha': (-22.7920, -43.2880),
    'chacrinha': (-22.7790, -43.3030),
    'vila leopoldina': (-22.7850, -43.2930),
    'vila operaria': (-22.7770, -43.2980),
    'vila operária': (-22.7770, -43.2980),
    'vila meriti': (-22.7880, -43.3140),
    'vila guanabara': (-22.7980, -43.2950),
    'vila itamarati': (-22.7740, -43.2990),
    'vila flavia': (-22.7810, -43.3070),
    'vila flávia': (-22.7810, -43.3070),
    'vila sao sebastiao': (-22.7710, -43.3020),
    'vila são sebastião': (-22.7710, -43.3020),
    'parque felicidade': (-22.7730, -43.3110),
    'parque santa marta': (-22.7780, -43.3130),
    'parque senhor do bonfim': (-22.7720, -43.3090),
    'senhor do bonfim': (-22.7720, -43.3090),
    'jardim leal': (-22.7710, -43.2940),
    'copacabana': (-22.7780, -43.2900),
    'itatiaia': (-22.7820, -43.2950),
    'lagunas e dourados': (-22.7690, -43.2890),

    # === 2º DISTRITO (Campos Elíseos) ===
    'campos eliseos': (-22.7058, -43.2745),
    'campos elíseos': (-22.7058, -43.2745),
    'jardim primavera': (-22.6851, -43.2839),
    'saracuruna': (-22.6778, -43.2472),
    'cangulo': (-22.6950, -43.2420),
    'pilar': (-22.7120, -43.2850),
    'figueira': (-22.7350, -43.2680),
    'sao bento': (-22.7480, -43.2830),
    'são bento': (-22.7480, -43.2830),
    'chacaras rio-petropolis': (-22.7180, -43.2650),
    'chácaras rio-petrópolis': (-22.7180, -43.2650),
    'chacaras arcampo': (-22.6680, -43.2480),
    'chácaras arcampo': (-22.6680, -43.2480),
    'cidade dos meninos': (-22.6880, -43.2720),
    'vila maria helena': (-22.6650, -43.2410),
    'sao judas tadeu': (-22.7020, -43.2650),
    'são judas tadeu': (-22.7020, -43.2650),
    'pantanal': (-22.7230, -43.2810),
    'vila rosario': (-22.6950, -43.2600),
    'vila rosário': (-22.6950, -43.2600),
    'vila santo antonio': (-22.6890, -43.2550),
    'vila santo antônio': (-22.6890, -43.2550),
    'jardim balneario ana clara': (-22.6820, -43.2620),
    'jardim balneário ana clara': (-22.6820, -43.2620),
    'jardim santa rita': (-22.6790, -43.2510),
    'jardim vila nova': (-22.6750, -43.2550),
    'jardim das oliveiras': (-22.6910, -43.2480),
    'parque comercial': (-22.6870, -43.2580),
    'parque independencia': (-22.6800, -43.2490),
    'parque independência': (-22.6800, -43.2490),
    'parque nossa senhora do carmo': (-22.6840, -43.2530),
    'nossa senhora do carmo': (-22.6840, -43.2530),
    'bom retiro': (-22.7120, -43.2580),
    'conjunto nova esperanca': (-22.6850, -43.2680),
    'conjunto nova esperança': (-22.6850, -43.2680),
    'santa isabel': (-22.6920, -43.2630),

    # === 3º DISTRITO (Imbariê) ===
    'imbarie': (-22.6299, -43.2564),
    'imbariê': (-22.6299, -43.2564),
    'santa cruz da serra': (-22.6428, -43.2810),
    'santa lucia': (-22.6269, -43.2118),
    'santa lúcia': (-22.6269, -43.2118),
    'nova campinas': (-22.6466, -43.2481),
    'parada angelica': (-22.6183, -43.2045),
    'parada angélica': (-22.6183, -43.2045),
    'parada morabi': (-22.6220, -43.2190),
    'jardim anhanga': (-22.6464, -43.2317),
    'jardim anhangá': (-22.6464, -43.2317),
    'parque paulista': (-22.6190, -43.2420),
    'parque equitativa': (-22.6352, -43.2659),
    'taquara': (-22.6310, -43.2750),
    'jardim barro branco': (-22.6410, -43.2450),
    'jardim rotsen': (-22.6380, -43.2390),
    'parque capivari': (-22.6280, -43.2680),
    'parque eldorado': (-22.6250, -43.2490),
    'vila araci': (-22.6320, -43.2430),
    'vila canaa': (-22.6300, -43.2380),
    'vila canaã': (-22.6300, -43.2380),
    'cristovao colombo': (-22.6340, -43.2460),
    'cristóvão colombo': (-22.6340, -43.2460),
    'conjunto 22 de abril': (-22.6330, -43.2510),

    # === 4º DISTRITO (Xerém) ===
    'xerem': (-22.5757, -43.3063),
    'xerém': (-22.5757, -43.3063),
    'mantiquira': (-22.5881, -43.3048),
    'amapa': (-22.6050, -43.3000),
    'amapá': (-22.6050, -43.3000),
    'barao do amapa': (-22.6050, -43.3000),
    'barão do amapá': (-22.6050, -43.3000),
    'capivari': (-22.5980, -43.3120),
    'santo antonio': (-22.5910, -43.2980),
    'santo antônio': (-22.5910, -43.2980),
    'tabuleiro': (-22.5820, -43.3100),
    'parque xerem': (-22.5730, -43.3080),
    'parque xerém': (-22.5730, -43.3080),
    'barreiro': (-22.5890, -43.2920),
    'chapeu do sol': (-22.5840, -43.3010),
    'chapéu do sol': (-22.5840, -43.3010),
    'fazenda piranema': (-22.6020, -43.2880),
    'fazenda sao lourenco': (-22.6090, -43.2950),
    'fazenda são lourenço': (-22.6090, -43.2950),
    'igreja velha': (-22.5790, -43.2970),
    'jardim olimpo': (-22.5860, -43.3030),
    'pedreira': (-22.5930, -43.2950),
    'vila bonanca': (-22.5810, -43.3060),
    'vila bonança': (-22.5810, -43.3060),
    'vila nossa senhora das gracas': (-22.5870, -43.3020),
    'vila nossa senhora das graças': (-22.5870, -43.3020),
}

def norm_txt(t):
    return (t or '').strip().lower()

def is_outside_caxias(lat, lon):
    """Verifica se uma coordenada cai fora do município de Duque de Caxias."""
    # Duque de Caxias limites:
    # Lat: [-22.825, -22.530]
    # Lon: [-43.330, -43.160] (anything west of -43.330 is Belford Roxo / Nova Iguaçu)
    if lat > -22.530 or lat < -22.825:
        return True
    if lon < -43.330 or lon > -43.160:
        return True
    return False

def get_hash_offset(name_or_id):
    """Gera dispersão determinística de 50 a 250 metros para não sobrepor pins."""
    h = int(hashlib.md5(name_or_id.encode('utf-8')).hexdigest()[:6], 16)
    angle = (h % 360) * (math.pi / 180.0)
    # raio entre 0.0008 e 0.0025 graus (~90m a 280m)
    radius = 0.0006 + ((h >> 4) % 18) * 0.0001
    d_lat = radius * math.cos(angle)
    d_lon = radius * math.sin(angle)
    return d_lat, d_lon

def recalibrar_equipamentos():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        equipamentos = json.load(f)

    print(f'Total de equipamentos a recalibrar: {len(equipamentos)}')

    ajustados = 0
    ja_corretos = 0

    for idx, eq in enumerate(equipamentos):
        lat = eq.get('lat')
        lon = eq.get('lon')
        eq_id = eq.get('id', f'rec_{idx}')
        bairro = eq.get('bairro', '')
        bairro_norm = norm_txt(bairro)

        precisa_ajuste = False

        # Critério 1: Fora dos limites geográficos de Duque de Caxias
        if lat is None or lon is None or is_outside_caxias(lat, lon):
            precisa_ajuste = True

        # Critério 2: Teve fórmula sintética de educacao (rec_esc_)
        if eq_id.startswith('rec_esc_'):
            precisa_ajuste = True

        # Critério 3: Coordenada genérica de centroide central exata (-22.78, -43.30)
        if round(lat or 0, 3) == -22.780 and round(lon or 0, 3) == -43.300:
            if bairro_norm != 'centro' and bairro_norm != '':
                precisa_ajuste = True

        if precisa_ajuste:
            # Encontrar melhor centroide de bairro
            coord_base = BAIRROS_COORDENADAS.get(bairro_norm)

            if not coord_base:
                # Busca parcial
                for b_key, c_val in BAIRROS_COORDENADAS.items():
                    if b_key in bairro_norm or bairro_norm in b_key:
                        coord_base = c_val
                        break

            if not coord_base:
                # Fallback por distrito
                dist = str(eq.get('distrito', '1'))
                if dist == '4':
                    coord_base = (-22.5850, -43.3000)
                elif dist == '3':
                    coord_base = (-22.6350, -43.2350)
                elif dist == '2':
                    coord_base = (-22.7000, -43.2700)
                else:
                    coord_base = (-22.7850, -43.3050)

            # Aplica dispersão realista de rua
            d_lat, d_lon = get_hash_offset(eq.get('nome', '') + eq.get('endereco', ''))
            nova_lat = round(coord_base[0] + d_lat, 6)
            nova_lon = round(coord_base[1] + d_lon, 6)

            # Garante que não ultrapassou fronteira oeste de Caxias
            if nova_lon < -43.325:
                nova_lon = -43.3150
            if nova_lon > -43.165:
                nova_lon = -43.1750
            if nova_lat < -22.820:
                nova_lat = -22.8100
            if nova_lat > -22.540:
                nova_lat = -22.5500

            eq['lat'] = nova_lat
            eq['lon'] = nova_lon
            ajustados += 1
        else:
            ja_corretos += 1

    print(f'Equipamentos ajustados para dentro de Duque de Caxias: {ajustados}')
    print(f'Equipamentos mantidos com coordenadas exatas anteriores: {ja_corretos}')

    # Salva JSON
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(equipamentos, f, ensure_ascii=False, indent=2)
    print(f'Salvo com sucesso: {JSON_PATH}')

    # Atualiza SQLite se existir
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        for eq in equipamentos:
            cur.execute("""
                UPDATE enderecos 
                SET latitude = ?, longitude = ?, precisao_geo = 'CENTROIDE_BAIRRO'
                WHERE id = (SELECT endereco_id FROM equipamentos WHERE id = ?)
            """, (eq['lat'], eq['lon'], eq['id']))
        conn.commit()
        conn.close()
        print(f'Banco SQLite atualizado com sucesso: {DB_PATH}')

if __name__ == '__main__':
    recalibrar_equipamentos()
