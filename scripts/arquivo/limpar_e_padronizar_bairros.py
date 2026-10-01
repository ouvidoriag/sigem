# -*- coding: utf-8 -*-
"""
Script de Limpeza, Normalização e Padronização Completa de Bairros e Distritos
Município de Duque de Caxias - RJ | Base Oficial Consolidada 2026
"""

import json
import csv
import re
import os
import shutil

JSON_PATH = os.path.join('dados', 'todos_os_enderecos_duque_de_caxias.json')
CSV_PATH = os.path.join('dados', 'todos_os_enderecos_duque_de_caxias.csv')

def main():
    print("Iniciando limpeza e padronização completa...")

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        equips = json.load(f)

    # 1. CORREÇÃO ESPECÍFICA DAS 21 ANOMALIAS IDENTIFICADAS
    correcoes_especificas = {
        "rec_73": {"bairro": "Nossa Senhora do Carmo", "distrito": "2"},
        "rec_74": {"bairro": "Pantanal", "distrito": "2"},
        "rec_76": {"bairro": "Vila Canaã", "distrito": "3"},
        "rec_78": {"bairro": "Imbariê", "distrito": "3"},
        "rec_83": {"bairro": "Nova Campinas", "distrito": "3"},
        "rec_85": {"bairro": "Parque Paulista", "distrito": "3"},
        "rec_87": {"bairro": "Jardim Olimpo", "distrito": "4"},
        "rec_88": {"bairro": "Xerém", "distrito": "4"},
        "rec_90": {"bairro": "Jardim Primavera", "distrito": "2"},
        "rec_92": {"bairro": "Parque Fluminense", "distrito": "2"},
        "rec_93": {"bairro": "Vila Operária", "distrito": "1"},
        "rec_94": {"bairro": "Jardim Gramacho", "distrito": "1"},
        "rec_95": {"bairro": "Olavo Bilac", "distrito": "1"},
        "rec_97": {"bairro": "Pilar", "distrito": "2"},
        "rec_99": {"bairro": "Bom Retiro", "distrito": "2"},
        "rec_101": {"bairro": "Engenho do Porto", "distrito": "1"},
        "rec_104": {"bairro": "Doutor Laureano", "distrito": "1"},
        "rec_106": {"bairro": "Figueira", "distrito": "2"},
        "rec_110": {"bairro": "Pantanal", "distrito": "2"},
        "rec_113": {"bairro": "Pilar", "distrito": "2"},
        "rec_152": {"bairro": "25 de Agosto", "distrito": "1"}
    }

    # 2. MAPA DE PADRONIZAÇÃO TOPONÍMICA (Padroniza grafias e remove sufixos desnecessários)
    padronizacao_bairros = {
        "Vila São Luis": "Vila São Luís",
        "Vila São Luiz": "Vila São Luís",
        "Dr. Laureano": "Doutor Laureano",
        "Sarapuíí": "Sarapuí",
        "Vila Sarapuíí": "Vila Sarapuí",
        "Chácara Rio - Petrópolis": "Chácaras Rio-Petrópolis",
        "Chácara Rio-Petrópolis": "Chácaras Rio-Petrópolis",
        "Chácara Arcampo - Vila Maria Elena": "Chácaras Arcampo",
        "Chácaras Arcampo": "Chácaras Arcampo",
        "Cangulo - Saracuruna": "Cangulo",
        "Parque Independência - Saracuruna": "Parque Independência",
        "Santa Lucia - Imbariê": "Santa Lúcia",
        "Parada Morabi - Imbariê": "Parada Morabi",
        "Parque Eldorado - Santa Cruz da Serra": "Parque Eldorado",
        "Parque A Equitativa": "Parque Equitativa",
        "Santo Antônio - Xerém": "Santo Antônio",
        "Santo Antônio da Serra": "Santo Antônio",
        "Vila Santo Antônio - Pq. Comercial": "Vila Santo Antônio",
        "Vila Canaan": "Vila Canaã",
        "Vila N. S. das Graças (Xerém)": "Vila Nossa Senhora das Graças",
        "Chapéu do Sol - Xerem": "Chapéu do Sol",
        "Pedreira - Xerém": "Pedreira",
        "Jardim das Oliveiras - Pq. Comercial": "Jardim das Oliveiras",
        "Conjunto 22 de Abril - Imbariê": "Conjunto 22 de Abril",
        "Jardim Rotsen - Imbariê": "Jardim Rotsen",
        "Conjunto Nova Esperança - São Bento": "Conjunto Nova Esperança",
        "Nossa Senhora do carmo": "Nossa Senhora do Carmo"
    }

    total_corrigidos = 0

    for eq in equips:
        eid = eq.get('id')
        
        # Aplicar correções das 21 anomalias
        if eid in correcoes_especificas:
            c = correcoes_especificas[eid]
            eq['bairro'] = c['bairro']
            eq['distrito'] = c['distrito']
            total_corrigidos += 1
            continue

        # Aplicar padronização de nomes
        b_atual = str(eq.get('bairro', '')).strip()
        if b_atual in padronizacao_bairros:
            eq['bairro'] = padronizacao_bairros[b_atual]
            total_corrigidos += 1

        # Limpar distrito None
        d_atual = str(eq.get('distrito', '')).strip()
        if d_atual in ['None', '', '-']:
            eq['distrito'] = '1'

    print(f"Total de registros ajustados/padronizados: {total_corrigidos}")

    # Salvar JSON mestre atualizado
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(equips, f, ensure_ascii=False, indent=2)
    print(f"Salvo {JSON_PATH} com dados padronizados.")

    # 3. ATUALIZAR CSV MESTRE
    csv_headers = [
        'id', 'nome', 'sigla', 'categoria', 'distrito', 'bairro', 'endereco', 'cep',
        'predio_sala', 'telefone', 'email', 'horario_funcionamento', 'lat', 'lon',
        'hub_id', 'hub_nome', 'servicos', 'descricao'
    ]
    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers, delimiter=';')
        writer.writeheader()
        for eq in equips:
            row = {h: eq.get(h, '') for h in csv_headers}
            writer.writerow(row)
    print(f"Salvo {CSV_PATH} atualizado.")

    # 4. ATUALIZAR CSVS POR SETOR
    setor_map = {
        "01_secretarias_e_orgaos.csv": "Secretarias e Órgãos",
        "02_saude_completa.csv": ["Saúde Especializada / Hospitalar", "Saúde Básica (APS / USF / UBS)"],
        "03_educacao_smedc.csv": "Educação (SMEDC)",
        "04_fundec.csv": "FUNDEC",
        "05_assistencia_social.csv": "Assistência Social (SEASDIH)",
        "06_seguranca_subprefeituras_cultura.csv": "Segurança, Subprefeituras e Cultura"
    }
    for fname, cat_filtro in setor_map.items():
        fpath = os.path.join('dados', 'por_setor', fname)
        if isinstance(cat_filtro, list):
            items_setor = [e for e in equips if e.get('categoria') in cat_filtro]
        else:
            items_setor = [e for e in equips if e.get('categoria') == cat_filtro]
        
        with open(fpath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers, delimiter=';')
            writer.writeheader()
            for eq in items_setor:
                row = {h: eq.get(h, '') for h in csv_headers}
                writer.writerow(row)
    print("Planilhas segmentadas em dados/por_setor/ atualizadas.")

    # 5. ATUALIZAR index.html e gerenciador_enderecos.html
    import subprocess
    subprocess.run(["node", "scripts/atualizar_gerenciador_com_orienta.js"], check=True)
    print("index.html e gerenciador_enderecos.html sincronizados com o JSON padronizado.")

    # 6. RE-EXECUTAR MIGRAÇÃO DO BANCO V2 (SQLite e SQL Dump)
    subprocess.run(["python", "scripts/migrar_banco_v2.py"], check=True)
    print("Banco de dados SQLite V2 e dump SQL ANSI recriados com dados 100% limpos.")

    # 7. Sincronizar com pasta Transparência
    transp_base = r'c:\Users\501379.PMDC\Desktop\Transparencia\PASTAS_DE_ENDERECOS\07_Bases_Consolidadas'
    if os.path.exists(transp_base):
        shutil.copy2(JSON_PATH, os.path.join(transp_base, 'todos_os_enderecos_duque_de_caxias.json'))
        shutil.copy2(CSV_PATH, os.path.join(transp_base, 'todos_os_enderecos_duque_de_caxias.csv'))
        shutil.copy2(os.path.join('dados', 'enderecos_duque_de_caxias_v2.db'), os.path.join(transp_base, 'enderecos_duque_de_caxias_v2.db'))
        shutil.copy2(os.path.join('dados', 'schema_e_dados_v2.sql'), os.path.join(transp_base, 'schema_e_dados_v2.sql'))
        print("Bases sincronizadas com Transparencia/PASTAS_DE_ENDERECOS/07_Bases_Consolidadas.")

    print("\nProcesso de limpeza e padronização concluído com sucesso!")

if __name__ == '__main__':
    main()
