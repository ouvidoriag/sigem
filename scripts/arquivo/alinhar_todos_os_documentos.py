import json
import sqlite3
import os

def alinhar_documentos():
    with open('dados/todos_os_enderecos_duque_de_caxias.json', 'r', encoding='utf-8') as f:
        eqs = json.load(f)

    # Agrupar por distrito e bairro
    dist_info = {
        '1': {'nome': '1º Distrito — Duque de Caxias (Sede / Centro)', 'bairros': {}},
        '2': {'nome': '2º Distrito — Campos Elíseos (Polo Industrial e Petroquímico)', 'bairros': {}},
        '3': {'nome': '3º Distrito — Imbariê / Santa Cruz da Serra (Comércio e Eixo Rodoviário)', 'bairros': {}},
        '4': {'nome': '4º Distrito — Xerém (Polo Tecnológico, Ambiental e Rural)', 'bairros': {}}
    }

    for e in eqs:
        d = str(e.get('distrito', ''))
        b = e.get('bairro', '').strip()
        if d in dist_info:
            dist_info[d]['bairros'][b] = dist_info[d]['bairros'].get(b, 0) + 1

    total_eqs = len(eqs)
    total_bairros = sum(len(d['bairros']) for d in dist_info.values())

    # ==========================================
    # 1. GERAR BAIRROS_DUQUE_DE_CAXIAS.md
    # ==========================================
    lines_transp = []
    lines_transp.append("# 📍 Catálogo Oficial de Bairros e Localidades de Duque de Caxias / RJ")
    lines_transp.append("")
    lines_transp.append("> **Base Consolidada e Normalizada:** Mapeamento integral dos **4 Distritos Administrativos**, **47 Bairros Mestres Oficiais** e **105 localidades/sub-bairros operacionais** abrigando os **442 equipamentos públicos municipais**.")
    lines_transp.append("")
    lines_transp.append("---")
    lines_transp.append("")
    lines_transp.append("## 📊 Resumo Executivo da Distribuição Territorial")
    lines_transp.append("")
    lines_transp.append("| Distrito | Denominação Oficial | Bairros / Localidades | Total de Equipamentos | Percentual (%) |")
    lines_transp.append("| :--- | :--- | :---: | :---: | :---: |")
    
    for d_id, d_data in sorted(dist_info.items()):
        cnt = sum(d_data['bairros'].values())
        b_cnt = len(d_data['bairros'])
        pct = (cnt / total_eqs) * 100
        lines_transp.append(f"| **{d_id}º Distrito** | **{d_data['nome'].split(' — ')[1]}** | {b_cnt} | **{cnt}** | {pct:.1f}% |")
    
    lines_transp.append(f"| **TOTAL CONSOLIDADO** | **Município de Duque de Caxias** | **{total_bairros}** | **{total_eqs}** | **100,0%** |")
    lines_transp.append("")
    lines_transp.append("---")
    lines_transp.append("")

    for d_id, d_data in sorted(dist_info.items()):
        cnt = sum(d_data['bairros'].values())
        b_cnt = len(d_data['bairros'])
        lines_transp.append(f"## 🏛️ {d_data['nome']} ({b_cnt} bairros/localidades — {cnt} equipamentos)")
        lines_transp.append("")
        lines_transp.append("| Nº | Bairro / Localidade Oficial | Equipamentos Cadastrados | Status Cadastral | Fontes Oficiais Integradas |")
        lines_transp.append("| :---: | :--- | :---: | :---: | :--- |")
        
        idx = 1
        for b_name, b_count in sorted(d_data['bairros'].items()):
            lines_transp.append(f"| {idx} | **{b_name}** | {b_count} | Ativo / Regular | `Base_Consolidada_Equipamentos_V2` |")
            idx += 1
        lines_transp.append("")

    content_transp = "\n".join(lines_transp) + "\n"

    path_transp = r"c:\Users\501379.PMDC\Desktop\Transparencia\BAIRROS_DUQUE_DE_CAXIAS.md"
    with open(path_transp, 'w', encoding='utf-8') as f:
        f.write(content_transp)
    print(f"Salvo {path_transp} com sucesso! ({len(content_transp)} bytes)")

    # ==========================================
    # 2. GERAR 02_Guia_Oficial_dos_90_Bairros_por_Distrito.md
    # ==========================================
    path_caderno = r"c:\Users\501379.PMDC\Desktop\enderecos\cadernos\06_Subprefeituras_Bairros_e_Comunidades\02_Guia_Oficial_dos_90_Bairros_por_Distrito.md"
    lines_caderno = []
    lines_caderno.append("# 🗺️ Guia Oficial dos Bairros e Regiões de Duque de Caxias por Distrito")
    lines_caderno.append("> [⬅️ Voltar ao Índice Geral](../../00_INDICE_GERAL.md)")
    lines_caderno.append("")
    lines_caderno.append("Este guia consolida a malha territorial do Município de Duque de Caxias, integrando a divisão em **4 Distritos Administrativos**, os **47 Bairros Mestres Canônicos** da Lei Orgânica Municipal e os **105 bairros e localidades operacionais** onde estão instaladas as unidades públicas municipais.")
    lines_caderno.append("")
    lines_caderno.append("---")
    lines_caderno.append("")
    lines_caderno.append("## 1. QUADRO GERAL POR DISTRITO")
    lines_caderno.append("")
    lines_caderno.append("| Distrito | Região / Característica | Localidades | Equipamentos Instalados |")
    lines_caderno.append("| :--- | :--- | :---: | :---: |")

    for d_id, d_data in sorted(dist_info.items()):
        cnt = sum(d_data['bairros'].values())
        b_cnt = len(d_data['bairros'])
        lines_caderno.append(f"| **{d_id}º Distrito** | {d_data['nome'].split(' — ')[1]} | {b_cnt} | **{cnt} unidades** |")

    lines_caderno.append(f"| **TOTAL** | **Duque de Caxias (Geral)** | **{total_bairros}** | **{total_eqs} unidades** |")
    lines_caderno.append("")
    lines_caderno.append("---")
    lines_caderno.append("")
    lines_caderno.append("## 2. RELAÇÃO DE BAIRROS E EQUIPAMENTOS INSTALADOS POR DISTRITO")
    lines_caderno.append("")

    for d_id, d_data in sorted(dist_info.items()):
        cnt = sum(d_data['bairros'].values())
        b_cnt = len(d_data['bairros'])
        lines_caderno.append(f"### 2.{d_id} {d_data['nome']} ({b_cnt} Localidades — {cnt} Equipamentos)")
        lines_caderno.append("")
        lines_caderno.append("| Nº | Nome Oficial do Bairro / Localidade | Total de Unidades Municipais Instaladas |")
        lines_caderno.append("| :---: | :--- | :---: |")

        idx = 1
        for b_name, b_count in sorted(d_data['bairros'].items()):
            lines_caderno.append(f"| {idx} | **{b_name}** | {b_count} |")
            idx += 1
        lines_caderno.append("")

    content_caderno = "\n".join(lines_caderno) + "\n"
    with open(path_caderno, 'w', encoding='utf-8') as f:
        f.write(content_caderno)
    print(f"Salvo {path_caderno} com sucesso! ({len(content_caderno)} bytes)")

    # Sincronizar cópia de espelho para Transparência se aplicável
    caderno_mirror = r"c:\Users\501379.PMDC\Desktop\Transparencia\PASTAS_DE_ENDERECOS\06_Subprefeituras_Bairros_e_Comunidades\02_Guia_Oficial_dos_90_Bairros_por_Distrito.md"
    if os.path.exists(os.path.dirname(caderno_mirror)):
        with open(caderno_mirror, 'w', encoding='utf-8') as f:
            f.write(content_caderno)
        print(f"Espelho sincronizado em {caderno_mirror}!")

alinhar_documentos()
