#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza index.html e gerenciador_enderecos.html com:
1. Base recalibrada com 442 equipamentos estritamente em Duque de Caxias (zero pontos fora do município).
2. O fluxo perfeito de cadastro/edição:
   CEP -> ViaCEP -> Auto-preenchimento -> Número do Imóvel -> Geocodificação -> Lat/Lon -> Marcador no Mapa.
3. Mini-mapa interativo com:
   - Marcador arrastável
   - Botão [ Ajustar localização manualmente ]
   - Clique em qualquer rua para posicionar o pin
4. Controle de camadas no mapa principal:
   - Alternar Camada de Hubs (12 polos)
   - Alternar Camada de Equipamentos (442 pontos)
   - Filtros por Distrito e Categoria
   - Enquadramento com Bounding Box oficial de Duque de Caxias.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'dados', 'todos_os_enderecos_duque_de_caxias.json')
HTML_PATH = os.path.join(BASE_DIR, 'index.html')
GERENCIADOR_PATH = os.path.join(BASE_DIR, 'gerenciador_enderecos.html')

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    equips = json.load(f)

print(f"Total de equipamentos carregados do JSON recalibrado: {len(equips)}")

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Extrair DEFAULT_HUBS de forma resiliente
hubs_start = html.find('const DEFAULT_HUBS = ') + len('const DEFAULT_HUBS = ')
hubs_end = html.find('const PMDC_DB_VERSION', hubs_start)
hubs_raw = html[hubs_start:hubs_end]
if '//' in hubs_raw:
    hubs_raw = hubs_raw[:hubs_raw.find('//')]
hubs_raw = hubs_raw.strip().rstrip(';')
hubs = json.loads(hubs_raw)
print(f"Total de Hubs carregados: {len(hubs)}")

# Garantir todos os campos em cada equipamento
for e in equips:
    if 'status' not in e or not e['status']: e['status'] = 'Ativo'
    if 'sigla' not in e: e['sigla'] = ''
    if 'secretaria_responsavel' not in e:
        cat = e.get('categoria', '')
        if 'Saúde' in cat: e['secretaria_responsavel'] = 'Secretaria Municipal de Saúde (SMS)'
        elif 'Educação' in cat: e['secretaria_responsavel'] = 'Secretaria Municipal de Educação (SMEDC)'
        elif 'FUNDEC' in cat: e['secretaria_responsavel'] = 'FUNDEC'
        elif 'Assistência' in cat: e['secretaria_responsavel'] = 'Secretaria Municipal de Assistência Social e Direitos Humanos (SEASDIH)'
        elif 'Segurança' in cat: e['secretaria_responsavel'] = 'Secretaria Municipal de Segurança Pública (SMSP)'
        else: e['secretaria_responsavel'] = 'Secretaria Municipal de Governo (SEGOV)'
    if 'tipo_equipamento' not in e: e['tipo_equipamento'] = 'Equipamento Municipal'
    if 'cnes_inep' not in e:
        ps = e.get('predio_sala', '')
        if 'CNES:' in ps: e['cnes_inep'] = ps.split('CNES:')[1].split('|')[0].strip()
        elif 'INEP:' in ps: e['cnes_inep'] = ps.split('INEP:')[1].split('|')[0].strip()
        else: e['cnes_inep'] = ''
    if 'numero' not in e: e['numero'] = ''
    if 'ponto_referencia' not in e: e['ponto_referencia'] = ''
    if 'telefone_secundario' not in e: e['telefone_secundario'] = ''
    if 'whatsapp' not in e: e['whatsapp'] = ''
    if 'email_secundario' not in e: e['email_secundario'] = ''
    if 'site' not in e: e['site'] = 'https://duquedecaxias.rj.gov.br'
    if 'observacoes' not in e: e['observacoes'] = ''

bairros_unicos = sorted(list(set([e.get('bairro', '').strip() for e in equips if e.get('bairro', '').strip() and e.get('bairro') != '-'])))
bairros_options = "\n".join([f'                  <option value="{b}">{b}</option>' for b in bairros_unicos])

# Dicionário de Bairros para injeção no JS do navegador (fallback de altíssima precisão)
BAIRROS_JS_DICT = {
    # 1º Distrito
    'centro': [-22.7905, -43.3080, '1'],
    '25 de agosto': [-22.7885, -43.3045, '1'],
    'jardim vinte e cinco de agosto': [-22.7885, -43.3045, '1'],
    'parque duque': [-22.7895, -43.3060, '1'],
    'beira mar': [-22.7843, -43.2842, '1'],
    'parque beira mar': [-22.7843, -43.2842, '1'],
    'vila sao luis': [-22.7805, -43.2950, '1'],
    'doutor laureano': [-22.7666, -43.2955, '1'],
    'bar dos cavaleiros': [-22.7860, -43.2980, '1'],
    'centenario': [-22.7760, -43.3080, '1'],
    'vila centenario': [-22.7770, -43.3090, '1'],
    'jardim gramacho': [-22.7569, -43.2842, '1'],
    'gramacho': [-22.7569, -43.2842, '1'],
    'olavo bilac': [-22.7680, -43.3180, '1'],
    'parque lafaiete': [-22.7820, -43.3150, '1'],
    'parque fluminense': [-22.7650, -43.3120, '1'],
    'vila sarapui': [-22.7600, -43.3050, '1'],
    'sarapui': [-22.7600, -43.3050, '1'],
    'vila ideal': [-22.7870, -43.3020, '1'],
    'engenho do porto': [-22.7930, -43.2990, '1'],
    'corte oito': [-22.7750, -43.3010, '1'],
    'trevo das missoes': [-22.8120, -43.2920, '1'],
    'parque das missoes': [-22.8120, -43.2920, '1'],
    'pauliceia': [-22.7840, -43.2910, '1'],
    'periquitos': [-22.7920, -43.2880, '1'],
    'prainha': [-22.7920, -43.2880, '1'],
    'chacrinha': [-22.7790, -43.3030, '1'],
    'vila leopoldina': [-22.7850, -43.2930, '1'],
    'vila operaria': [-22.7770, -43.2980, '1'],
    'vila meriti': [-22.7880, -43.3140, '1'],
    'vila guanabara': [-22.7980, -43.2950, '1'],
    'vila itamarati': [-22.7740, -43.2990, '1'],
    'vila flavia': [-22.7810, -43.3070, '1'],
    'vila sao sebastiao': [-22.7710, -43.3020, '1'],
    'parque felicidade': [-22.7730, -43.3110, '1'],
    'parque santa marta': [-22.7780, -43.3130, '1'],
    'parque senhor do bonfim': [-22.7720, -43.3090, '1'],
    'jardim leal': [-22.7710, -43.2940, '1'],
    'copacabana': [-22.7780, -43.2900, '1'],
    'itatiaia': [-22.7820, -43.2950, '1'],
    'lagunas e dourados': [-22.7690, -43.2890, '1'],

    # 2º Distrito
    'campos eliseos': [-22.7058, -43.2745, '2'],
    'jardim primavera': [-22.6851, -43.2839, '2'],
    'saracuruna': [-22.6778, -43.2472, '2'],
    'cangulo': [-22.6950, -43.2420, '2'],
    'pilar': [-22.7120, -43.2850, '2'],
    'figueira': [-22.7350, -43.2680, '2'],
    'sao bento': [-22.7480, -43.2830, '2'],
    'chacaras rio-petropolis': [-22.7180, -43.2650, '2'],
    'chacaras arcampo': [-22.6680, -43.2480, '2'],
    'cidade dos meninos': [-22.6880, -43.2720, '2'],
    'vila maria helena': [-22.6650, -43.2410, '2'],
    'sao judas tadeu': [-22.7020, -43.2650, '2'],
    'pantanal': [-22.7230, -43.2810, '2'],
    'vila rosario': [-22.6950, -43.2600, '2'],
    'vila santo antonio': [-22.6890, -43.2550, '2'],
    'jardim balneario ana clara': [-22.6820, -43.2620, '2'],
    'jardim santa rita': [-22.6790, -43.2510, '2'],
    'jardim vila nova': [-22.6750, -43.2550, '2'],
    'jardim das oliveiras': [-22.6910, -43.2480, '2'],
    'parque comercial': [-22.6870, -43.2580, '2'],
    'parque independencia': [-22.6800, -43.2490, '2'],
    'parque nossa senhora do carmo': [-22.6840, -43.2530, '2'],
    'nossa senhora do carmo': [-22.6840, -43.2530, '2'],
    'bom retiro': [-22.7120, -43.2580, '2'],
    'conjunto nova esperanca': [-22.6850, -43.2680, '2'],
    'santa isabel': [-22.6920, -43.2630, '2'],

    # 3º Distrito
    'imbarie': [-22.6299, -43.2564, '3'],
    'santa cruz da serra': [-22.6428, -43.2810, '3'],
    'santa lucia': [-22.6269, -43.2118, '3'],
    'nova campinas': [-22.6466, -43.2481, '3'],
    'parada angelica': [-22.6183, -43.2045, '3'],
    'parada morabi': [-22.6220, -43.2190, '3'],
    'jardim anhanga': [-22.6464, -43.2317, '3'],
    'parque paulista': [-22.6190, -43.2420, '3'],
    'parque equitativa': [-22.6352, -43.2659, '3'],
    'taquara': [-22.6310, -43.2750, '3'],
    'jardim barro branco': [-22.6410, -43.2450, '3'],
    'jardim rotsen': [-22.6380, -43.2390, '3'],
    'parque capivari': [-22.6280, -43.2680, '3'],
    'parque eldorado': [-22.6250, -43.2490, '3'],
    'vila araci': [-22.6320, -43.2430, '3'],
    'vila canaa': [-22.6300, -43.2380, '3'],
    'cristovao colombo': [-22.6340, -43.2460, '3'],
    'conjunto 22 de abril': [-22.6330, -43.2510, '3'],

    # 4º Distrito
    'xerem': [-22.5757, -43.3063, '4'],
    'mantiquira': [-22.5881, -43.3048, '4'],
    'amapa': [-22.6050, -43.3000, '4'],
    'barao do amapa': [-22.6050, -43.3000, '4'],
    'capivari': [-22.5980, -43.3120, '4'],
    'santo antonio': [-22.5910, -43.2980, '4'],
    'tabuleiro': [-22.5820, -43.3100, '4'],
    'parque xerem': [-22.5730, -43.3080, '4'],
    'barreiro': [-22.5890, -43.2920, '4'],
    'chapeu do sol': [-22.5840, -43.3010, '4'],
    'fazenda piranema': [-22.6020, -43.2880, '4'],
    'fazenda sao lourenco': [-22.6090, -43.2950, '4'],
    'igreja velha': [-22.5790, -43.2970, '4'],
    'jardim olimpo': [-22.5860, -43.3030, '4'],
    'pedreira': [-22.5930, -43.2950, '4'],
    'vila bonanca': [-22.5810, -43.3060, '4'],
    'vila nossa senhora das gracas': [-22.5870, -43.3020, '4'],
}

bairros_js_str = json.dumps(BAIRROS_JS_DICT, ensure_ascii=False)
equips_json_str = json.dumps(equips, ensure_ascii=False)
hubs_json_str = json.dumps(hubs, ensure_ascii=False)

TEMPLATE = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gestão de Endereços e Equipamentos — Prefeitura de Duque de Caxias</title>
  <meta name="description" content="Plataforma oficial de cadastro, edição, geocodificação e gestão de endereços dos equipamentos públicos de Duque de Caxias - RJ.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    :root {
      --navy-950: #070d18;
      --navy-900: #0f1b2d;
      --navy-800: #16243b;
      --navy-700: #1e3352;
      --blue-600: #0284c7;
      --blue-500: #0ea5e9;
      --blue-100: #e0f2fe;
      --emerald-600: #059669;
      --emerald-500: #10b981;
      --emerald-50: #ecfdf5;
      --amber-600: #d97706;
      --amber-500: #f59e0b;
      --amber-50: #fffbeb;
      --red-600: #dc2626;
      --red-500: #ef4444;
      --red-50: #fef2f2;
      --gray-50: #f8fafc;
      --gray-100: #f1f5f9;
      --gray-200: #e2e8f0;
      --gray-300: #cbd5e1;
      --gray-400: #94a3b8;
      --gray-500: #64748b;
      --gray-600: #475569;
      --gray-700: #334155;
      --gray-800: #1e293b;
      
      --bg-base: #f8fafc;
      --surface-card: #ffffff;
      --surface-subtle: #f1f5f9;
      --border: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.03);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-base);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
    }

    .top-header {
      background: linear-gradient(135deg, #09121f 0%, #0f1d32 50%, #152744 100%);
      color: #ffffff;
      padding: 16px 32px;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .header-content {
      max-width: 1680px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
    }
    .brand-section {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brasao-badge {
      width: 44px;
      height: 44px;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .title-group h1 {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #ffffff;
      line-height: 1.2;
    }
    .title-group p {
      font-size: 12px;
      color: var(--gray-400);
      margin-top: 2px;
      font-weight: 400;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .nav-bar {
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      padding: 0 32px;
      position: sticky;
      top: 77px;
      z-index: 90;
    }
    .nav-content {
      max-width: 1680px;
      margin: 0 auto;
      display: flex;
      gap: 8px;
      overflow-x: auto;
    }
    .nav-item {
      padding: 12px 16px;
      font-size: 13px;
      font-weight: 600;
      color: var(--gray-600);
      border-bottom: 2px solid transparent;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s ease;
      white-space: nowrap;
    }
    .nav-item:hover {
      color: var(--navy-900);
      border-bottom-color: var(--gray-300);
    }
    .nav-item.active {
      color: var(--blue-600);
      border-bottom-color: var(--blue-600);
    }
    .nav-item .count-pill {
      background: var(--gray-100);
      color: var(--gray-700);
      padding: 2px 7px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 700;
    }
    .nav-item.active .count-pill {
      background: var(--blue-100);
      color: var(--blue-600);
    }

    .main-body {
      max-width: 1680px;
      width: 100%;
      margin: 0 auto;
      padding: 24px 32px 64px 32px;
      flex: 1;
    }

    .kpi-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 20px;
    }
    .kpi-card {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 16px 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      align-items: center;
      gap: 14px;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }
    .kpi-icon {
      width: 44px;
      height: 44px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      flex-shrink: 0;
    }
    .kpi-icon-blue { background: var(--blue-100); color: var(--blue-600); }
    .kpi-icon-green { background: var(--emerald-50); color: var(--emerald-600); }
    .kpi-icon-amber { background: var(--amber-50); color: var(--amber-600); }
    .kpi-icon-red { background: var(--red-50); color: var(--red-600); }
    .kpi-meta { display: flex; flex-direction: column; }
    .kpi-value {
      font-size: 22px;
      font-weight: 800;
      color: var(--navy-900);
      letter-spacing: -0.02em;
      line-height: 1.1;
    }
    .kpi-label {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-top: 3px;
    }

    .toolbar-box {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 14px 18px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: var(--shadow-sm);
    }
    .search-filter-group {
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 1;
      max-width: 900px;
      flex-wrap: wrap;
    }
    .search-input-wrap {
      position: relative;
      flex: 1;
      min-width: 240px;
    }
    .search-input-wrap span {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 14px;
      color: var(--gray-400);
    }
    .search-input {
      width: 100%;
      padding: 9px 12px 9px 36px;
      font-size: 13px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      outline: none;
      background: var(--surface-subtle);
      transition: all 0.15s ease;
      font-family: inherit;
    }
    .search-input:focus {
      background: #ffffff;
      border-color: var(--blue-500);
      box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
    }
    .filter-select {
      padding: 9px 12px;
      font-size: 13px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      outline: none;
      background: #ffffff;
      color: var(--gray-700);
      font-family: inherit;
      cursor: pointer;
    }
    .filter-select:focus {
      border-color: var(--blue-500);
    }

    .table-container {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      margin-bottom: 16px;
    }
    .table-responsive {
      overflow-x: auto;
      width: 100%;
    }
    table.data-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }
    table.data-table thead {
      background: #f8fafc;
      border-bottom: 2px solid var(--border);
    }
    table.data-table th {
      padding: 12px 14px;
      font-size: 11px;
      font-weight: 700;
      color: var(--gray-600);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      white-space: nowrap;
    }
    table.data-table tbody tr {
      border-bottom: 1px solid var(--border);
      transition: background 0.1s ease;
    }
    table.data-table tbody tr:hover {
      background: #f8fafc;
    }
    table.data-table td {
      padding: 11px 14px;
      vertical-align: middle;
      color: var(--gray-800);
    }

    .cell-editable {
      cursor: pointer;
      position: relative;
      border-radius: var(--radius-sm);
      padding: 2px 4px;
      margin: -2px -4px;
      transition: background 0.15s ease;
    }
    .cell-editable:hover {
      background: rgba(14, 165, 233, 0.08);
      outline: 1px dashed var(--blue-500);
    }
    .cell-editable::after {
      content: '✏️';
      font-size: 10px;
      margin-left: 4px;
      opacity: 0;
      transition: opacity 0.15s ease;
    }
    .cell-editable:hover::after {
      opacity: 0.6;
    }

    .badge-status {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      user-select: none;
      transition: opacity 0.15s ease;
    }
    .badge-status:hover { opacity: 0.85; }
    .badge-status-ativo { background: var(--emerald-50); color: var(--emerald-600); border: 1px solid rgba(16,185,129,0.3); }
    .badge-status-pendente { background: var(--amber-50); color: var(--amber-600); border: 1px solid rgba(245,158,11,0.3); }
    .badge-status-desatualizado { background: var(--red-50); color: var(--red-600); border: 1px solid rgba(239,68,68,0.3); }

    .badge-cat {
      display: inline-block;
      padding: 3px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      background: var(--surface-subtle);
      color: var(--gray-700);
      border: 1px solid var(--border);
      white-space: nowrap;
    }
    .badge-distrito {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      white-space: nowrap;
      cursor: pointer;
    }
    .badge-hub {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      background: #fdf2f8;
      color: #be185d;
      border: 1px solid #fbcfe8;
      cursor: pointer;
    }

    .action-cell {
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .btn {
      padding: 7px 12px;
      font-size: 12px;
      font-weight: 600;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
      font-family: inherit;
    }
    .btn-primary {
      background: var(--blue-600);
      color: #ffffff;
    }
    .btn-primary:hover {
      background: #0369a1;
    }
    .btn-secondary {
      background: #ffffff;
      color: var(--gray-700);
      border-color: var(--border);
    }
    .btn-secondary:hover {
      background: var(--surface-subtle);
      color: var(--navy-900);
    }
    .btn-outline-primary {
      background: transparent;
      color: var(--blue-600);
      border-color: var(--blue-500);
    }
    .btn-outline-primary:hover {
      background: var(--blue-100);
    }
    .btn-navy {
      background: var(--navy-900);
      color: #ffffff;
    }
    .btn-navy:hover {
      background: var(--navy-800);
    }
    .btn-danger-outline {
      background: transparent;
      color: var(--red-600);
      border-color: rgba(220,38,38,0.3);
    }
    .btn-danger-outline:hover {
      background: var(--red-50);
    }
    .btn-xs {
      padding: 4px 8px;
      font-size: 11px;
    }
    .btn-sm {
      padding: 6px 10px;
      font-size: 12px;
    }

    .action-dropdown {
      position: relative;
      display: inline-block;
    }
    .action-dropdown-menu {
      position: absolute;
      right: 0;
      top: 100%;
      margin-top: 4px;
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      box-shadow: var(--shadow-lg);
      min-width: 170px;
      z-index: 50;
      display: none;
      padding: 4px 0;
    }
    .action-dropdown.open .action-dropdown-menu {
      display: block;
    }
    .action-dropdown-item {
      padding: 7px 12px;
      font-size: 12px;
      color: var(--gray-700);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: background 0.1s ease;
    }
    .action-dropdown-item:hover {
      background: var(--surface-subtle);
      color: var(--navy-900);
    }

    .pagination-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 18px;
      background: #f8fafc;
      border-top: 1px solid var(--border);
      font-size: 12px;
      color: var(--text-muted);
    }
    .pagination-pages {
      display: flex;
      gap: 4px;
    }
    .page-btn {
      padding: 4px 10px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: #ffffff;
      color: var(--gray-700);
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
    }
    .page-btn.active {
      background: var(--blue-600);
      color: #ffffff;
      border-color: var(--blue-600);
    }
    .page-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    /* MODAL PADRÃO */
    .modal-backdrop {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }
    .modal-backdrop.active {
      display: flex;
    }
    .modal-box {
      background: #ffffff;
      border-radius: var(--radius-lg);
      max-width: 900px;
      width: 100%;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.25);
      animation: modalFadeIn 0.2s ease-out;
    }
    @keyframes modalFadeIn {
      from { opacity: 0; transform: scale(0.97); }
      to { opacity: 1; transform: scale(1); }
    }
    .modal-head {
      padding: 18px 24px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-head h3 {
      font-size: 17px;
      font-weight: 800;
      color: var(--navy-900);
    }
    .modal-head p {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }
    .modal-close {
      background: transparent;
      border: none;
      font-size: 20px;
      color: var(--gray-400);
      cursor: pointer;
      line-height: 1;
      padding: 4px;
    }
    .modal-close:hover { color: var(--navy-900); }
    .modal-body {
      padding: 20px 24px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .modal-foot {
      padding: 14px 24px;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #f8fafc;
      border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    }

    .form-section {
      background: var(--surface-subtle);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 14px 18px;
    }
    .form-section-title {
      font-size: 12px;
      font-weight: 700;
      color: var(--navy-900);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 10px;
    }
    .form-row-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
      margin-bottom: 10px;
    }
    .form-ctrl {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .form-ctrl label {
      font-size: 11px;
      font-weight: 600;
      color: var(--gray-700);
    }
    .form-ctrl label span.req { color: var(--red-600); }
    .form-ctrl input, .form-ctrl select, .form-ctrl textarea {
      padding: 8px 10px;
      font-size: 12px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: #ffffff;
      outline: none;
      font-family: inherit;
    }
    .form-ctrl input:focus, .form-ctrl select:focus, .form-ctrl textarea:focus {
      border-color: var(--blue-500);
      box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.15);
    }
    .input-with-button {
      display: flex;
      gap: 6px;
    }
    .input-with-button input { flex: 1; }

    /* MINI MAPA NO MODAL */
    #modalMiniMap {
      width: 100%;
      height: 240px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      margin-top: 8px;
    }

    /* MAPA PRINCIPAL LEAFLET */
    #mapContainer {
      width: 100%;
      height: calc(100vh - 270px);
      min-height: 520px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
    }

    .hub-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
    }
    .hub-card {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 18px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .hub-card-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
    }
    .hub-card-head h3 {
      font-size: 15px;
      font-weight: 700;
      color: var(--navy-900);
    }
    .hub-addr {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }
    .hub-desc {
      font-size: 12px;
      color: var(--gray-700);
      line-height: 1.4;
      background: var(--surface-subtle);
      padding: 8px 10px;
      border-radius: var(--radius-sm);
    }
    .hub-orgaos-box {
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      overflow: hidden;
    }
    .hub-orgaos-head {
      background: #f8fafc;
      padding: 6px 10px;
      border-bottom: 1px solid var(--border);
      font-size: 11px;
      font-weight: 700;
      color: var(--gray-600);
      text-transform: uppercase;
    }
    .hub-orgaos-list {
      list-style: none;
      max-height: 140px;
      overflow-y: auto;
    }
    .hub-orgaos-list li {
      padding: 6px 10px;
      border-bottom: 1px solid var(--border);
      font-size: 11px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .hub-orgaos-list li:last-child { border-bottom: none; }

    /* TOAST */
    .toast-msg {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--navy-900);
      color: #ffffff;
      padding: 10px 18px;
      border-radius: var(--radius-md);
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      font-weight: 600;
      z-index: 9999;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s ease;
      pointer-events: none;
    }
    .toast-msg.active {
      transform: translateY(0);
      opacity: 1;
    }

    .view-section { display: none; }
    .view-section.active { display: block; }

    /* Modo Planilha */
    .spreadsheet-input {
      width: 100%;
      border: 1px solid transparent;
      background: transparent;
      padding: 3px 6px;
      font-size: 12px;
      border-radius: 4px;
      font-family: inherit;
      color: inherit;
    }
    .spreadsheet-input:hover {
      border-color: var(--gray-300);
      background: #ffffff;
    }
    .spreadsheet-input:focus {
      border-color: var(--blue-500);
      background: #ffffff;
      outline: none;
      box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.2);
    }
    .spreadsheet-active .data-table td {
      padding: 4px 6px;
    }

    @media (max-width: 1024px) {
      .kpi-row { grid-template-columns: repeat(2, 1fr); }
      .form-row, .form-row-3 { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <!-- CABEÇALHO INSTITUCIONAL -->
  <header class="top-header">
    <div class="header-content">
      <div class="brand-section">
        <div class="brasao-badge">🏛️</div>
        <div class="title-group">
          <h1>Gestão de Endereços e Equipamentos</h1>
          <p>Cadastre, edite, organize e mantenha atualizados os endereços dos equipamentos públicos de Duque de Caxias.</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary btn-sm" onclick="toggleSpreadsheetMode()" id="btnSpreadsheetMode">
          <span>📊</span>
          <span>Modo Planilha</span>
        </button>
        <button class="btn btn-primary btn-sm" onclick="openNewEquipModal()">
          <span>➕</span>
          <span>Novo Equipamento</span>
        </button>
        <button class="btn btn-navy btn-sm" onclick="exportData('equipamentos', 'csv')">
          <span>📥</span>
          <span>Exportar CSV</span>
        </button>
      </div>
    </div>
  </header>

  <!-- BARRA DE NAVEGAÇÃO -->
  <nav class="nav-bar">
    <div class="nav-content">
      <div class="nav-item active" onclick="navigateTab('equipamentos', this)">
        <span>📋</span>
        <span>Equipamentos & Endereços</span>
        <span class="count-pill" id="badgeTotalEquip">__TOTAL_EQUIPS__</span>
      </div>
      <div class="nav-item" onclick="navigateTab('hubs', this)">
        <span>🏛️</span>
        <span>Complexos & Polos (Hubs)</span>
        <span class="count-pill">__TOTAL_HUBS__</span>
      </div>
      <div class="nav-item" onclick="navigateTab('mapa', this)">
        <span>🗺️</span>
        <span>Mapa Georreferenciado</span>
      </div>
      <div class="nav-item" onclick="navigateTab('relatorios', this)">
        <span>📊</span>
        <span>Relatórios & Dados</span>
      </div>
      <div class="nav-item" onclick="navigateTab('config', this)">
        <span>⚙️</span>
        <span>Configurações</span>
      </div>
    </div>
  </nav>

  <!-- CORPO PRINCIPAL -->
  <main class="main-body">

    <!-- ABA 1: TABELA DE EQUIPAMENTOS & ENDEREÇOS -->
    <section id="viewEquipamentos" class="view-section active">

      <!-- CARDS KPI DE GESTÃO -->
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-blue">🏢</div>
          <div class="kpi-meta">
            <span class="kpi-value" id="kpiTotal">__TOTAL_EQUIPS__</span>
            <span class="kpi-label">Total de Equipamentos</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-green">🟢</div>
          <div class="kpi-meta">
            <span class="kpi-value" id="kpiAtivos">0</span>
            <span class="kpi-label">Endereços Ativos</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-amber">🟡</div>
          <div class="kpi-meta">
            <span class="kpi-value" id="kpiPendentes">0</span>
            <span class="kpi-label">Pendentes de Revisão</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-red">🔴</div>
          <div class="kpi-meta">
            <span class="kpi-value" id="kpiDesatualizados">0</span>
            <span class="kpi-label">Desatualizados / Incompletos</span>
          </div>
        </div>
      </div>

      <!-- BARRA DE PESQUISA E FILTROS -->
      <div class="toolbar-box">
        <div class="search-filter-group">
          <div class="search-input-wrap">
            <span>🔍</span>
            <input type="text" id="searchEquip" class="search-input" placeholder="Buscar por nome, logradouro, bairro, CEP, telefone ou órgão..." oninput="onSearchInput()">
          </div>

          <select id="filterDistrito" class="filter-select" onchange="onFilterChange()">
            <option value="">Todos os Distritos</option>
            <option value="1">1º Distrito (Centro / Caxias)</option>
            <option value="2">2º Distrito (Campos Elíseos)</option>
            <option value="3">3º Distrito (Imbariê)</option>
            <option value="4">4º Distrito (Xerém)</option>
          </select>

          <select id="filterCategoria" class="filter-select" onchange="onFilterChange()">
            <option value="">Todas as Categorias</option>
            <option value="Educação">Educação (SMEDC)</option>
            <option value="Saúde">Saúde (SMS)</option>
            <option value="Assistência">Assistência Social (SEASDIH)</option>
            <option value="Segurança">Segurança Pública (SMSP)</option>
            <option value="Administração">Administração / Governo</option>
            <option value="FUNDEC">FUNDEC / Cursos</option>
          </select>

          <select id="filterStatus" class="filter-select" onchange="onFilterChange()">
            <option value="">Todos os Status</option>
            <option value="Ativo">🟢 Ativo</option>
            <option value="Pendente de revisão">🟡 Pendente de revisão</option>
            <option value="Desatualizado">🔴 Desatualizado</option>
          </select>
        </div>

        <div style="display: flex; gap: 8px;">
          <button class="btn btn-secondary btn-sm" onclick="clearFilters()">Limpar Filtros</button>
        </div>
      </div>

      <!-- TABELA DE DADOS -->
      <div class="table-container" id="tableContainer">
        <div class="table-responsive">
          <table class="data-table" id="equipTable">
            <thead>
              <tr>
                <th style="width: 40px;">#</th>
                <th style="min-width: 200px;">Nome do Equipamento</th>
                <th style="width: 140px;">Categoria</th>
                <th style="width: 90px;">Distrito</th>
                <th style="width: 130px;">Bairro</th>
                <th style="min-width: 240px;">Endereço Oficial</th>
                <th style="width: 100px;">CEP</th>
                <th style="width: 130px;">Telefone</th>
                <th style="width: 110px;">Status</th>
                <th style="width: 130px; text-align: right;">Ações</th>
              </tr>
            </thead>
            <tbody id="equipTableBody">
              <!-- Renderizado via JavaScript -->
            </tbody>
          </table>
        </div>

        <!-- BARRA DE PAGINAÇÃO -->
        <div class="pagination-bar">
          <div id="paginationInfo">Mostrando 1–25 de __TOTAL_EQUIPS__ endereços cadastrados</div>
          <div class="pagination-pages" id="paginationButtons">
            <!-- Botões gerados via JS -->
          </div>
        </div>
      </div>

    </section>

    <!-- ABA 2: HUBS / POLOS INTEGRADOS -->
    <section id="viewHubs" class="view-section">
      <div class="toolbar-box">
        <div>
          <h2 style="font-size: 16px; font-weight: 800; color: var(--navy-900);">Complexos & Polos Governamentais Integrados</h2>
          <p style="font-size: 12px; color: var(--text-muted);">Edifícios sede e polos municipais que abrigam múltiplos órgãos e secretarias no mesmo endereço.</p>
        </div>
        <button class="btn btn-primary btn-sm" onclick="openNewHubModal()">
          <span>➕</span>
          <span>Novo Complexo</span>
        </button>
      </div>

      <div class="hub-grid" id="hubsContainer">
        <!-- Populado via JS -->
      </div>
    </section>

    <!-- ABA 3: MAPA DIGITAL GEORREFERENCIADO -->
    <section id="viewMapa" class="view-section">
      <!-- BARRA DE CONTROLE DE CAMADAS DO MAPA -->
      <div class="toolbar-box" style="margin-bottom: 12px;">
        <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center;">
          <span style="font-size: 12px; font-weight: 800; color: var(--navy-900); text-transform: uppercase;">Camadas no Mapa:</span>
          
          <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; cursor: pointer; user-select: none;">
            <input type="checkbox" id="layerToggleHubs" checked onchange="updateMapLayers()">
            <span>🏛️ Complexos / Polos (12 Hubs)</span>
          </label>

          <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; cursor: pointer; user-select: none;">
            <input type="checkbox" id="layerToggleEquips" checked onchange="updateMapLayers()">
            <span>📍 Equipamentos Públicos (442 pontos)</span>
          </label>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
          <select id="mapFilterDistrito" class="filter-select" onchange="updateMapLayers()" style="padding: 6px 10px; font-size: 12px;">
            <option value="">Todos os Distritos</option>
            <option value="1">1º Distrito (Centro)</option>
            <option value="2">2º Distrito (Campos Elíseos)</option>
            <option value="3">3º Distrito (Imbariê)</option>
            <option value="4">4º Distrito (Xerém)</option>
          </select>

          <select id="mapFilterCategoria" class="filter-select" onchange="updateMapLayers()" style="padding: 6px 10px; font-size: 12px;">
            <option value="">Todas as Categorias</option>
            <option value="Saúde">Saúde</option>
            <option value="Educação">Educação</option>
            <option value="Assistência">Assistência Social</option>
            <option value="Segurança">Segurança Pública</option>
          </select>

          <button class="btn btn-secondary btn-sm" onclick="fitAllMap()">
            <span>🎯</span>
            <span>Enquadrar Duque de Caxias</span>
          </button>
        </div>
      </div>

      <div id="mapContainer"></div>
    </section>

    <!-- ABA 4: RELATÓRIOS & EXPORTAÇÕES -->
    <section id="viewRelatorios" class="view-section">
      <div class="hub-card" style="padding: 24px;">
        <h2 style="font-size: 18px; font-weight: 800; color: var(--navy-900); margin-bottom: 4px;">Relatórios Oficiais e Exportação de Dados</h2>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">Exporte o banco de endereços consolidado em formatos abertos para auditoria ou integração SIG.</p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
          <div style="padding: 16px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
            <h3 style="font-size: 14px; font-weight: 700; color: var(--navy-900);">📦 Base Completa (JSON)</h3>
            <p style="font-size: 12px; color: var(--text-muted); margin: 6px 0 12px 0;">Todos os 442 equipamentos com coordenadas exatas, distritos, bairros, telefones e vínculos.</p>
            <button class="btn btn-primary btn-sm" onclick="exportData('equipamentos', 'json')">Baixar JSON Oficial</button>
          </div>

          <div style="padding: 16px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
            <h3 style="font-size: 14px; font-weight: 700; color: var(--navy-900);">📊 Planilha Tabulada (CSV)</h3>
            <p style="font-size: 12px; color: var(--text-muted); margin: 6px 0 12px 0;">Compatível com Microsoft Excel, LibreOffice Calc e Google Sheets (delimitador ';').</p>
            <button class="btn btn-navy btn-sm" onclick="exportData('equipamentos', 'csv')">Baixar Planilha CSV</button>
          </div>

          <div style="padding: 16px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
            <h3 style="font-size: 14px; font-weight: 700; color: var(--navy-900);">🏛️ Catálogo de Complexos (Hubs)</h3>
            <p style="font-size: 12px; color: var(--text-muted); margin: 6px 0 12px 0;">Mapeamento dos 12 edifícios governamentais compartilhados e seus órgãos instalados.</p>
            <button class="btn btn-secondary btn-sm" onclick="exportHubsData('csv')">Exportar Hubs CSV</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ABA 5: CONFIGURAÇÕES -->
    <section id="viewConfig" class="view-section">
      <div class="hub-card" style="padding: 24px;">
        <h2 style="font-size: 18px; font-weight: 800; color: var(--navy-900); margin-bottom: 4px;">Configurações do Sistema & Persistência Local</h2>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">Gerencie o banco de dados em cache no navegador e opções de restauração dos dados oficiais.</p>

        <div style="display: flex; flex-direction: column; gap: 14px; max-width: 600px;">
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface-subtle);">
            <div>
              <strong style="font-size: 13px; color: var(--navy-900);">Persistência no Navegador (LocalStorage)</strong>
              <p style="font-size: 11px; color: var(--text-muted);">Suas alterações e cadastros são salvos automaticamente no navegador.</p>
            </div>
            <span class="badge-status badge-status-ativo">Ativo</span>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface-subtle);">
            <div>
              <strong style="font-size: 13px; color: var(--navy-900);">Restaurar Base Oficial Original</strong>
              <p style="font-size: 11px; color: var(--text-muted);">Limpa as edições locais e recarrega os dados calibrados oficiais de Duque de Caxias.</p>
            </div>
            <button class="btn btn-danger-outline btn-sm" onclick="resetEquipToDefault()">Restaurar Dados</button>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- ========================================================================= -->
  <!-- MODAL DE CADASTRO / EDIÇÃO TOTAL DE EQUIPAMENTO & ENDEREÇO -->
  <!-- ========================================================================= -->
  <div class="modal-backdrop" id="modalEquip">
    <div class="modal-box">
      <div class="modal-head">
        <div>
          <h3 id="modalEquipTitle">Editar Tudo — Equipamento & Endereço</h3>
          <p id="modalEquipSubtitle">Preencha os dados e utilize o mapa interativo para calibrar a localização exata.</p>
        </div>
        <button class="modal-close" onclick="closeEquipModal()">&times;</button>
      </div>

      <div class="modal-body">
        <input type="hidden" id="editEquipId">

        <!-- SEÇÃO 1: DADOS INSTITUCIONAIS -->
        <div class="form-section">
          <div class="form-section-title">
            <span>🏛️</span>
            <span>1. Identificação Institucional</span>
          </div>

          <div class="form-row">
            <div class="form-ctrl">
              <label>Nome Oficial do Equipamento <span class="req">*</span></label>
              <input type="text" id="editEquipNome" placeholder="Ex: Hospital Municipal Dr. Moacyr Rodrigues do Carmo">
            </div>

            <div class="form-ctrl">
              <label>Sigla / Nome Abreviado</label>
              <input type="text" id="editEquipSigla" placeholder="Ex: HMMRC">
            </div>
          </div>

          <div class="form-row-3">
            <div class="form-ctrl">
              <label>Categoria Oficial <span class="req">*</span></label>
              <select id="editEquipCat">
                <option value="Saúde (SMS)">Saúde (SMS)</option>
                <option value="Educação (SMEDC)">Educação (SMEDC)</option>
                <option value="Assistência Social (SEASDIH)">Assistência Social (SEASDIH)</option>
                <option value="Segurança Pública (SMSP)">Segurança Pública (SMSP)</option>
                <option value="Administração / Fazenda">Administração / Fazenda</option>
                <option value="FUNDEC">FUNDEC / Cursos Profissionalizantes</option>
                <option value="Cultura e Turismo">Cultura e Turismo</option>
                <option value="Serviços Públicos e Obras">Serviços Públicos e Obras</option>
              </select>
            </div>

            <div class="form-ctrl">
              <label>Secretaria Responsável</label>
              <input type="text" id="editEquipSecResp" placeholder="Ex: Secretaria Municipal de Saúde">
            </div>

            <div class="form-ctrl">
              <label>Status Cadastral <span class="req">*</span></label>
              <select id="editEquipStatus">
                <option value="Ativo">🟢 Ativo</option>
                <option value="Pendente de revisão">🟡 Pendente de revisão</option>
                <option value="Desatualizado">🔴 Desatualizado</option>
              </select>
            </div>
          </div>
        </div>

        <!-- SEÇÃO 2: ENDEREÇO & VIA CEP -->
        <div class="form-section">
          <div class="form-section-title">
            <span>📍</span>
            <span>2. Endereço Completo & Localização Postal</span>
          </div>

          <div class="form-row-3">
            <div class="form-ctrl">
              <label>CEP (8 dígitos) <span class="req">*</span></label>
              <div class="input-with-button">
                <input type="text" id="editEquipCep" placeholder="25000-000" maxlength="9">
                <button type="button" class="btn btn-secondary btn-xs" onclick="buscarCepModal()" title="Preencher automaticamente via ViaCEP">🔍 Buscar</button>
              </div>
            </div>

            <div class="form-ctrl">
              <label>Distrito <span class="req">*</span></label>
              <select id="editEquipDist">
                <option value="1">1º Distrito (Centro / Caxias)</option>
                <option value="2">2º Distrito (Campos Elíseos)</option>
                <option value="3">3º Distrito (Imbariê)</option>
                <option value="4">4º Distrito (Xerém)</option>
              </select>
            </div>

            <div class="form-ctrl">
              <label>Bairro Oficial <span class="req">*</span></label>
              <input type="text" id="editEquipBairro" list="listBairrosModal" placeholder="Ex: 25 de Agosto">
              <datalist id="listBairrosModal">
__BAIRROS_OPTIONS__
              </datalist>
            </div>
          </div>

          <div class="form-row" style="grid-template-columns: 2fr 1fr;">
            <div class="form-ctrl">
              <label>Logradouro Oficial (Rua / Av / Praça) <span class="req">*</span></label>
              <input type="text" id="editEquipLogradouro" placeholder="Ex: Avenida Brigadeiro Lima e Silva">
            </div>

            <div class="form-ctrl">
              <label>Número do Imóvel <span class="req">*</span></label>
              <input type="text" id="editEquipNumero" placeholder="Ex: 131 ou s/nº">
            </div>
          </div>

          <div class="form-row">
            <div class="form-ctrl">
              <label>Complemento / Pavimento / Bloco</label>
              <input type="text" id="editEquipPredioSala" placeholder="Ex: Bloco A, Sala 204">
            </div>

            <div class="form-ctrl">
              <label>Ponto de Referência</label>
              <input type="text" id="editEquipRef" placeholder="Ex: Próximo à Praça do Pacificador">
            </div>
          </div>

          <div class="form-ctrl">
            <label>Prédio Compartilhado (Hub / Complexo Vinculado)</label>
            <select id="editEquipHubSelect">
              <!-- Populado via JS -->
            </select>
          </div>
        </div>

        <!-- SEÇÃO 3: LOCALIZAÇÃO NO MAPA & GEOCODIFICAÇÃO (FLUXO PERFEITO) -->
        <div class="form-section">
          <div class="form-section-title">
            <span>🗺️</span>
            <span>3. Localização no Mapa (Geoprocessamento SIG)</span>
          </div>

          <!-- Guia do Fluxo -->
          <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #1e40af; line-height: 1.4; margin-bottom: 10px;">
            <strong>Fluxo de Geocodificação:</strong> Após preencher o CEP e o Número do imóvel, clique em <strong>Obter Coordenadas Exatas</strong>. Se a geocodificação necessitar de ajuste fino, use <strong>[ Ajustar localização manualmente ]</strong> ou arraste o marcador diretamente no mapa.
          </div>

          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 8px;">
            <button type="button" class="btn btn-primary btn-sm" onclick="geolocalizarEnderecoCompletoModal()" id="btnGeocodeModal">
              <span>📍</span>
              <span>Obter Coordenadas Exatas (Geocodificar)</span>
            </button>
            <button type="button" class="btn btn-outline-primary btn-sm" onclick="ativarAjusteManualModal()" id="btnAjusteManualModal">
              <span>✋</span>
              <span>Ajustar localização manualmente</span>
            </button>
            <span id="geocodeStatusBadge" style="font-size: 11px; padding: 3px 8px; border-radius: 4px; display: none;"></span>
          </div>

          <!-- Mini Mapa com Pin Arrastável -->
          <div style="position: relative;">
            <div id="modalMiniMap"></div>
            <div id="manualAdjustmentBanner" style="display: none; position: absolute; top: 8px; left: 8px; right: 8px; z-index: 1000; background: rgba(15, 23, 42, 0.92); color: #ffffff; padding: 8px 14px; border-radius: 6px; font-size: 11px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.35);">
              📍 <strong>Modo de Ajuste Manual Ativo:</strong> Clique em qualquer ponto da rua ou arraste o marcador para a posição exata da fachada do imóvel.
            </div>
          </div>

          <div class="form-row" style="margin-top: 10px;">
            <div class="form-ctrl">
              <label>Latitude (GPS)</label>
              <input type="text" id="editEquipLat" placeholder="-22.785000" style="font-family: monospace;">
            </div>
            <div class="form-ctrl">
              <label>Longitude (GPS)</label>
              <input type="text" id="editEquipLon" placeholder="-43.305000" style="font-family: monospace;">
            </div>
          </div>
        </div>

        <!-- SEÇÃO 4: CONTATO & COMUNICAÇÃO -->
        <div class="form-section">
          <div class="form-section-title">
            <span>📞</span>
            <span>4. Canais de Atendimento & Contato</span>
          </div>

          <div class="form-row-3">
            <div class="form-ctrl">
              <label>Telefone Principal</label>
              <input type="text" id="editEquipTel" placeholder="(21) 2773-5500">
            </div>

            <div class="form-ctrl">
              <label>Telefone Secundário / Ramal</label>
              <input type="text" id="editEquipTelSec" placeholder="(21) 2672-8889">
            </div>

            <div class="form-ctrl">
              <label>WhatsApp Oficial</label>
              <input type="text" id="editEquipWhats" placeholder="(21) 99999-9999">
            </div>
          </div>

          <div class="form-row">
            <div class="form-ctrl">
              <label>E-mail Oficial</label>
              <input type="email" id="editEquipEmail" placeholder="contato@duquedecaxias.rj.gov.br">
            </div>

            <div class="form-ctrl">
              <label>Horário de Funcionamento</label>
              <input type="text" id="editEquipHorario" placeholder="Segunda a sexta, das 09h às 17h">
            </div>
          </div>
        </div>

        <!-- SEÇÃO 5: OBSERVAÇÕES -->
        <div class="form-section">
          <div class="form-section-title">
            <span>📝</span>
            <span>5. Descrição de Atividades & Observações</span>
          </div>

          <div class="form-ctrl">
            <label>Descrição dos Serviços Prestados</label>
            <textarea id="editEquipDesc" rows="3" placeholder="Descreva as atribuições, exames, atendimentos ou serviços deste equipamento..."></textarea>
          </div>
        </div>

      </div>

      <div class="modal-foot">
        <div>
          <button type="button" class="btn btn-danger-outline btn-sm" id="btnModalDeleteEquip" onclick="deleteCurrentModalEquip()" style="display: none;">🗑️ Excluir Registro</button>
        </div>
        <div style="display: flex; gap: 8px;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="closeEquipModal()">Cancelar</button>
          <button type="button" class="btn btn-primary btn-sm" onclick="saveEquipModal()">💾 Salvar Alterações</button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL DE VISUALIZAÇÃO (FICHA CADASTRAL COMPLETA) -->
  <div class="modal-backdrop" id="modalViewEquip">
    <div class="modal-box" style="max-width: 680px;">
      <div class="modal-head">
        <div>
          <h3 id="viewModalNome">Detalhes do Endereço</h3>
          <p id="viewModalCat">Ficha Cadastral do Equipamento Público</p>
        </div>
        <button class="modal-close" onclick="closeViewModal()">&times;</button>
      </div>

      <div class="modal-body" id="viewModalBody" style="font-size: 13px; line-height: 1.5;">
        <!-- Preenchido via JS -->
      </div>

      <div class="modal-foot">
        <button type="button" class="btn btn-secondary btn-sm" onclick="closeViewModal()">Fechar</button>
        <div style="display: flex; gap: 8px;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="abrirRotaGmaps()">🗺️ Abrir no Google Maps</button>
          <button type="button" class="btn btn-primary btn-sm" onclick="abrirEdicaoDeVisualizacao()">✏️ Editar Este Endereço</button>
        </div>
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION -->
  <div class="toast-msg" id="toastMsg">
    <span>✅</span>
    <span id="toastText">Operação realizada com sucesso!</span>
  </div>

  <!-- DADOS E SCRIPTS -->
  <script>
    const DEFAULT_EQUIP = __DEFAULT_EQUIP__;
    const DEFAULT_HUBS = __DEFAULT_HUBS__;
    const PMDC_DB_VERSION = '2026_v5_coordenadas_calibradas_caxias';
    const BAIRROS_COORDENADAS = __BAIRROS_JS__;

    let equipData = [];
    let hubsData = [];
    let filteredEquipList = [];
    let currentPage = 1;
    const itemsPerPage = 25;
    let isSpreadsheetMode = false;
    let currentViewingEquipId = null;

    // Leaflet Maps
    let map = null;
    let hubsMapLayer = null;
    let equipsMapLayer = null;
    let modalMap = null;
    let modalMarker = null;

    // INICIALIZAÇÃO DE DADOS
    function initDatabase() {
      const stored = localStorage.getItem('pmdc_equipamentos_db');
      const storedVer = localStorage.getItem('pmdc_db_version');

      if (stored && storedVer === PMDC_DB_VERSION) {
        try {
          equipData = JSON.parse(stored);
        } catch (e) {
          equipData = JSON.parse(JSON.stringify(DEFAULT_EQUIP));
        }
      } else {
        equipData = JSON.parse(JSON.stringify(DEFAULT_EQUIP));
        localStorage.setItem('pmdc_equipamentos_db', JSON.stringify(equipData));
        localStorage.setItem('pmdc_db_version', PMDC_DB_VERSION);
      }

      hubsData = JSON.parse(JSON.stringify(DEFAULT_HUBS));
      filteredEquipList = equipData;
      updateKPIs();
    }

    function updateKPIs() {
      let ativos = 0;
      let pendentes = 0;
      let desat = 0;

      equipData.forEach(e => {
        const s = e.status || 'Ativo';
        if (s === 'Ativo') ativos++;
        else if (s === 'Pendente de revisão') pendentes++;
        else desat++;
      });

      document.getElementById('kpiTotal').innerText = equipData.length;
      document.getElementById('kpiAtivos').innerText = ativos;
      document.getElementById('kpiPendentes').innerText = pendentes;
      document.getElementById('kpiDesatualizados').innerText = desat;
      document.getElementById('badgeTotalEquip').innerText = equipData.length;
    }

    function saveToStorage() {
      localStorage.setItem('pmdc_equipamentos_db', JSON.stringify(equipData));
      updateKPIs();
    }

    function resetEquipToDefault() {
      if (confirm('Deseja restaurar todos os equipamentos para os dados oficiais originais calibrados?')) {
        localStorage.removeItem('pmdc_equipamentos_db');
        localStorage.setItem('pmdc_db_version', PMDC_DB_VERSION);
        equipData = JSON.parse(JSON.stringify(DEFAULT_EQUIP));
        filteredEquipList = equipData;
        saveToStorage();
        renderEquipTable();
        if (map) updateMapLayers();
        showToast('Base de endereços restaurada com sucesso!');
      }
    }

    // =========================================================================
    // NAVEGAÇÃO ENTRE ABAS
    // =========================================================================
    function navigateTab(tabKey, navElem) {
      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
      if (navElem) navElem.classList.add('active');

      document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
      
      if (tabKey === 'equipamentos') {
        document.getElementById('viewEquipamentos').classList.add('active');
      } else if (tabKey === 'hubs') {
        document.getElementById('viewHubs').classList.add('active');
        renderHubsCards();
      } else if (tabKey === 'mapa') {
        document.getElementById('viewMapa').classList.add('active');
        initMap();
        setTimeout(() => { if (map) map.invalidateSize(); }, 200);
      } else if (tabKey === 'relatorios') {
        document.getElementById('viewRelatorios').classList.add('active');
      } else if (tabKey === 'config') {
        document.getElementById('viewConfig').classList.add('active');
      }
    }

    // =========================================================================
    // RENDERIZAÇÃO DA TABELA
    // =========================================================================
    function renderEquipTable() {
      const tbody = document.getElementById('equipTableBody');
      tbody.innerHTML = '';

      const totalFiltered = filteredEquipList.length;
      const totalPages = Math.ceil(totalFiltered / itemsPerPage) || 1;
      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;

      const startIndex = (currentPage - 1) * itemsPerPage;
      const endIndex = Math.min(startIndex + itemsPerPage, totalFiltered);
      const pageItems = filteredEquipList.slice(startIndex, endIndex);

      if (pageItems.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 32px; color: var(--text-muted);">Nenhum equipamento encontrado para os filtros selecionados.</td></tr>`;
        renderPaginationControls(0, 1, 0, 0);
        return;
      }

      pageItems.forEach((item, index) => {
        const row = document.createElement('tr');
        const absIndex = startIndex + index + 1;
        const itemStatus = item.status || 'Ativo';

        let statusClass = 'badge-status-ativo';
        let statusIcon = '🟢';
        if (itemStatus === 'Pendente de revisão') {
          statusClass = 'badge-status-pendente';
          statusIcon = '🟡';
        } else if (itemStatus === 'Desatualizado') {
          statusClass = 'badge-status-desatualizado';
          statusIcon = '🔴';
        }

        if (!isSpreadsheetMode) {
          row.innerHTML = `
            <td style="color: var(--text-light); font-weight: 600; font-size: 11px;">${absIndex}</td>
            <td>
              <div class="cell-editable" onclick="openEditEquipModal('${item.id}')">
                <strong style="color: var(--navy-900); font-weight: 700;">${item.nome}</strong>
                ${item.sigla ? `<span style="font-size: 11px; color: var(--text-muted); margin-left: 4px;">(${item.sigla})</span>` : ''}
                ${item.hub_nome ? `<br><span class="badge-hub" onclick="event.stopPropagation(); filterByHub('${item.hub_nome}')">🏢 ${item.hub_nome}</span>` : ''}
              </div>
            </td>
            <td><span class="badge-cat">${item.categoria || '-'}</span></td>
            <td><span class="badge-distrito" onclick="quickToggleDistrito('${item.id}', event)" title="Clique para alternar distrito">${item.distrito || '1'}º Dist.</span></td>
            <td><div class="cell-editable" onclick="quickEditField('${item.id}', 'bairro', event)">${item.bairro || '-'}</div></td>
            <td>
              <div class="cell-editable" onclick="quickEditField('${item.id}', 'endereco', event)">
                ${item.endereco || '-'}
                ${item.numero ? `, ${item.numero}` : ''}
                ${item.predio_sala ? `<span style="color: var(--text-muted); font-size: 11px;"> (${item.predio_sala})</span>` : ''}
              </div>
            </td>
            <td><div class="cell-editable" onclick="quickEditField('${item.id}', 'cep', event)" style="font-family: monospace; font-size: 12px;">${item.cep || '-'}</div></td>
            <td><div class="cell-editable" onclick="quickEditField('${item.id}', 'telefone', event)">${item.telefone || '-'}</div></td>
            <td>
              <span class="badge-status ${statusClass}" onclick="quickToggleStatus('${item.id}', event)" title="Clique para alternar status">
                ${statusIcon} ${itemStatus}
              </span>
            </td>
            <td style="text-align: right;">
              <div class="action-cell" style="justify-content: flex-end;">
                <button class="btn btn-secondary btn-xs" onclick="openViewModal('${item.id}')" title="Ver Ficha Cadastral">👁 Ver</button>
                <button class="btn btn-primary btn-xs" onclick="openEditEquipModal('${item.id}')" title="Editar Tudo">✏️ Editar</button>
                <div class="action-dropdown" id="dropdown_${item.id}">
                  <button class="btn btn-secondary btn-xs" onclick="toggleActionDropdown('${item.id}')">⋮</button>
                  <div class="action-dropdown-menu">
                    <div class="action-dropdown-item" onclick="focusEquipOnMap(${item.lat || -22.785}, ${item.lon || -43.305}, '${escapeStr(item.nome)}')">🗺️ Ver no Mapa</div>
                    <div class="action-dropdown-item" onclick="openEditEquipModal('${item.id}')">✏️ Alterar Endereço</div>
                    <div class="action-dropdown-item" onclick="quickToggleStatus('${item.id}')">🔄 Alternar Status</div>
                    <div class="action-dropdown-item" style="color: var(--red-600);" onclick="deleteEquip('${item.id}')">🗑️ Excluir</div>
                  </div>
                </div>
              </div>
            </td>
          `;
        } else {
          // Modo Planilha
          row.innerHTML = `
            <td style="color: var(--text-light); font-size: 11px;">${absIndex}</td>
            <td><input class="spreadsheet-input" style="font-weight: 700;" value="${escapeStr(item.nome)}" onchange="onSpreadsheetChange('${item.id}', 'nome', this.value)"></td>
            <td>
              <select class="spreadsheet-input" onchange="onSpreadsheetChange('${item.id}', 'categoria', this.value)">
                <option value="Saúde (SMS)" ${item.categoria === 'Saúde (SMS)' ? 'selected' : ''}>Saúde (SMS)</option>
                <option value="Educação (SMEDC)" ${item.categoria === 'Educação (SMEDC)' ? 'selected' : ''}>Educação (SMEDC)</option>
                <option value="Assistência Social (SEASDIH)" ${item.categoria === 'Assistência Social (SEASDIH)' ? 'selected' : ''}>Assistência Social</option>
                <option value="Segurança Pública (SMSP)" ${item.categoria === 'Segurança Pública (SMSP)' ? 'selected' : ''}>Segurança Pública</option>
                <option value="Administração / Fazenda" ${item.categoria === 'Administração / Fazenda' ? 'selected' : ''}>Administração</option>
                <option value="FUNDEC" ${item.categoria === 'FUNDEC' ? 'selected' : ''}>FUNDEC</option>
              </select>
            </td>
            <td>
              <select class="spreadsheet-input" onchange="onSpreadsheetChange('${item.id}', 'distrito', this.value)">
                <option value="1" ${item.distrito === '1' ? 'selected' : ''}>1º Dist.</option>
                <option value="2" ${item.distrito === '2' ? 'selected' : ''}>2º Dist.</option>
                <option value="3" ${item.distrito === '3' ? 'selected' : ''}>3º Dist.</option>
                <option value="4" ${item.distrito === '4' ? 'selected' : ''}>4º Dist.</option>
              </select>
            </td>
            <td><input class="spreadsheet-input" value="${escapeStr(item.bairro)}" onchange="onSpreadsheetChange('${item.id}', 'bairro', this.value)"></td>
            <td><input class="spreadsheet-input" value="${escapeStr(item.endereco)}" onchange="onSpreadsheetChange('${item.id}', 'endereco', this.value)"></td>
            <td><input class="spreadsheet-input" value="${escapeStr(item.cep)}" onchange="onSpreadsheetChange('${item.id}', 'cep', this.value)"></td>
            <td><input class="spreadsheet-input" value="${escapeStr(item.telefone)}" onchange="onSpreadsheetChange('${item.id}', 'telefone', this.value)"></td>
            <td>
              <select class="spreadsheet-input" onchange="onSpreadsheetChange('${item.id}', 'status', this.value)">
                <option value="Ativo" ${itemStatus === 'Ativo' ? 'selected' : ''}>🟢 Ativo</option>
                <option value="Pendente de revisão" ${itemStatus === 'Pendente de revisão' ? 'selected' : ''}>🟡 Pendente</option>
                <option value="Desatualizado" ${itemStatus === 'Desatualizado' ? 'selected' : ''}>🔴 Desatualizado</option>
              </select>
            </td>
            <td style="text-align: right;">
              <button class="btn btn-primary btn-xs" onclick="openEditEquipModal('${item.id}')">✏️ Tudo</button>
            </td>
          `;
        }

        tbody.appendChild(row);
      });

      renderPaginationControls(totalFiltered, totalPages, startIndex, endIndex);
    }

    function renderPaginationControls(totalFiltered, totalPages, startIndex, endIndex) {
      const info = document.getElementById('paginationInfo');
      if (totalFiltered === 0) {
        info.innerHTML = 'Nenhum registro encontrado';
      } else {
        info.innerHTML = `Mostrando <strong>${startIndex + 1}–${endIndex}</strong> de <strong>${totalFiltered}</strong> endereços cadastrados`;
      }

      const container = document.getElementById('paginationButtons');
      container.innerHTML = '';
      if (totalPages <= 1) return;

      const prevBtn = document.createElement('button');
      prevBtn.className = 'page-btn';
      prevBtn.innerHTML = '‹';
      prevBtn.disabled = currentPage === 1;
      prevBtn.onclick = () => { if (currentPage > 1) { currentPage--; renderEquipTable(); } };
      container.appendChild(prevBtn);

      let maxVisible = 5;
      let startP = Math.max(1, currentPage - 2);
      let endP = Math.min(totalPages, startP + maxVisible - 1);
      if (endP - startP < maxVisible - 1) {
        startP = Math.max(1, endP - maxVisible + 1);
      }

      if (startP > 1) {
        const btn1 = document.createElement('button');
        btn1.className = 'page-btn';
        btn1.innerText = '1';
        btn1.onclick = () => { currentPage = 1; renderEquipTable(); };
        container.appendChild(btn1);
        if (startP > 2) {
          const dots = document.createElement('span');
          dots.innerText = '...';
          dots.style.padding = '4px';
          container.appendChild(dots);
        }
      }

      for (let p = startP; p <= endP; p++) {
        const btn = document.createElement('button');
        btn.className = 'page-btn' + (p === currentPage ? ' active' : '');
        btn.innerText = p;
        btn.onclick = () => { currentPage = p; renderEquipTable(); };
        container.appendChild(btn);
      }

      if (endP < totalPages) {
        if (endP < totalPages - 1) {
          const dots = document.createElement('span');
          dots.innerText = '...';
          dots.style.padding = '4px';
          container.appendChild(dots);
        }
        const btnLast = document.createElement('button');
        btnLast.className = 'page-btn';
        btnLast.innerText = totalPages;
        btnLast.onclick = () => { currentPage = totalPages; renderEquipTable(); };
        container.appendChild(btnLast);
      }

      const nextBtn = document.createElement('button');
      nextBtn.className = 'page-btn';
      nextBtn.innerHTML = '›';
      nextBtn.disabled = currentPage === totalPages;
      nextBtn.onclick = () => { if (currentPage < totalPages) { currentPage++; renderEquipTable(); } };
      container.appendChild(nextBtn);
    }

    // =========================================================================
    // FILTROS E BUSCA
    // =========================================================================
    function onSearchInput() {
      applyFilters();
    }

    function onFilterChange() {
      applyFilters();
    }

    function applyFilters() {
      const query = document.getElementById('searchEquip').value.toLowerCase().trim();
      const dist = document.getElementById('filterDistrito').value;
      const cat = document.getElementById('filterCategoria').value;
      const status = document.getElementById('filterStatus').value;

      filteredEquipList = equipData.filter(item => {
        if (dist && String(item.distrito) !== String(dist)) return false;
        if (cat && !item.categoria.includes(cat)) return false;
        if (status && (item.status || 'Ativo') !== status) return false;

        if (query) {
          const searchCorpus = [
            item.nome, item.sigla, item.categoria, item.secretaria_responsavel,
            item.bairro, item.endereco, item.cep, item.telefone, item.hub_nome,
            item.predio_sala, item.numero, item.ponto_referencia
          ].filter(Boolean).join(' ').toLowerCase();

          if (!searchCorpus.includes(query)) return false;
        }
        return true;
      });

      currentPage = 1;
      renderEquipTable();
    }

    function clearFilters() {
      document.getElementById('searchEquip').value = '';
      document.getElementById('filterDistrito').value = '';
      document.getElementById('filterCategoria').value = '';
      document.getElementById('filterStatus').value = '';
      filteredEquipList = equipData;
      currentPage = 1;
      renderEquipTable();
    }

    function toggleSpreadsheetMode() {
      isSpreadsheetMode = !isSpreadsheetMode;
      const btn = document.getElementById('btnSpreadsheetMode');
      const tableWrap = document.getElementById('tableContainer');
      if (isSpreadsheetMode) {
        btn.classList.add('btn-primary');
        btn.classList.remove('btn-secondary');
        tableWrap.classList.add('spreadsheet-active');
        showToast('Modo Planilha Ativado: edite diretamente nas células!');
      } else {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-secondary');
        tableWrap.classList.remove('spreadsheet-active');
        showToast('Modo Tabela Visual Ativado.');
      }
      renderEquipTable();
    }

    function onSpreadsheetChange(id, field, val) {
      const item = equipData.find(x => x.id === id);
      if (!item) return;
      item[field] = val;
      saveToStorage();
      showToast(`Campo "${field}" atualizado.`);
    }

    function quickToggleStatus(id, event) {
      if (event) event.stopPropagation();
      const item = equipData.find(x => x.id === id);
      if (!item) return;
      if (item.status === 'Ativo') item.status = 'Pendente de revisão';
      else if (item.status === 'Pendente de revisão') item.status = 'Desatualizado';
      else item.status = 'Ativo';
      saveToStorage();
      renderEquipTable();
      showToast(`Status alterado para ${item.status}.`);
    }

    function quickToggleDistrito(id, event) {
      if (event) event.stopPropagation();
      const item = equipData.find(x => x.id === id);
      if (!item) return;
      let d = parseInt(item.distrito || '1', 10);
      d = (d % 4) + 1;
      item.distrito = String(d);
      saveToStorage();
      renderEquipTable();
      showToast(`Distrito alterado para ${item.distrito}º Distrito.`);
    }

    function quickEditField(id, field, event) {
      if (event) event.stopPropagation();
      const item = equipData.find(x => x.id === id);
      if (!item) return;
      const current = item[field] || '';
      const promptLabel = field === 'endereco' ? 'Logradouro Oficial' : (field === 'bairro' ? 'Bairro' : (field === 'cep' ? 'CEP' : 'Telefone'));
      const val = prompt(`Editar ${promptLabel}:`, current);
      if (val !== null && val.trim() !== current) {
        item[field] = val.trim();
        saveToStorage();
        renderEquipTable();
        showToast(`${promptLabel} atualizado com sucesso!`);
      }
    }

    function toggleActionDropdown(id) {
      document.querySelectorAll('.action-dropdown.open').forEach(d => {
        if (d.id !== 'dropdown_' + id) d.classList.remove('open');
      });
      const el = document.getElementById('dropdown_' + id);
      if (el) el.classList.toggle('open');
    }

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.action-dropdown')) {
        document.querySelectorAll('.action-dropdown.open').forEach(d => d.classList.remove('open'));
      }
    });

    function escapeStr(str) {
      return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
    }

    // =========================================================================
    // MODAL DE CADASTRO / EDIÇÃO TOTAL
    // =========================================================================
    function openNewEquipModal() {
      document.getElementById('modalEquipTitle').innerText = '➕ Cadastrar Novo Equipamento';
      document.getElementById('modalEquipSubtitle').innerText = 'Insira as informações oficiais do novo endereço público.';
      document.getElementById('btnModalDeleteEquip').style.display = 'none';

      document.getElementById('editEquipId').value = '';
      document.getElementById('editEquipNome').value = '';
      document.getElementById('editEquipSigla').value = '';
      document.getElementById('editEquipCat').value = 'Educação (SMEDC)';
      document.getElementById('editEquipSecResp').value = '';
      document.getElementById('editEquipStatus').value = 'Ativo';

      document.getElementById('editEquipCep').value = '';
      document.getElementById('editEquipDist').value = '1';
      document.getElementById('editEquipBairro').value = '';
      document.getElementById('editEquipLogradouro').value = '';
      document.getElementById('editEquipNumero').value = '';
      document.getElementById('editEquipPredioSala').value = '';
      document.getElementById('editEquipRef').value = '';

      document.getElementById('editEquipTel').value = '';
      document.getElementById('editEquipTelSec').value = '';
      document.getElementById('editEquipWhats').value = '';
      document.getElementById('editEquipEmail').value = '';
      document.getElementById('editEquipHorario').value = 'Segunda a sexta, das 09h às 17h';
      document.getElementById('editEquipDesc').value = '';

      document.getElementById('editEquipLat').value = '-22.785000';
      document.getElementById('editEquipLon').value = '-43.305000';

      populateHubSelect('');
      document.getElementById('modalEquip').classList.add('active');

      setTimeout(() => {
        initOrUpdateModalMiniMap(-22.785000, -43.305000);
      }, 250);
    }

    function openEditEquipModal(id) {
      const item = equipData.find(x => x.id === id);
      if (!item) return;

      document.getElementById('modalEquipTitle').innerText = '✏️ Editar Tudo — Equipamento & Endereço';
      document.getElementById('modalEquipSubtitle').innerText = `ID: ${item.id} • Última revisão registrada`;
      document.getElementById('btnModalDeleteEquip').style.display = 'inline-block';

      document.getElementById('editEquipId').value = item.id;
      document.getElementById('editEquipNome').value = item.nome || '';
      document.getElementById('editEquipSigla').value = item.sigla || '';
      document.getElementById('editEquipCat').value = item.categoria || 'Educação (SMEDC)';
      document.getElementById('editEquipSecResp').value = item.secretaria_responsavel || '';
      document.getElementById('editEquipStatus').value = item.status || 'Ativo';

      document.getElementById('editEquipCep').value = item.cep || '';
      document.getElementById('editEquipDist').value = item.distrito || '1';
      document.getElementById('editEquipBairro').value = item.bairro || '';
      document.getElementById('editEquipLogradouro').value = item.endereco || '';
      document.getElementById('editEquipNumero').value = item.numero || '';
      document.getElementById('editEquipPredioSala').value = item.predio_sala || '';
      document.getElementById('editEquipRef').value = item.ponto_referencia || '';

      document.getElementById('editEquipTel').value = item.telefone || '';
      document.getElementById('editEquipTelSec').value = item.telefone_secundario || '';
      document.getElementById('editEquipWhats').value = item.whatsapp || '';
      document.getElementById('editEquipEmail').value = item.email || '';
      document.getElementById('editEquipHorario').value = item.horario_funcionamento || '';
      document.getElementById('editEquipDesc').value = item.descricao || '';

      const lat = item.lat || -22.785000;
      const lon = item.lon || -43.305000;
      document.getElementById('editEquipLat').value = lat.toFixed(6);
      document.getElementById('editEquipLon').value = lon.toFixed(6);

      populateHubSelect(item.hub_id || '');
      document.getElementById('modalEquip').classList.add('active');

      setTimeout(() => {
        initOrUpdateModalMiniMap(lat, lon);
      }, 250);
    }

    function closeEquipModal() {
      document.getElementById('modalEquip').classList.remove('active');
      document.getElementById('manualAdjustmentBanner').style.display = 'none';
      document.getElementById('geocodeStatusBadge').style.display = 'none';
    }

    function saveEquipModal() {
      const id = document.getElementById('editEquipId').value;
      const nome = document.getElementById('editEquipNome').value.trim();
      const endereco = document.getElementById('editEquipLogradouro').value.trim();
      const bairro = document.getElementById('editEquipBairro').value.trim();

      if (!nome || !endereco || !bairro) {
        alert('Por favor preencha os campos obrigatórios: Nome Oficial, Logradouro e Bairro.');
        return;
      }

      const selectedHubId = document.getElementById('editEquipHubSelect').value;
      let hubNome = '';
      if (selectedHubId) {
        const h = hubsData.find(x => x.id === selectedHubId);
        if (h) hubNome = h.nome;
      }

      const lat = parseFloat(document.getElementById('editEquipLat').value) || -22.785000;
      const lon = parseFloat(document.getElementById('editEquipLon').value) || -43.305000;

      if (id) {
        // Edição
        const item = equipData.find(x => x.id === id);
        if (item) {
          item.nome = nome;
          item.sigla = document.getElementById('editEquipSigla').value.trim();
          item.categoria = document.getElementById('editEquipCat').value;
          item.secretaria_responsavel = document.getElementById('editEquipSecResp').value.trim();
          item.status = document.getElementById('editEquipStatus').value;

          item.cep = document.getElementById('editEquipCep').value.trim();
          item.distrito = document.getElementById('editEquipDist').value;
          item.bairro = bairro;
          item.endereco = endereco;
          item.numero = document.getElementById('editEquipNumero').value.trim();
          item.predio_sala = document.getElementById('editEquipPredioSala').value.trim();
          item.ponto_referencia = document.getElementById('editEquipRef').value.trim();
          item.hub_id = selectedHubId;
          item.hub_nome = hubNome;

          item.telefone = document.getElementById('editEquipTel').value.trim();
          item.telefone_secundario = document.getElementById('editEquipTelSec').value.trim();
          item.whatsapp = document.getElementById('editEquipWhats').value.trim();
          item.email = document.getElementById('editEquipEmail').value.trim();
          item.horario_funcionamento = document.getElementById('editEquipHorario').value.trim();
          item.descricao = document.getElementById('editEquipDesc').value.trim();

          item.lat = lat;
          item.lon = lon;
          showToast(`Equipamento "${nome}" salvo com sucesso!`);
        }
      } else {
        // Novo
        const newId = 'rec_novo_' + Date.now();
        const newItem = {
          id: newId,
          nome: nome,
          sigla: document.getElementById('editEquipSigla').value.trim(),
          categoria: document.getElementById('editEquipCat').value,
          secretaria_responsavel: document.getElementById('editEquipSecResp').value.trim(),
          status: document.getElementById('editEquipStatus').value,
          cep: document.getElementById('editEquipCep').value.trim(),
          distrito: document.getElementById('editEquipDist').value,
          bairro: bairro,
          endereco: endereco,
          numero: document.getElementById('editEquipNumero').value.trim(),
          predio_sala: document.getElementById('editEquipPredioSala').value.trim(),
          ponto_referencia: document.getElementById('editEquipRef').value.trim(),
          hub_id: selectedHubId,
          hub_nome: hubNome,
          telefone: document.getElementById('editEquipTel').value.trim(),
          telefone_secundario: document.getElementById('editEquipTelSec').value.trim(),
          whatsapp: document.getElementById('editEquipWhats').value.trim(),
          email: document.getElementById('editEquipEmail').value.trim(),
          horario_funcionamento: document.getElementById('editEquipHorario').value.trim(),
          descricao: document.getElementById('editEquipDesc').value.trim(),
          lat: lat,
          lon: lon
        };
        equipData.unshift(newItem);
        showToast(`Novo equipamento "${nome}" cadastrado com sucesso!`);
      }

      saveToStorage();
      closeEquipModal();
      applyFilters();
      if (map) updateMapLayers();
    }

    function deleteCurrentModalEquip() {
      const id = document.getElementById('editEquipId').value;
      if (!id) return;
      deleteEquip(id);
      closeEquipModal();
    }

    function deleteEquip(id) {
      const idx = equipData.findIndex(x => x.id === id);
      if (idx === -1) return;
      const nome = equipData[idx].nome;
      if (confirm(`Tem certeza que deseja excluir o cadastro de "${nome}"?`)) {
        equipData.splice(idx, 1);
        saveToStorage();
        applyFilters();
        if (map) updateMapLayers();
        showToast(`Equipamento "${nome}" excluído com sucesso.`);
      }
    }

    // =========================================================================
    // MINI MAPA & FLUXO DE GEOCODIFICAÇÃO (PERFEITO)
    // =========================================================================
    function initOrUpdateModalMiniMap(lat, lon) {
      const container = document.getElementById('modalMiniMap');
      if (!container) return;

      if (!modalMap) {
        modalMap = L.map('modalMiniMap').setView([lat, lon], 15);
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
          attribution: 'Esri &copy; Prefeitura de Duque de Caxias',
          maxZoom: 18
        }).addTo(modalMap);

        modalMarker = L.marker([lat, lon], { draggable: true }).addTo(modalMap);

        modalMarker.on('dragend', function (e) {
          const pos = modalMarker.getLatLng();
          document.getElementById('editEquipLat').value = pos.lat.toFixed(6);
          document.getElementById('editEquipLon').value = pos.lng.toFixed(6);
          showToast(`Coordenada capturada: ${pos.lat.toFixed(5)}, ${pos.lng.toFixed(5)}`);
        });

        modalMap.on('click', function (e) {
          modalMarker.setLatLng(e.latlng);
          document.getElementById('editEquipLat').value = e.latlng.lat.toFixed(6);
          document.getElementById('editEquipLon').value = e.latlng.lng.toFixed(6);
          showToast(`Pin reposicionado: ${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)}`);
        });
      } else {
        modalMap.invalidateSize();
        modalMap.setView([lat, lon], 15);
        modalMarker.setLatLng([lat, lon]);
      }
    }

    function ativarAjusteManualModal() {
      const banner = document.getElementById('manualAdjustmentBanner');
      banner.style.display = 'block';
      if (modalMap && modalMarker) {
        modalMap.setZoom(16);
        modalMarker.dragging.enable();
      }
      showToast('Ajuste manual ativado: clique na rua ou arraste o marcador 📍');
    }

    // 1. VIA CEP: Preenche Logradouro, Bairro, Cidade, Distrito e foca no Número
    function buscarCepModal() {
      let cep = document.getElementById('editEquipCep').value.replace(/\D/g, '');
      if (cep.length !== 8) {
        alert('Digite um CEP válido com 8 dígitos numéricos.');
        return;
      }

      const badge = document.getElementById('geocodeStatusBadge');
      badge.style.display = 'inline-block';
      badge.style.background = '#e0f2fe';
      badge.style.color = '#0284c7';
      badge.innerText = 'Consultando ViaCEP...';

      fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(res => res.json())
        .then(data => {
          if (data.erro) {
            badge.style.background = '#fee2e2';
            badge.style.color = '#dc2626';
            badge.innerText = '❌ CEP não localizado nos Correios.';
            return;
          }

          if (data.logradouro) document.getElementById('editEquipLogradouro').value = data.logradouro;
          if (data.bairro) {
            document.getElementById('editEquipBairro').value = data.bairro;
            // Identificar distrito pelo bairro
            const bNorm = data.bairro.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
            if (BAIRROS_COORDENADAS[bNorm]) {
              document.getElementById('editEquipDist').value = BAIRROS_COORDENADAS[bNorm][2];
            }
          }

          badge.style.background = '#dcfce7';
          badge.style.color = '#15803d';
          badge.innerText = '✅ Endereço preenchido! Agora informe o NÚMERO.';

          // Foca no número do imóvel
          const numInput = document.getElementById('editEquipNumero');
          numInput.focus();
          numInput.style.borderColor = '#0284c7';
          setTimeout(() => { numInput.style.borderColor = ''; }, 2500);

          showToast('ViaCEP: Logradouro e Bairro preenchidos! Informe o Número.');
        })
        .catch(() => {
          badge.style.background = '#fee2e2';
          badge.style.color = '#dc2626';
          badge.innerText = '❌ Erro ao conectar ao ViaCEP.';
        });
    }

    // 2. GEOCODIFICAÇÃO COMPLETA: Logradouro + Número + Bairro + Duque de Caxias + RJ
    function geolocalizarEnderecoCompletoModal() {
      const logradouro = document.getElementById('editEquipLogradouro').value.trim();
      const numero = document.getElementById('editEquipNumero').value.trim();
      const bairro = document.getElementById('editEquipBairro').value.trim();

      if (!logradouro || !bairro) {
        alert('Para geocodificar, preencha ao menos o Logradouro e o Bairro.');
        return;
      }

      const badge = document.getElementById('geocodeStatusBadge');
      badge.style.display = 'inline-block';
      badge.style.background = '#e0f2fe';
      badge.style.color = '#0284c7';
      badge.innerText = 'Buscando coordenadas exatas...';

      let query = `${logradouro}, ${bairro}, Duque de Caxias, RJ, Brasil`;
      if (numero && numero.toLowerCase() !== 's/n' && numero.toLowerCase() !== 'sn') {
        query = `${logradouro}, ${numero}, ${bairro}, Duque de Caxias, RJ, Brasil`;
      }

      // Geocodificação OpenStreetMap / Nominatim restrita aos limites de Duque de Caxias
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&viewbox=-43.34,-22.52,-43.16,-22.82&bounded=1&countrycodes=br&limit=1`;

      fetch(url)
        .then(res => res.json())
        .then(data => {
          if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lon = parseFloat(data[0].lon);

            // Validar se está dentro de Duque de Caxias
            if (lat >= -22.825 && lat <= -22.530 && lon >= -43.330 && lon <= -43.160) {
              document.getElementById('editEquipLat').value = lat.toFixed(6);
              document.getElementById('editEquipLon').value = lon.toFixed(6);

              initOrUpdateModalMiniMap(lat, lon);
              modalMap.setZoom(16);

              badge.style.background = '#dcfce7';
              badge.style.color = '#15803d';
              badge.innerText = '✅ Coordenadas exatas obtidas pelo endereço completo!';
              showToast('Coordenadas georreferenciadas com precisão exata!');
              return;
            }
          }

          // Fallback imediato: Catálogo de Centroides de Alta Precisão dos Bairros de Duque de Caxias
          const bNorm = bairro.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
          let coord = BAIRROS_COORDENADAS[bNorm];

          if (!coord) {
            for (let k in BAIRROS_COORDENADAS) {
              if (k.includes(bNorm) || bNorm.includes(k)) {
                coord = BAIRROS_COORDENADAS[k];
                break;
              }
            }
          }

          if (!coord) {
            const dist = document.getElementById('editEquipDist').value;
            if (dist === '4') coord = [-22.5850, -43.3000];
            else if (dist === '3') coord = [-22.6350, -43.2350];
            else if (dist === '2') coord = [-22.7000, -43.2700];
            else coord = [-22.7850, -43.3050];
          }

          const lat = coord[0];
          const lon = coord[1];
          document.getElementById('editEquipLat').value = lat.toFixed(6);
          document.getElementById('editEquipLon').value = lon.toFixed(6);

          initOrUpdateModalMiniMap(lat, lon);

          badge.style.background = '#fef3c7';
          badge.style.color = '#b45309';
          badge.innerText = '⚠️ Posição aproximada pelo Bairro. Use [Ajustar localização] para afinar.';

          ativarAjusteManualModal();
          showToast('Coordenada baseada no bairro. Ajuste o marcador manualmente se necessário.');
        })
        .catch(() => {
          badge.style.background = '#fee2e2';
          badge.style.color = '#dc2626';
          badge.innerText = '❌ Falha na conexão de geocodificação.';
        });
    }

    function populateHubSelect(selectedId) {
      const sel = document.getElementById('editEquipHubSelect');
      if (!sel) return;
      sel.innerHTML = '<option value="">-- Prédio Próprio / Isolado (Não pertence a Hub) --</option>';
      hubsData.forEach(h => {
        const opt = document.createElement('option');
        opt.value = h.id;
        opt.innerText = `🏢 ${h.nome} (${h.bairro})`;
        if (h.id === selectedId) opt.selected = true;
        sel.appendChild(opt);
      });
    }

    // =========================================================================
    // MODAL DE VISUALIZAÇÃO
    // =========================================================================
    function openViewModal(id) {
      const item = equipData.find(x => x.id === id);
      if (!item) return;
      currentViewingEquipId = item.id;

      document.getElementById('viewModalNome').innerText = item.nome;
      document.getElementById('viewModalCat').innerText = `${item.categoria} • ${item.distrito}º Distrito (${item.bairro})`;

      const itemStatus = item.status || 'Ativo';
      let statusColor = '#10b981';
      if (itemStatus === 'Pendente de revisão') statusColor = '#f59e0b';
      else if (itemStatus === 'Desatualizado') statusColor = '#ef4444';

      let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 14px;">
          <div>
            <strong style="color: var(--navy-900);">Status Cadastral:</strong>
            <span style="color: ${statusColor}; font-weight: 700; margin-left: 6px;">${itemStatus}</span>
          </div>
          <div>
            <strong style="color: var(--navy-900);">Distrito:</strong>
            <span style="margin-left: 6px;">${item.distrito}º Distrito</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
          <div style="background: var(--surface-subtle); padding: 10px 12px; border-radius: 6px; border: 1px solid var(--border);">
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">LOGRADOURO & NÚMERO</div>
            <div style="font-weight: 600; color: var(--navy-900); margin-top: 2px;">📍 ${item.endereco}${item.numero ? ', ' + item.numero : ''}</div>
          </div>
          <div style="background: var(--surface-subtle); padding: 10px 12px; border-radius: 6px; border: 1px solid var(--border);">
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">BAIRRO & CEP</div>
            <div style="font-weight: 600; color: var(--navy-900); margin-top: 2px;">📮 ${item.bairro} | CEP ${item.cep || '-'}</div>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
          <div style="background: var(--surface-subtle); padding: 10px 12px; border-radius: 6px; border: 1px solid var(--border);">
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">TELEFONE OFICIAL</div>
            <div style="font-weight: 600; color: var(--navy-900); margin-top: 2px;">📞 ${item.telefone || 'Não informado'}</div>
          </div>
          <div style="background: var(--surface-subtle); padding: 10px 12px; border-radius: 6px; border: 1px solid var(--border);">
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">E-MAIL INSTITUCIONAL</div>
            <div style="font-weight: 600; color: var(--navy-900); margin-top: 2px;">✉️ ${item.email || 'Não informado'}</div>
          </div>
        </div>

        <div style="background: #f8fafc; padding: 10px 12px; border-radius: 6px; border: 1px solid var(--border); margin-bottom: 12px;">
          <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">COORDENADAS GEOGRÁFICAS (SIG)</div>
          <div style="font-family: monospace; font-size: 12px; color: var(--navy-900); margin-top: 2px;">
            Latitude: <strong>${item.lat ? item.lat.toFixed(6) : '-'}</strong> | Longitude: <strong>${item.lon ? item.lon.toFixed(6) : '-'}</strong>
          </div>
        </div>

        ${item.predio_sala ? `
          <div style="background: #fffbeb; border: 1px solid #fef3c7; padding: 10px 12px; border-radius: 6px; margin-bottom: 12px;">
            <div style="font-size: 11px; color: #b45309; font-weight: 700;">COMPLEMENTO / INEP / CNES</div>
            <div style="font-size: 12px; color: #78350f; margin-top: 2px;">${item.predio_sala}</div>
          </div>
        ` : ''}

        ${item.descricao ? `
          <div style="margin-top: 10px;">
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 700;">DESCRIÇÃO DOS SERVIÇOS</div>
            <div style="font-size: 12px; color: var(--gray-700); margin-top: 4px; line-height: 1.4;">${item.descricao}</div>
          </div>
        ` : ''}
      `;

      document.getElementById('viewModalBody').innerHTML = html;
      document.getElementById('modalViewEquip').classList.add('active');
    }

    function closeViewModal() {
      document.getElementById('modalViewEquip').classList.remove('active');
    }

    function abrirRotaGmaps() {
      if (!currentViewingEquipId) return;
      const item = equipData.find(x => x.id === currentViewingEquipId);
      if (!item) return;
      const q = encodeURIComponent(`${item.nome}, ${item.endereco}, Duque de Caxias - RJ`);
      window.open(`https://www.google.com/maps/search/?api=1&query=${q}`, '_blank');
    }

    function abrirEdicaoDeVisualizacao() {
      if (!currentViewingEquipId) return;
      const id = currentViewingEquipId;
      closeViewModal();
      openEditEquipModal(id);
    }

    // =========================================================================
    // HUBS
    // =========================================================================
    function renderHubsCards() {
      const container = document.getElementById('hubsContainer');
      if (!container) return;
      container.innerHTML = '';

      hubsData.forEach(hub => {
        const card = document.createElement('div');
        card.className = 'hub-card';

        let orgaosListHtml = '';
        if (!hub.orgaos || hub.orgaos.length === 0) {
          orgaosListHtml = '<li style="color: var(--text-light); font-style: italic; font-size: 11px;">Nenhum órgão cadastrado neste complexo.</li>';
        } else {
          hub.orgaos.forEach(org => {
            orgaosListHtml += `
              <li>
                <div>
                  <strong style="color: var(--navy-900);">${org.nome}</strong>
                  <div style="color: var(--text-muted); font-size: 10px;">📍 ${org.andar_sala || 'Pavimento Geral'} ${org.ramal ? '| 📞 ' + org.ramal : ''}</div>
                </div>
              </li>
            `;
          });
        }

        card.innerHTML = `
          <div class="hub-card-head">
            <div>
              <h3>${hub.nome}</h3>
              <div class="hub-addr">📍 ${hub.endereco} — <strong>${hub.bairro}</strong> (${hub.distrito}º Distrito)</div>
            </div>
            <span class="badge-cat" style="background: #fef2f2; color: #dc2626; border-color: #fecaca;">${hub.orgaos ? hub.orgaos.length : 0} Órgãos</span>
          </div>
          <p class="hub-desc">${hub.descricao || 'Complexo administrativo governamental de Duque de Caxias.'}</p>
          <div class="hub-orgaos-box">
            <div class="hub-orgaos-head">🏛️ Órgãos Instalados (${hub.orgaos ? hub.orgaos.length : 0})</div>
            <ul class="hub-orgaos-list">${orgaosListHtml}</ul>
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px;">
            <button class="btn btn-secondary btn-xs" onclick="filterByHub('${escapeStr(hub.nome)}')">🔍 Filtrar na Tabela</button>
            <button class="btn btn-primary btn-xs" onclick="focusHubOnMap(${hub.lat || -22.785}, ${hub.lon || -43.305}, '${escapeStr(hub.nome)}')">🗺️ Ver no Mapa</button>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function filterByHub(hubNome) {
      navigateTab('equipamentos', document.querySelectorAll('.nav-item')[0]);
      document.getElementById('searchEquip').value = hubNome;
      onSearchInput();
    }

    // =========================================================================
    // MAPA PRINCIPAL COM CONTROLE DE CAMADAS
    // =========================================================================
    function initMap() {
      if (map) {
        map.invalidateSize();
        return;
      }

      // Bounding box e Centroide de Duque de Caxias
      map = L.map('mapContainer').setView([-22.7150, -43.2750], 11);

      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Prefeitura de Duque de Caxias',
        maxZoom: 18
      }).addTo(map);

      hubsMapLayer = L.layerGroup().addTo(map);
      equipsMapLayer = L.layerGroup().addTo(map);

      updateMapLayers();
    }

    function updateMapLayers() {
      if (!map) return;

      const showHubs = document.getElementById('layerToggleHubs').checked;
      const showEquips = document.getElementById('layerToggleEquips').checked;
      const filterDist = document.getElementById('mapFilterDistrito').value;
      const filterCat = document.getElementById('mapFilterCategoria').value;

      hubsMapLayer.clearLayers();
      equipsMapLayer.clearLayers();

      // Camada 1: Hubs (Ícones Vermelhos Institucionais)
      if (showHubs) {
        hubsData.forEach(hub => {
          if (hub.lat && hub.lon) {
            if (filterDist && String(hub.distrito) !== String(filterDist)) return;

            const hubIcon = L.divIcon({
              className: 'custom-hub-icon',
              html: `<div style="background: #dc2626; color: white; border: 2px solid white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.35);">🏛️</div>`,
              iconSize: [30, 30],
              iconAnchor: [15, 15]
            });

            const marker = L.marker([hub.lat, hub.lon], { icon: hubIcon });
            let orgaosList = (hub.orgaos || []).map(o => `• <strong>${o.nome}</strong> (${o.andar_sala || ''})`).join('<br>');
            let popupHtml = `
              <div style="font-family: 'Inter', sans-serif; font-size: 12px; max-width: 280px; line-height: 1.4;">
                <strong style="font-size: 13px; color: #b91c1c;">🏢 ${hub.nome}</strong><br>
                📍 ${hub.endereco} — ${hub.bairro}<br>
                <hr style="margin: 6px 0; border: none; border-top: 1px solid #e2e8f0;">
                <strong style="font-size: 11px; color: #1e293b;">Órgãos Instalados (${(hub.orgaos || []).length}):</strong><br>
                ${orgaosList || 'Nenhum órgão listado.'}
              </div>
            `;
            marker.bindPopup(popupHtml);
            hubsMapLayer.addLayer(marker);
          }
        });
      }

      // Camada 2: Equipamentos Públicos (Pontos Coloridos)
      if (showEquips) {
        equipData.forEach(item => {
          if (item.lat && item.lon) {
            if (filterDist && String(item.distrito) !== String(filterDist)) return;
            if (filterCat && !item.categoria.includes(filterCat)) return;

            let color = '#0284c7';
            if (item.categoria.includes('Saúde')) color = '#10b981';
            else if (item.categoria.includes('Educação')) color = '#f59e0b';
            else if (item.categoria.includes('Assistência')) color = '#ec4899';

            const marker = L.circleMarker([item.lat, item.lon], {
              radius: 6,
              fillColor: color,
              color: '#ffffff',
              weight: 1.5,
              opacity: 1,
              fillOpacity: 0.85
            });

            let popupHtml = `
              <div style="font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.4; max-width: 260px;">
                <strong style="font-size: 13px; color: #0f1b2d;">${item.nome}</strong><br>
                <span style="color: #64748b; font-weight: 700;">${item.categoria} (${item.distrito}º Dist.)</span><br>
                📍 ${item.endereco}${item.numero ? ', ' + item.numero : ''} — ${item.bairro}<br>
                📞 ${item.telefone || '-'}<br>
                <div style="margin-top: 8px; display: flex; gap: 6px;">
                  <button style="padding: 3px 8px; font-size: 11px; background: #0284c7; color: white; border: none; border-radius: 4px; cursor: pointer;" onclick="openEditEquipModal('${item.id}')">✏️ Editar</button>
                  <button style="padding: 3px 8px; font-size: 11px; background: #64748b; color: white; border: none; border-radius: 4px; cursor: pointer;" onclick="openViewModal('${item.id}')">👁 Ver Ficha</button>
                </div>
              </div>
            `;
            marker.bindPopup(popupHtml);
            equipsMapLayer.addLayer(marker);
          }
        });
      }
    }

    function focusHubOnMap(lat, lon, nome) {
      navigateTab('mapa', document.querySelectorAll('.nav-item')[2]);
      setTimeout(() => {
        if (map) map.setView([lat, lon], 16);
      }, 300);
    }

    function focusEquipOnMap(lat, lon, nome) {
      navigateTab('mapa', document.querySelectorAll('.nav-item')[2]);
      setTimeout(() => {
        if (map) map.setView([lat, lon], 16);
      }, 300);
    }

    function fitAllMap() {
      if (map) {
        // Limites oficiais de Duque de Caxias
        map.fitBounds([
          [-22.820, -43.325],
          [-22.540, -43.165]
        ]);
      }
    }

    // =========================================================================
    // EXPORTAÇÃO
    // =========================================================================
    function exportData(type, format) {
      const data = filteredEquipList.length > 0 ? filteredEquipList : equipData;
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        downloadBlob(blob, `enderecos_duque_de_caxias_${new Date().toISOString().slice(0,10)}.json`);
      } else if (format === 'csv') {
        let csv = "ID;Nome;Sigla;Categoria;Secretaria;Status;Distrito;Bairro;Endereco;Numero;CEP;Telefone;Email;Horario;Latitude;Longitude;Complexo" + String.fromCharCode(10);
        data.forEach(x => {
          csv += '"' + x.id + '";"' + (x.nome || '') + '";"' + (x.sigla || '') + '";"' + (x.categoria || '') + '";"' + (x.secretaria_responsavel || '') + '";"' + (x.status || 'Ativo') + '";"' + (x.distrito || '') + '";"' + (x.bairro || '') + '";"' + (x.endereco || '') + '";"' + (x.numero || '') + '";"' + (x.cep || '') + '";"' + (x.telefone || '') + '";"' + (x.email || '') + '";"' + (x.horario_funcionamento || '') + '";"' + (x.lat || '') + '";"' + (x.lon || '') + '";"' + (x.hub_nome || '') + '"' + String.fromCharCode(10);
        });
        const blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8;' });
        downloadBlob(blob, `enderecos_duque_de_caxias_${new Date().toISOString().slice(0,10)}.csv`);
      }
    }

    function exportHubsData(format) {
      let csv = "ID;Nome;Bairro;Distrito;Endereco;Latitude;Longitude;Total_Orgaos" + String.fromCharCode(10);
      hubsData.forEach(h => {
        csv += '"' + h.id + '";"' + (h.nome || '') + '";"' + (h.bairro || '') + '";"' + (h.distrito || '') + '";"' + (h.endereco || '') + '";"' + (h.lat || '') + '";"' + (h.lon || '') + '";"' + ((h.orgaos || []).length) + '"' + String.fromCharCode(10);
      });
      const blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8;' });
      downloadBlob(blob, `hubs_complexos_duque_de_caxias_${new Date().toISOString().slice(0,10)}.csv`);
    }

    function downloadBlob(blob, filename) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    }

    function showToast(msg) {
      const t = document.getElementById('toastMsg');
      const txt = document.getElementById('toastText');
      if (!t || !txt) return;
      txt.innerText = msg;
      t.classList.add('active');
      setTimeout(() => {
        t.classList.remove('active');
      }, 3200);
    }

    // BOOTSTRAP INICIAL
    document.addEventListener('DOMContentLoaded', () => {
      initDatabase();
      renderEquipTable();
      renderHubsCards();
    });
  </script>
</body>
</html>
'''

# Realizar substituições
conteudo_final = TEMPLATE.replace('__TOTAL_EQUIPS__', str(len(equips)))
conteudo_final = conteudo_final.replace('__TOTAL_HUBS__', str(len(hubs)))
conteudo_final = conteudo_final.replace('__BAIRROS_OPTIONS__', bairros_options)
conteudo_final = conteudo_final.replace('__DEFAULT_EQUIP__', equips_json_str)
conteudo_final = conteudo_final.replace('__DEFAULT_HUBS__', hubs_json_str)
conteudo_final = conteudo_final.replace('__BAIRROS_JS__', bairros_js_str)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(conteudo_final)
print(f"Salvo index.html com sucesso ({len(conteudo_final)} bytes)!")

with open(GERENCIADOR_PATH, 'w', encoding='utf-8') as f:
    f.write(conteudo_final)
print(f"Salvo gerenciador_enderecos.html com sucesso ({len(conteudo_final)} bytes)!")
