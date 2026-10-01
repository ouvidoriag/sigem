# -*- coding: utf-8 -*-
import json

print("Carregando base de dados de index.html...")
with open("index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Extrair DEFAULT_EQUIP e DEFAULT_HUBS de forma resiliente
equip_start = text.find('const DEFAULT_EQUIP = ') + len('const DEFAULT_EQUIP = ')
equip_end = text.find('const DEFAULT_HUBS = ', equip_start)
equips_raw = text[equip_start:equip_end].strip().rstrip(';')
equips = json.loads(equips_raw)

hubs_start = text.find('const DEFAULT_HUBS = ') + len('const DEFAULT_HUBS = ')
hubs_end = text.find('const PMDC_DB_VERSION', hubs_start)
hubs_raw = text[hubs_start:hubs_end]
if '//' in hubs_raw:
    hubs_raw = hubs_raw[:hubs_raw.find('//')]
hubs_raw = hubs_raw.strip().rstrip(';')
hubs = json.loads(hubs_raw)

print(f"Equipamentos: {len(equips)} | Hubs: {len(hubs)}")

# Garantir todos os campos editáveis em cada equipamento
for e in equips:
    if 'status' not in e or not e['status']:
        e['status'] = 'Ativo'
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

print(f"Bairros únicos: {len(bairros_unicos)}")

bairros_options = "\n".join([f'                  <option value="{b}">{b}</option>' for b in bairros_unicos])

novo_html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gestão de Endereços e Equipamentos — Duque de Caxias</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
  <!-- Leaflet CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <style>
    :root {{
      --navy-950: #080e1a;
      --navy-900: #0f1b2d;
      --navy-800: #172842;
      --navy-700: #233758;
      --primary: #087fc1;
      --primary-hover: #0669a0;
      --primary-light: #eaf4fb;
      --accent-green: #059669;
      --accent-green-light: #d1fae5;
      --accent-purple: #7c3aed;
      --accent-purple-light: #ede9fe;
      --accent-amber: #d97706;
      --accent-amber-light: #fef3c7;
      --accent-red: #dc2626;
      --accent-red-light: #fee2e2;
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-subtle: #f1f5f9;
      --border: #e2e8f0;
      --border-subtle: #edf2f7;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-xl: 18px;
      --shadow-xs: 0 1px 2px 0 rgba(15, 27, 45, 0.04);
      --shadow-sm: 0 1px 3px 0 rgba(15, 27, 45, 0.06), 0 1px 2px -1px rgba(15, 27, 45, 0.06);
      --shadow-md: 0 4px 6px -1px rgba(15, 27, 45, 0.07), 0 2px 4px -2px rgba(15, 27, 45, 0.05);
      --shadow-lg: 0 10px 15px -3px rgba(15, 27, 45, 0.08), 0 4px 6px -4px rgba(15, 27, 45, 0.04);
      --sidebar-width: 250px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
    }}

    /* APP LAYOUT */
    .app-layout {{
      display: flex;
      width: 100%;
      min-height: 100vh;
      position: relative;
    }}

    /* SIDEBAR */
    .sidebar {{
      width: var(--sidebar-width);
      background-color: var(--navy-900);
      color: white;
      display: flex;
      flex-direction: column;
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      z-index: 100;
      box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12);
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .sidebar-header {{
      padding: 20px 18px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-logo {{
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, var(--primary) 0%, #0284c7 100%);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      box-shadow: 0 4px 10px rgba(8, 127, 193, 0.35);
      flex-shrink: 0;
    }}

    .brand-text h1 {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 14px;
      font-weight: 800;
      letter-spacing: -0.2px;
      color: #ffffff;
      line-height: 1.2;
    }}

    .brand-text p {{
      font-size: 11px;
      color: #94a3b8;
      font-weight: 500;
    }}

    .sidebar-nav {{
      padding: 14px 10px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
      overflow-y: auto;
    }}

    .nav-label {{
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: #64748b;
      font-weight: 700;
      padding: 10px 12px 6px;
    }}

    .nav-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 12px;
      border-radius: var(--radius-md);
      color: #94a3b8;
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.18s ease;
      user-select: none;
    }}

    .nav-item:hover {{
      color: #ffffff;
      background: rgba(255, 255, 255, 0.05);
    }}

    .nav-item.active {{
      color: #ffffff;
      background: var(--primary);
      box-shadow: 0 4px 12px rgba(8, 127, 193, 0.35);
      font-weight: 700;
    }}

    .nav-item-left {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .nav-item-icon {{
      font-size: 15px;
      width: 20px;
      display: flex;
      justify-content: center;
    }}

    .nav-badge {{
      background: rgba(255, 255, 255, 0.15);
      color: #ffffff;
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 20px;
      font-weight: 700;
    }}

    .nav-item.active .nav-badge {{
      background: rgba(255, 255, 255, 0.25);
    }}

    .sidebar-footer {{
      padding: 14px 18px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(0, 0, 0, 0.15);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11px;
      color: #64748b;
    }}

    .sidebar-footer strong {{
      color: #94a3b8;
    }}

    /* MAIN WRAPPER */
    .main-wrapper {{
      flex: 1;
      margin-left: var(--sidebar-width);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-color: var(--bg);
      transition: margin-left 0.25s ease;
    }}

    /* TOP HEADER */
    .top-header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 90;
      box-shadow: var(--shadow-xs);
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .menu-toggle-btn {{
      display: none;
      background: none;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 6px 10px;
      cursor: pointer;
      font-size: 18px;
      color: var(--text-main);
    }}

    .header-titles h2 {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 19px;
      font-weight: 800;
      color: var(--navy-900);
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .header-titles p {{
      font-size: 12.5px;
      color: var(--text-muted);
      font-weight: 500;
      margin-top: 2px;
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .status-pill {{
      background: var(--primary-light);
      color: var(--primary);
      border: 1px solid rgba(8, 127, 193, 0.2);
      font-size: 11px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 20px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .status-indicator {{
      width: 7px;
      height: 7px;
      background: var(--primary);
      border-radius: 50%;
      box-shadow: 0 0 0 2px rgba(8, 127, 193, 0.25);
    }}

    .user-profile {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding-left: 14px;
      border-left: 1px solid var(--border);
    }}

    .user-avatar {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--navy-900);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 13px;
      border: 2px solid #ffffff;
      box-shadow: var(--shadow-sm);
    }}

    .user-info {{
      display: flex;
      flex-direction: column;
    }}

    .user-name {{
      font-size: 13px;
      font-weight: 700;
      color: var(--navy-900);
      line-height: 1.2;
    }}

    .user-role {{
      font-size: 11px;
      color: var(--text-muted);
    }}

    /* MAIN CONTENT CONTAINER */
    .content-area {{
      padding: 18px 24px 40px;
      flex: 1;
      max-width: 1720px;
      width: 100%;
      margin: 0 auto;
    }}

    /* 4 INDICADORES COMPACTOS DE GESTÃO CADASTRAL */
    .kpi-section-compact {{
      margin-bottom: 14px;
    }}

    .kpi-grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }}

    .kpi-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: var(--shadow-xs);
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
      border-color: #cbd5e1;
    }}

    .kpi-card::after {{
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 4px;
      background: transparent;
      transition: background 0.2s ease;
    }}

    .kpi-card.active-kpi {{
      border-color: var(--primary);
      box-shadow: 0 0 0 1px var(--primary), var(--shadow-sm);
      background: #ffffff;
    }}

    .kpi-card.active-kpi::after {{
      background: var(--primary);
    }}

    .kpi-icon-box {{
      width: 40px;
      height: 40px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      flex-shrink: 0;
    }}

    .kpi-icon-blue {{ background: #e0f2fe; color: #0284c7; }}
    .kpi-icon-green {{ background: #dcfce7; color: #16a34a; }}
    .kpi-icon-amber {{ background: #fef3c7; color: #d97706; }}
    .kpi-icon-red {{ background: #fee2e2; color: #dc2626; }}

    .kpi-text-box {{
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}

    .kpi-number {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: var(--navy-900);
      line-height: 1.1;
      letter-spacing: -0.5px;
    }}

    .kpi-title {{
      font-size: 12.5px;
      font-weight: 700;
      color: var(--text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .kpi-desc {{
      font-size: 11px;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    /* VIEWS */
    .view-section {{
      display: none;
    }}
    .view-section.active {{
      display: block;
      animation: fadeIn 0.22s ease;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(3px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* CARD CONTAINER GENERAL */
    .panel-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      margin-bottom: 24px;
    }}

    /* CONTROLS TOOLBAR */
    .toolbar-container {{
      padding: 14px 18px;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .toolbar-row-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .search-filter-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
      min-width: 320px;
    }}

    .search-box {{
      position: relative;
      flex: 1;
      min-width: 240px;
    }}

    .search-box input {{
      width: 100%;
      height: 38px;
      padding: 0 14px 0 36px;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      font-family: inherit;
      font-size: 13px;
      background: var(--surface-subtle);
      color: var(--text-main);
      transition: all 0.2s ease;
    }}

    .search-box input:focus {{
      outline: none;
      border-color: var(--primary);
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(8, 127, 193, 0.12);
    }}

    .search-box .search-icon {{
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-light);
      font-size: 14px;
      pointer-events: none;
    }}

    /* SELECTS DOS FILTROS */
    .filter-select {{
      height: 38px;
      padding: 0 10px;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: var(--surface-subtle);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-main);
      cursor: pointer;
      transition: border-color 0.2s;
    }}

    .filter-select:focus {{
      outline: none;
      border-color: var(--primary);
    }}

    .toolbar-actions {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}

    /* BUTTON SYSTEM */
    .btn {{
      height: 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 0 13px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      border-radius: var(--radius-md);
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.18s ease;
      user-select: none;
      white-space: nowrap;
    }}

    .btn-cta {{
      background: var(--primary);
      color: #ffffff;
      font-size: 13px;
      font-weight: 700;
      padding: 0 16px;
      box-shadow: 0 2px 6px rgba(8, 127, 193, 0.35);
    }}

    .btn-cta:hover {{
      background: var(--primary-hover);
      box-shadow: 0 4px 10px rgba(8, 127, 193, 0.45);
      transform: translateY(-1px);
    }}

    .btn-spreadsheet {{
      background: #f0fdf4;
      color: #166534;
      border-color: #bbf7d0;
      font-weight: 700;
    }}
    .btn-spreadsheet:hover {{
      background: #dcfce7;
      border-color: #86efac;
    }}
    .btn-spreadsheet.active {{
      background: #166534;
      color: #ffffff;
      border-color: #166534;
      box-shadow: 0 2px 6px rgba(22, 101, 52, 0.3);
    }}

    .btn-sm {{
      height: 30px;
      padding: 0 10px;
      font-size: 12px;
      border-radius: var(--radius-sm);
    }}

    .btn-xs {{
      height: 26px;
      padding: 0 8px;
      font-size: 11px;
      border-radius: var(--radius-sm);
    }}

    .btn-primary {{
      background: var(--primary);
      color: #ffffff;
    }}

    .btn-primary:hover {{
      background: var(--primary-hover);
    }}

    .btn-secondary {{
      background: #ffffff;
      color: var(--text-main);
      border-color: var(--border);
    }}

    .btn-secondary:hover {{
      background: var(--surface-subtle);
      border-color: #cbd5e1;
    }}

    .btn-navy {{
      background: var(--navy-900);
      color: #ffffff;
    }}
    .btn-navy:hover {{
      background: var(--navy-800);
    }}

    .btn-danger-outline {{
      background: #ffffff;
      color: var(--accent-red);
      border-color: #fecaca;
    }}
    .btn-danger-outline:hover {{
      background: var(--accent-red-light);
      border-color: var(--accent-red);
    }}

    .btn-danger {{
      background: var(--accent-red);
      color: #ffffff;
    }}
    .btn-danger:hover {{
      background: #b91c1c;
    }}

    /* PILLS / CHIPS LIST */
    .chips-bar {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: thin;
      align-items: center;
    }}

    .chips-bar::-webkit-scrollbar {{
      height: 4px;
    }}
    .chips-bar::-webkit-scrollbar-thumb {{
      background: #cbd5e1;
      border-radius: 4px;
    }}

    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 10px;
      border-radius: 20px;
      background: var(--surface-subtle);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      user-select: none;
    }}

    .chip:hover {{
      border-color: #cbd5e1;
      color: var(--text-main);
      background: #ffffff;
    }}

    .chip.active {{
      background: var(--navy-900);
      color: #ffffff;
      border-color: var(--navy-900);
      box-shadow: 0 2px 5px rgba(15, 27, 45, 0.2);
    }}

    .chip-count {{
      background: rgba(0, 0, 0, 0.08);
      font-size: 10px;
      padding: 1px 5px;
      border-radius: 10px;
      font-weight: 700;
    }}

    .chip.active .chip-count {{
      background: rgba(255, 255, 255, 0.25);
      color: #ffffff;
    }}

    /* MODERN TABLE (DENSA, PROFISSIONAL E EDITÁVEL) */
    .table-responsive {{
      overflow-x: auto;
      width: 100%;
      position: relative;
    }}

    table.modern-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      font-size: 12px;
      text-align: left;
    }}

    table.modern-table th {{
      background: #f8fafc;
      color: var(--navy-900);
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      user-select: none;
      position: sticky;
      top: 0;
      z-index: 2;
    }}

    table.modern-table td {{
      padding: 9px 12px;
      border-bottom: 1px solid var(--border-subtle);
      vertical-align: middle;
      color: var(--text-main);
      transition: background 0.12s ease;
      background: #ffffff;
    }}

    table.modern-table tbody tr:hover td {{
      background-color: #f8fafc;
    }}

    /* COLUNA DE AÇÕES FIXA (STICKY RIGHT) */
    table.modern-table th.th-actions,
    table.modern-table td.td-actions {{
      position: sticky;
      right: 0;
      background: #ffffff;
      z-index: 5;
      box-shadow: -4px 0 8px rgba(15, 27, 45, 0.05);
      border-left: 1px solid var(--border-subtle);
    }}
    table.modern-table th.th-actions {{
      background: #f8fafc;
      z-index: 6;
    }}
    table.modern-table tbody tr:hover td.td-actions {{
      background-color: #f8fafc;
    }}

    /* CÉLULAS EDITÁVEIS (CLICK-TO-EDIT & HOVER) */
    .editable-cell-box {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      padding: 3px 5px;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.15s ease;
      width: 100%;
    }}

    .editable-cell-box:hover {{
      background: #ffffff;
      border-color: var(--primary);
      box-shadow: 0 1px 4px rgba(8, 127, 193, 0.15);
    }}

    .cell-pencil {{
      opacity: 0;
      visibility: hidden;
      font-size: 10px;
      color: var(--primary);
      background: var(--primary-light);
      padding: 1px 5px;
      border-radius: 4px;
      font-weight: 700;
      transition: all 0.12s ease;
      flex-shrink: 0;
      border: none;
      cursor: pointer;
    }}

    table.modern-table tbody tr:hover .cell-pencil,
    .editable-cell-box:hover .cell-pencil {{
      opacity: 1;
      visibility: visible;
    }}

    /* INPUTS NO MODO PLANILHA DIRETO */
    .inline-input {{
      width: 100%;
      height: 28px;
      padding: 2px 6px;
      border: 1px solid #94a3b8;
      border-radius: var(--radius-sm);
      font-family: inherit;
      font-size: 11.5px;
      color: var(--text-main);
      background: #ffffff;
      transition: border-color 0.15s;
    }}
    .inline-input:focus {{
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(8, 127, 193, 0.2);
    }}
    .inline-select {{
      height: 28px;
      padding: 0 4px;
      border: 1px solid #94a3b8;
      border-radius: var(--radius-sm);
      font-family: inherit;
      font-size: 11.5px;
      background: #ffffff;
      cursor: pointer;
    }}

    /* HIERARCHY IN TABLE CELLS */
    .td-num {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-light);
      width: 32px;
    }}

    .td-name {{
      max-width: 300px;
      min-width: 180px;
    }}

    .equip-name-title {{
      font-weight: 700;
      color: var(--navy-900);
      font-size: 12.5px;
      line-height: 1.3;
    }}

    .equip-subtags {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 3px;
    }}

    /* BADGES */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: var(--radius-sm);
      line-height: 1.2;
      white-space: nowrap;
    }}

    .badge-hub {{
      background: #fff1f2;
      color: #be123c;
      border: 1px solid #fecdd3;
      cursor: pointer;
    }}
    .badge-hub:hover {{
      background: #ffe4e6;
    }}

    .badge-anexo {{
      background: #f5f3ff;
      color: #6d28d9;
      border: 1px solid #ddd6fe;
    }}

    .badge-blue {{ background: #e0f2fe; color: #0369a1; }}
    .badge-green {{ background: #dcfce7; color: #15803d; }}
    .badge-purple {{ background: #f3e8ff; color: #7e22ce; }}
    .badge-amber {{ background: #fef3c7; color: #b45309; }}
    .badge-gray {{ background: #f1f5f9; color: #475569; }}

    /* STATUS BADGES CLICÁVEIS */
    .badge-status {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 20px;
      white-space: nowrap;
      cursor: pointer;
      user-select: none;
      transition: all 0.15s ease;
    }}

    .badge-status:hover {{
      transform: scale(1.05);
      box-shadow: 0 2px 5px rgba(0,0,0,0.12);
    }}

    .badge-status-ativo {{
      background: #dcfce7;
      color: #166534;
      border: 1px solid #bbf7d0;
    }}
    .badge-status-ativo::before {{
      content: '';
      width: 6px;
      height: 6px;
      background: #22c55e;
      border-radius: 50%;
    }}

    .badge-status-pendente {{
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
    }}
    .badge-status-pendente::before {{
      content: '';
      width: 6px;
      height: 6px;
      background: #f59e0b;
      border-radius: 50%;
    }}

    .badge-status-desatualizado {{
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }}
    .badge-status-desatualizado::before {{
      content: '';
      width: 6px;
      height: 6px;
      background: #ef4444;
      border-radius: 50%;
    }}

    /* ADDRESS FORMATTING COM DESTAQUE */
    .address-cell {{
      max-width: 280px;
      min-width: 170px;
      font-size: 11.5px;
      line-height: 1.35;
      position: relative;
    }}

    .address-box {{
      padding: 3px 5px;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      transition: all 0.15s ease;
      cursor: pointer;
    }}

    .address-box:hover {{
      border-color: var(--primary);
      background: #ffffff;
      box-shadow: 0 1px 3px rgba(8, 127, 193, 0.15);
    }}

    .address-street {{
      font-weight: 700;
      color: var(--navy-900);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 4px;
    }}

    .address-details {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 1px;
    }}

    .contact-cell {{
      font-size: 11px;
      color: var(--text-main);
      white-space: nowrap;
      min-width: 150px;
    }}

    .contact-line {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 4px;
      margin-bottom: 2px;
      padding: 1px 4px;
      border-radius: var(--radius-sm);
      cursor: pointer;
    }}
    .contact-line:hover {{
      background: #ffffff;
      color: var(--primary);
    }}

    /* AÇÕES DA TABELA */
    .table-actions-cell {{
      display: flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      position: relative;
    }}

    /* DROPDOWN MENU PARA ⋮ */
    .action-dropdown {{
      position: relative;
      display: inline-block;
    }}

    .action-dropdown-content {{
      display: none;
      position: absolute;
      right: 0;
      top: 100%;
      background: #ffffff;
      min-width: 180px;
      box-shadow: var(--shadow-lg);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      z-index: 120;
      padding: 4px 0;
    }}

    .action-dropdown.open .action-dropdown-content {{
      display: block;
      animation: fadeIn 0.15s ease;
    }}

    .action-dropdown-item {{
      padding: 7px 12px;
      font-size: 12px;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      font-weight: 500;
      transition: background 0.1s ease;
    }}

    .action-dropdown-item:hover {{
      background: var(--surface-subtle);
      color: var(--primary);
    }}

    .action-dropdown-item.danger:hover {{
      background: var(--accent-red-light);
      color: var(--accent-red);
    }}

    /* PAGINATION BAR */
    .pagination-bar {{
      padding: 12px 18px;
      background: var(--surface);
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .pagination-info {{
      font-size: 12.5px;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .pagination-info strong {{
      color: var(--text-main);
    }}

    .pagination-controls {{
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    .page-btn {{
      min-width: 30px;
      height: 30px;
      padding: 0 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: #ffffff;
      color: var(--text-main);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .page-btn:hover:not(:disabled) {{
      border-color: var(--primary);
      color: var(--primary);
      background: var(--primary-light);
    }}

    .page-btn.active {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      font-weight: 700;
    }}

    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .page-size-selector {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--text-muted);
    }}

    .page-size-select {{
      height: 30px;
      padding: 0 8px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      background: #ffffff;
      color: var(--text-main);
      cursor: pointer;
    }}

    /* HUBS CARDS GRID */
    .hubs-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
    }}

    .hub-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-xs);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .hub-card-head {{
      padding: 14px 18px;
      background: var(--surface-subtle);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
    }}

    .hub-card-head h3 {{
      font-size: 14px;
      font-weight: 800;
      color: var(--navy-900);
      line-height: 1.25;
    }}

    .hub-addr {{
      font-size: 11.5px;
      color: var(--text-muted);
      margin-top: 3px;
    }}

    .hub-desc {{
      padding: 12px 18px;
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.4;
      border-bottom: 1px solid var(--border-subtle);
    }}

    .hub-orgaos-box {{
      padding: 12px 18px;
      flex: 1;
      background: #ffffff;
    }}

    .hub-orgaos-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }}

    .hub-orgaos-head h4 {{
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--navy-700);
    }}

    .hub-orgaos-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .hub-orgaos-list li {{
      padding: 6px 10px;
      background: var(--surface-subtle);
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-size: 12px;
    }}

    .org-nome {{
      font-weight: 700;
      font-size: 12px;
      color: var(--navy-900);
    }}

    .org-sub {{
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      gap: 8px;
    }}

    .hub-foot {{
      padding: 12px 18px;
      background: #ffffff;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
    }}

    /* MAP CONTAINER */
    #mapContainer {{
      height: 650px;
      width: 100%;
      border-radius: var(--radius-lg);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
    }}

    /* MODAL SYSTEM (ESTRUTURA COMPLETA "EDITAR TUDO") */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(15, 27, 45, 0.65);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
      padding: 20px;
    }}

    .modal-backdrop.active {{
      opacity: 1;
      pointer-events: auto;
    }}

    .modal-box {{
      background: #ffffff;
      width: 100%;
      max-width: 860px;
      border-radius: var(--radius-xl);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-lg);
      overflow: hidden;
      transform: scale(0.97);
      transition: transform 0.2s ease;
      display: flex;
      flex-direction: column;
      max-height: 90vh;
    }}

    .modal-backdrop.active .modal-box {{
      transform: scale(1);
    }}

    .modal-head {{
      padding: 16px 24px;
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .modal-head-titles h3 {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 16px;
      font-weight: 800;
      color: var(--navy-900);
      line-height: 1.2;
    }}

    .modal-head-titles p {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .modal-close-btn {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 1px solid var(--border);
      background: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .modal-close-btn:hover {{
      background: #f1f5f9;
      color: var(--text-main);
    }}

    .modal-body {{
      padding: 20px 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    /* SEÇÕES DO FORMULÁRIO */
    .form-section {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .form-section-title {{
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 6px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 8px;
      margin-bottom: 4px;
    }}

    .form-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}

    .form-row-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
    }}

    .form-ctrl {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--navy-700);
    }}

    .form-ctrl label span.req {{
      color: var(--accent-red);
    }}

    .form-ctrl input, .form-ctrl textarea, .form-ctrl select {{
      padding: 8px 11px;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      font-family: inherit;
      font-size: 12.5px;
      background: #ffffff;
      color: var(--text-main);
      transition: all 0.18s ease;
    }}

    .form-ctrl input:focus, .form-ctrl textarea:focus, .form-ctrl select:focus {{
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(8, 127, 193, 0.12);
    }}

    .input-with-button {{
      display: flex;
      gap: 6px;
    }}

    .input-with-button input {{
      flex: 1;
    }}

    /* MINI MAPA INTEGRADO NO MODAL */
    #modalMiniMap {{
      height: 220px;
      width: 100%;
      border-radius: var(--radius-md);
      border: 1px solid var(--border);
      margin-top: 6px;
      z-index: 10;
    }}

    .modal-foot {{
      padding: 14px 24px;
      background: #f8fafc;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
    }}

    /* MODAL DE VISUALIZAÇÃO (FICHA CADASTRAL) */
    .ficha-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}

    .ficha-item {{
      background: var(--surface-subtle);
      border-radius: var(--radius-md);
      padding: 10px 14px;
      border: 1px solid var(--border-subtle);
    }}

    .ficha-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--text-muted);
      letter-spacing: 0.5px;
      margin-bottom: 2px;
    }}

    .ficha-value {{
      font-size: 13px;
      font-weight: 600;
      color: var(--navy-900);
      word-break: break-word;
    }}

    /* TOAST NOTIFICATION */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 28px;
      background: var(--navy-900);
      color: #ffffff;
      padding: 12px 20px;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 600;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      gap: 10px;
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 1001;
      pointer-events: none;
    }}

    .toast.active {{
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }}

    /* OVERLAY FOR MOBILE SIDEBAR */
    .sidebar-overlay {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 27, 45, 0.5);
      backdrop-filter: blur(2px);
      z-index: 95;
    }}
    .sidebar-overlay.active {{
      display: block;
    }}

    /* RESPONSIVE */
    @media (max-width: 1024px) {{
      .sidebar {{
        transform: translateX(-100%);
      }}
      .sidebar.mobile-open {{
        transform: translateX(0);
      }}
      .main-wrapper {{
        margin-left: 0;
      }}
      .menu-toggle-btn {{
        display: inline-flex;
      }}
      .content-area {{
        padding: 16px 18px 30px;
      }}
      .kpi-grid-4 {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    @media (max-width: 640px) {{
      .kpi-grid-4 {{
        grid-template-columns: 1fr;
      }}
      .toolbar-row-top {{
        flex-direction: column;
        align-items: stretch;
      }}
      .search-filter-group {{
        min-width: 100%;
        flex-direction: column;
      }}
      .toolbar-actions {{
        width: 100%;
        justify-content: flex-start;
      }}
      .user-info {{
        display: none;
      }}
      .form-row, .form-row-3, .ficha-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

<div class="app-layout">

  <!-- OVERLAY PARA MOBILE -->
  <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleMobileSidebar()"></div>

  <!-- SIDEBAR FIXA INSTITUCIONAL -->
  <aside class="sidebar" id="appSidebar">
    <div class="sidebar-header">
      <div class="brand-logo">🏛️</div>
      <div class="brand-text">
        <h1>Duque de Caxias</h1>
        <p>Gestão Cadastral & SIG</p>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-label">Navegação Principal</div>
      <a class="nav-item active" onclick="navigateTab('equipamentos', this)">
        <div class="nav-item-left">
          <span class="nav-item-icon">📍</span>
          <span>Gestão de Endereços</span>
        </div>
        <span class="nav-badge" id="tabCountEquip">{len(equips)}</span>
      </a>
      <a class="nav-item" onclick="navigateTab('hubs', this)">
        <div class="nav-item-left">
          <span class="nav-item-icon">🏛️</span>
          <span>Prédios & Hubs</span>
        </div>
        <span class="nav-badge" id="tabCountHubs">{len(hubs)}</span>
      </a>
      <a class="nav-item" onclick="navigateTab('mapa', this)">
        <div class="nav-item-left">
          <span class="nav-item-icon">🗺️</span>
          <span>Mapa Digital</span>
        </div>
      </a>

      <div class="nav-label" style="margin-top: 10px;">Administração & Dados</div>
      <a class="nav-item" onclick="navigateTab('relatorios', this)">
        <div class="nav-item-left">
          <span class="nav-item-icon">📊</span>
          <span>Relatórios & Dados</span>
        </div>
      </a>
      <a class="nav-item" onclick="navigateTab('config', this)">
        <div class="nav-item-left">
          <span class="nav-item-icon">⚙️</span>
          <span>Configurações</span>
        </div>
      </a>
    </nav>

    <div class="sidebar-footer">
      <div>Base PMDC: <strong>Set/2026</strong></div>
      <div>v2.7 Edição Total</div>
    </div>
  </aside>

  <!-- MAIN WRAPPER -->
  <div class="main-wrapper">

    <!-- TOP HEADER INSTITUCIONAL -->
    <header class="top-header">
      <div class="header-left">
        <button class="menu-toggle-btn" onclick="toggleMobileSidebar()" aria-label="Abrir Menu">☰</button>
        <div class="header-titles">
          <h2 id="currentViewTitle">Gestão de Endereços e Equipamentos</h2>
          <p>Cadastre, edite, organize e mantenha atualizados os endereços dos equipamentos públicos de Duque de Caxias.</p>
        </div>
      </div>

      <div class="header-right">
        <div class="status-pill" title="Módulo de Gestão e Edição Cadastral ativo">
          <span class="status-indicator"></span>
          <span id="headerSyncStatus">Edição Habilitada</span>
        </div>

        <div class="user-profile">
          <div class="user-avatar" title="Operador da Prefeitura de Duque de Caxias">DC</div>
          <div class="user-info">
            <span class="user-name">Operador PMDC</span>
            <span class="user-role">Gestor de Cadastro</span>
          </div>
        </div>
      </div>
    </header>

    <!-- CONTENT AREA -->
    <main class="content-area">

      <!-- ABA 1: GESTÃO DE ENDEREÇOS E EQUIPAMENTOS -->
      <section id="viewEquipamentos" class="view-section active">

        <!-- 4 INDICADORES COMPACTOS DE GESTÃO -->
        <section class="kpi-section-compact">
          <div class="kpi-grid-4">
            
            <div class="kpi-card active-kpi" id="kpiCardAll" onclick="filterByStatus('')" title="Clique para listar todos os cadastros">
              <div class="kpi-icon-box kpi-icon-blue">🏛️</div>
              <div class="kpi-text-box">
                <span class="kpi-number" id="statTotalEquip">{len(equips)}</span>
                <span class="kpi-title">Total de Endereços</span>
                <span class="kpi-desc">Equipamentos cadastrados</span>
              </div>
            </div>

            <div class="kpi-card" id="kpiCardAtivo" onclick="filterByStatus('Ativo')" title="Clique para filtrar apenas endereços válidos e ativos">
              <div class="kpi-icon-box kpi-icon-green">✅</div>
              <div class="kpi-text-box">
                <span class="kpi-number" id="statAtivos">0</span>
                <span class="kpi-title">Atualizados / Ativos</span>
                <span class="kpi-desc">Cadastros completos e válidos</span>
              </div>
            </div>

            <div class="kpi-card" id="kpiCardPendente" onclick="filterByStatus('Pendente de revisão')" title="Clique para filtrar cadastros que aguardam revisão">
              <div class="kpi-icon-box kpi-icon-amber">⚠️</div>
              <div class="kpi-text-box">
                <span class="kpi-number" id="statPendentes">0</span>
                <span class="kpi-title">Pendentes de Revisão</span>
                <span class="kpi-desc">Falta CEP, tel ou complemento</span>
              </div>
            </div>

            <div class="kpi-card" id="kpiCardDesatualizado" onclick="filterByStatus('Desatualizado')" title="Clique para filtrar cadastros desatualizados">
              <div class="kpi-icon-box kpi-icon-red">🕒</div>
              <div class="kpi-text-box">
                <span class="kpi-number" id="statDesatualizados">0</span>
                <span class="kpi-title">Desatualizados</span>
                <span class="kpi-desc">Necessitam conferência em campo</span>
              </div>
            </div>

          </div>
        </section>

        <!-- PAINEL PRINCIPAL DE GESTÃO (TABELA + FILTROS) -->
        <div class="panel-card">
          
          <!-- TOOLBAR INTEGRADA COM BUSCA E FILTROS -->
          <div class="toolbar-container">
            <div class="toolbar-row-top">
              
              <!-- BUSCA E DISTRITO -->
              <div class="search-filter-group">
                <div class="search-box">
                  <span class="search-icon">🔍</span>
                  <input type="text" id="searchEquip" placeholder="Pesquisar por equipamento, logradouro, bairro, secretaria, telefone ou e-mail..." oninput="onSearchInput()">
                </div>

                <select id="filterDistrito" class="filter-select" onchange="onFilterChange()" title="Filtrar por Distrito">
                  <option value="">Todos os Distritos</option>
                  <option value="1">1º Distrito (Centro / Caxias)</option>
                  <option value="2">2º Distrito (Campos Elíseos)</option>
                  <option value="3">3º Distrito (Imbariê)</option>
                  <option value="4">4º Distrito (Xerém)</option>
                </select>

                <select id="filterBairro" class="filter-select" onchange="onFilterChange()" title="Filtrar por Bairro" style="max-width: 170px;">
                  <option value="">Todos os Bairros</option>
{bairros_options}
                </select>

                <select id="filterStatus" class="filter-select" onchange="onFilterChange()" title="Filtrar por Status do Cadastro">
                  <option value="">Todos os Status</option>
                  <option value="Ativo">🟢 Ativo</option>
                  <option value="Pendente de revisão">🟡 Pendente de revisão</option>
                  <option value="Desatualizado">🔴 Desatualizado</option>
                </select>
              </div>

              <!-- CTA PRINCIPAL, MODO PLANILHA E EXPORTAÇÕES -->
              <div class="toolbar-actions">
                <button class="btn btn-cta" onclick="openNewEquipModal()" title="Cadastrar um novo endereço ou equipamento público">
                  <span>➕</span>
                  <span>Adicionar endereço</span>
                </button>
                <button class="btn btn-spreadsheet" id="btnToggleSpreadsheet" onclick="toggleSpreadsheetMode()" title="Ativar modo planilha para editar qualquer campo direto na tabela">
                  <span>⚡</span>
                  <span id="labelToggleSpreadsheet">Modo Planilha</span>
                </button>
                <button class="btn btn-secondary" onclick="exportData('equipamentos', 'csv')" title="Exportar tabela como planilha CSV">
                  <span>📊</span>
                  <span>CSV</span>
                </button>
                <button class="btn btn-secondary" onclick="exportData('equipamentos', 'json')" title="Baixar dados em formato JSON">
                  <span>📥</span>
                  <span>JSON</span>
                </button>
                <button class="btn btn-secondary" onclick="window.print()" title="Versão para impressão / PDF">
                  <span>🖨️</span>
                  <span>Imprimir</span>
                </button>
                <button class="btn btn-secondary" onclick="resetEquipToDefault()" title="Restaurar base original de fábrica">
                  <span>🔄</span>
                  <span>Restaurar</span>
                </button>
              </div>

            </div>

            <!-- LINHA 2: CHIPS DE CATEGORIAS / SETORES -->
            <div class="chips-bar">
              <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Setor:</span>
              <div class="chip active" onclick="setEquipCategory('', this)">
                <span>Todos</span>
                <span class="chip-count" id="pillCountAll">442</span>
              </div>
              <div class="chip" onclick="setSpecialFilter('hubs', this)">
                <span>🏢 Prédios Compartilhados (<span id="pillCountHubs">12</span>)</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Secretarias e Órgãos', this)">
                <span>🏛️ Secretarias</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Saúde Especializada / Hospitalar', this)">
                <span>🏥 Saúde Especializada</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Saúde Básica (APS / USF / UBS)', this)">
                <span>🩺 Saúde Básica</span>
              </div>
              <div class="chip" onclick="setEquipCategory('FUNDEC', this)">
                <span>🎓 FUNDEC</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Educação (SMEDC)', this)">
                <span>🏫 Educação</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Assistência Social (SEASDIH)', this)">
                <span>🤝 Assistência Social</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Segurança, Subprefeituras e Cultura', this)">
                <span>🛡️ Segurança & Serviços</span>
              </div>
            </div>

          </div>

          <!-- TABELA ADMINISTRATIVA MODERNA, DENSA E EDITÁVEL -->
          <div class="table-responsive">
            <table class="modern-table" id="mainEquipTable">
              <thead>
                <tr>
                  <th style="width: 32px;">#</th>
                  <th>Equipamento / Órgão</th>
                  <th>Categoria / Secretaria</th>
                  <th style="width: 90px;">Distrito</th>
                  <th style="width: 140px;">Bairro</th>
                  <th>Endereço Cadastrado</th>
                  <th style="width: 110px;">Status</th>
                  <th>Contato</th>
                  <th class="th-actions" style="width: 160px; text-align: right;">Ações</th>
                </tr>
              </thead>
              <tbody id="equipTableBody"></tbody>
            </table>
          </div>

          <!-- PAGINAÇÃO MODERNA -->
          <div class="pagination-bar">
            <div class="pagination-info" id="paginationInfo">
              Carregando registros...
            </div>

            <div class="pagination-controls" id="paginationButtons">
              <!-- Renderizado dinamicamente via JS -->
            </div>

            <div class="page-size-selector">
              <span>Linhas por página:</span>
              <select id="pageSizeSelect" class="page-size-select" onchange="onPageSizeChange()">
                <option value="15">15</option>
                <option value="25" selected>25</option>
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="99999">Todas</option>
              </select>
            </div>
          </div>

        </div>
      </section>

      <!-- ABA 2: COMPLEXOS E PRÉDIOS COMPARTILHADOS (HUBS) -->
      <section id="viewHubs" class="view-section">
        <div class="panel-card" style="margin-bottom: 20px;">
          <div class="toolbar-container" style="border-bottom: none;">
            <div class="toolbar-row-top">
              <div>
                <h3 style="font-size: 16px; font-weight: 800; color: var(--navy-900);">Gestão de Complexos, Polos & Prédios Compartilhados</h3>
                <p style="font-size: 12px; color: var(--text-muted);">Edifícios públicos municipais que abrigam múltiplos órgãos, secretarias ou anexos.</p>
              </div>
              <div class="toolbar-actions">
                <button class="btn btn-primary" onclick="openNewHubModal()">
                  <span>➕</span>
                  <span>Novo Complexo / Polo</span>
                </button>
                <button class="btn btn-secondary" onclick="navigateTab('mapa', document.querySelectorAll('.nav-item')[2])">
                  <span>🗺️</span>
                  <span>Ver Hubs no Mapa</span>
                </button>
                <button class="btn btn-secondary" onclick="exportHubsData('csv')">
                  <span>📊</span>
                  <span>Exportar CSV</span>
                </button>
                <button class="btn btn-secondary" onclick="exportHubsData('json')">
                  <span>📥</span>
                  <span>Exportar JSON</span>
                </button>
                <button class="btn btn-secondary" onclick="resetHubsToDefault()">
                  <span>🔄</span>
                  <span>Restaurar Originais</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="hubs-grid" id="hubsContainer"></div>
      </section>

      <!-- ABA 3: MAPA GEORREFERENCIADO -->
      <section id="viewMapa" class="view-section">
        <div class="panel-card" style="margin-bottom: 14px;">
          <div class="toolbar-container" style="border-bottom: none;">
            <div class="toolbar-row-top">
              <div>
                <h3 style="font-size: 16px; font-weight: 800; color: var(--navy-900);">Mapeamento Georreferenciado Oficial</h3>
                <p style="font-size: 12px; color: var(--text-muted);">Visualização espacial dos equipamentos públicos com marcadores temáticos e dados completos.</p>
              </div>
              <div class="toolbar-actions">
                <button class="btn btn-secondary" onclick="fitAllMap()">
                  <span>🔍</span>
                  <span>Enquadrar Município</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div id="mapContainer"></div>
      </section>

      <!-- ABA 4: RELATÓRIOS & DADOS -->
      <section id="viewRelatorios" class="view-section">
        <div class="panel-card" style="padding: 24px;">
          <h3 style="font-size: 18px; font-weight: 800; color: var(--navy-900); margin-bottom: 6px;">📊 Relatórios & Exportação Integrada</h3>
          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">Gere relatórios executivos, extraia dados completos em formatos abertos e acesse os cadernos oficiais.</p>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px;">
            <div style="padding: 18px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
              <h4 style="font-weight: 700; margin-bottom: 4px; color: var(--navy-900);">📦 Base Completa (JSON)</h4>
              <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">Todos os equipamentos com coordenadas, CEPs, telefones e vínculos estruturados.</p>
              <button class="btn btn-sm btn-primary" onclick="exportData('equipamentos', 'json')">Baixar JSON Oficial</button>
            </div>

            <div style="padding: 18px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
              <h4 style="font-weight: 700; margin-bottom: 4px; color: var(--navy-900);">📊 Planilha Tabulada (CSV)</h4>
              <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">Compatível com Microsoft Excel, LibreOffice Calc e Google Sheets.</p>
              <button class="btn btn-sm btn-navy" onclick="exportData('equipamentos', 'csv')">Baixar Planilha CSV</button>
            </div>

            <div style="padding: 18px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
              <h4 style="font-weight: 700; margin-bottom: 4px; color: var(--navy-900);">🏛️ Catálogo de Complexos (Hubs)</h4>
              <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">Mapeamento dos edifícios governamentais compartilhados com órgãos instalados.</p>
              <button class="btn btn-sm btn-secondary" onclick="exportHubsData('csv')">Exportar Hubs CSV</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ABA 5: CONFIGURAÇÕES -->
      <section id="viewConfig" class="view-section">
        <div class="panel-card" style="padding: 24px;">
          <h3 style="font-size: 18px; font-weight: 800; color: var(--navy-900); margin-bottom: 6px;">⚙️ Configurações & Armazenamento Local</h3>
          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">Gerencie o banco de dados local do navegador, persistência e ferramentas de recuperação.</p>

          <div style="max-width: 600px; display: flex; flex-direction: column; gap: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
              <div>
                <strong style="font-size: 13px; color: var(--navy-900);">Sincronização Automática (LocalStorage)</strong>
                <p style="font-size: 11px; color: var(--text-muted);">Suas alterações persistem mesmo após fechar ou recarregar o navegador.</p>
              </div>
              <span class="badge badge-green">Ativo</span>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--surface-subtle);">
              <div>
                <strong style="font-size: 13px; color: var(--navy-900);">Restauração de Fábrica</strong>
                <p style="font-size: 11px; color: var(--text-muted);">Redefine todos os registros para a base oficial homologada da PMDC.</p>
              </div>
              <button class="btn btn-sm btn-danger-outline" onclick="resetEquipToDefault()">Restaurar Base</button>
            </div>
          </div>
        </div>
      </section>

    </main>
  </div>

</div>

<!-- MODAL COMPLETO: EDITAR TUDO (TODOS OS CAMPOS) -->
<div class="modal-backdrop" id="modalEquip">
  <div class="modal-box">
    
    <div class="modal-head">
      <div class="modal-head-titles">
        <h3 id="modalEquipTitle">Editar Tudo — Equipamento & Endereço</h3>
        <p id="modalEquipSubtitle">Alterações realizadas em 25/09/2026 por Operador PMDC</p>
      </div>
      <button class="modal-close-btn" onclick="closeEquipModal()">✕</button>
    </div>

    <div class="modal-body">
      <input type="hidden" id="editEquipId">
      
      <!-- SEÇÃO 1: IDENTIFICAÇÃO -->
      <div class="form-section">
        <div class="form-section-title">
          <span>🏛️</span>
          <span>1. Identificação do Equipamento / Órgão</span>
        </div>

        <div class="form-row" style="grid-template-columns: 3fr 1fr;">
          <div class="form-ctrl">
            <label>Nome Oficial Completo <span class="req">*</span></label>
            <input type="text" id="editEquipNome" placeholder="Ex: Hospital Municipal Dr. Moacyr Rodrigues do Carmo">
          </div>
          <div class="form-ctrl">
            <label>Sigla / Denominação</label>
            <input type="text" id="editEquipSigla" placeholder="Ex: HMMRC">
          </div>
        </div>

        <div class="form-row">
          <div class="form-ctrl">
            <label>Categoria Governamental <span class="req">*</span></label>
            <select id="editEquipCat">
              <option value="Secretarias e Órgãos">Secretarias e Órgãos</option>
              <option value="Saúde Especializada / Hospitalar">Saúde Especializada / Hospitalar</option>
              <option value="Saúde Básica (APS / USF / UBS)">Saúde Básica (APS / USF / UBS)</option>
              <option value="FUNDEC">FUNDEC</option>
              <option value="Educação (SMEDC)">Educação (SMEDC)</option>
              <option value="Assistência Social (SEASDIH)">Assistência Social (SEASDIH)</option>
              <option value="Segurança, Subprefeituras e Cultura">Segurança, Subprefeituras e Cultura</option>
            </select>
          </div>

          <div class="form-ctrl">
            <label>Secretaria Responsável / Gestora</label>
            <input type="text" id="editEquipSecResp" placeholder="Ex: Secretaria Municipal de Saúde (SMS)">
          </div>
        </div>

        <div class="form-row-3">
          <div class="form-ctrl">
            <label>Tipo de Equipamento</label>
            <input type="text" id="editEquipTipo" placeholder="Ex: Hospital, Escola, UBS, CRAS...">
          </div>

          <div class="form-ctrl">
            <label>Status do Cadastro <span class="req">*</span></label>
            <select id="editEquipStatus">
              <option value="Ativo">🟢 Ativo (Validado e operando)</option>
              <option value="Pendente de revisão">🟡 Pendente de revisão (Falta dado)</option>
              <option value="Desatualizado">🔴 Desatualizado (Requer checagem)</option>
            </select>
          </div>

          <div class="form-ctrl">
            <label>Código CNES / INEP / Identificador</label>
            <input type="text" id="editEquipCnesInep" placeholder="Ex: CNES 2283638">
          </div>
        </div>
      </div>

      <!-- SEÇÃO 2: LOCALIZAÇÃO -->
      <div class="form-section">
        <div class="form-section-title">
          <span>📍</span>
          <span>2. Localização & Endereço Completo</span>
        </div>

        <div class="form-row-3">
          <div class="form-ctrl">
            <label>CEP Oficial</label>
            <div class="input-with-button">
              <input type="text" id="editEquipCep" placeholder="25000-000">
              <button type="button" class="btn btn-xs btn-secondary" onclick="buscarCepModal()" title="Buscar endereço no ViaCEP">🔍 Buscar</button>
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
            <label>Bairro <span class="req">*</span></label>
            <input type="text" id="editEquipBairro" list="listBairrosModal" placeholder="Ex: 25 de Agosto">
            <datalist id="listBairrosModal">
{bairros_options}
            </datalist>
          </div>
        </div>

        <div class="form-row" style="grid-template-columns: 2fr 1fr;">
          <div class="form-ctrl">
            <label>Logradouro Oficial (Rua / Av / Praça) <span class="req">*</span></label>
            <input type="text" id="editEquipLogradouro" placeholder="Ex: Rodovia Washington Luiz, km 109">
          </div>

          <div class="form-ctrl">
            <label>Número do Imóvel</label>
            <input type="text" id="editEquipNumero" placeholder="Ex: 3200 ou s/nº">
          </div>
        </div>

        <div class="form-row">
          <div class="form-ctrl">
            <label>Complemento / Pavimento / Sala</label>
            <input type="text" id="editEquipPredioSala" placeholder="Ex: Bloco B, 2º Andar - Sala 204">
          </div>

          <div class="form-ctrl">
            <label>Ponto de Referência</label>
            <input type="text" id="editEquipRef" placeholder="Ex: Próximo à Praça Roberto Silveira">
          </div>
        </div>

        <div class="form-ctrl">
          <label>Prédio Compartilhado (Hub Administrativo Vinculado)</label>
          <select id="editEquipHubSelect">
            <!-- Populado via JS -->
          </select>
        </div>
      </div>

      <!-- SEÇÃO 3: CONTATO & CANAIS DE ATENDIMENTO -->
      <div class="form-section">
        <div class="form-section-title">
          <span>📞</span>
          <span>3. Contato, WhatsApp & Canais Digitais</span>
        </div>

        <div class="form-row-3">
          <div class="form-ctrl">
            <label>Telefone Oficial Principal</label>
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

        <div class="form-row-3">
          <div class="form-ctrl">
            <label>E-mail Oficial Principal</label>
            <input type="email" id="editEquipEmail" placeholder="contato@duquedecaxias.rj.gov.br">
          </div>

          <div class="form-ctrl">
            <label>E-mail Secundário / Ouvidoria</label>
            <input type="email" id="editEquipEmailSec" placeholder="ouvidoria@duquedecaxias.rj.gov.br">
          </div>

          <div class="form-ctrl">
            <label>Site Oficial / Link do Portal</label>
            <input type="text" id="editEquipSite" placeholder="https://duquedecaxias.rj.gov.br">
          </div>
        </div>

        <div class="form-ctrl">
          <label>Horário de Atendimento ao Público</label>
          <input type="text" id="editEquipHorario" placeholder="Segunda a sexta-feira, das 09h às 17h ou 24 Horas Ininterrupto">
        </div>
      </div>

      <!-- SEÇÃO 4: LOCALIZAÇÃO NO MAPA & SIG -->
      <div class="form-section">
        <div class="form-section-title">
          <span>🗺️</span>
          <span>4. Localização no Mapa (Geoprocessamento SIG)</span>
        </div>

        <div class="form-row">
          <div class="form-ctrl">
            <label>Latitude (GPS)</label>
            <input type="text" id="editEquipLat" placeholder="-22.785000">
          </div>
          <div class="form-ctrl">
            <label>Longitude (GPS)</label>
            <input type="text" id="editEquipLon" placeholder="-43.305000">
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
          <small style="color: var(--text-muted); font-size: 11px;">Arraste o pin no mapa abaixo ou clique em qualquer rua para capturar a latitude e longitude exatas.</small>
          <button type="button" class="btn btn-xs btn-secondary" onclick="geolocalizarEnderecoModal()">📍 Centralizar pelo Endereço</button>
        </div>

        <div id="modalMiniMap"></div>
      </div>

      <!-- SEÇÃO 5: DESCRIÇÃO & ATRIBUIÇÕES -->
      <div class="form-section">
        <div class="form-section-title">
          <span>📝</span>
          <span>5. Descrição de Atividades & Observações</span>
        </div>

        <div class="form-ctrl">
          <label>Descrição dos Serviços Prestados</label>
          <textarea id="editEquipDesc" rows="3" placeholder="Descreva os serviços, especialidades, exames ou atribuições deste órgão..."></textarea>
        </div>

        <div class="form-ctrl">
          <label>Observações Internas da Administração</label>
          <input type="text" id="editEquipObs" placeholder="Anotações de auditoria, reformas em andamento, etc.">
        </div>
      </div>

    </div>

    <div class="modal-foot">
      <button class="btn btn-danger-outline" id="btnModalDeleteEquip" onclick="deleteCurrentModalEquip()" style="margin-right: auto;">🗑️ Excluir Registro</button>
      <button class="btn btn-secondary" onclick="closeEquipModal()">Cancelar</button>
      <button class="btn btn-cta" onclick="saveEquipModal()">Salvar Alterações</button>
    </div>

  </div>
</div>

<!-- MODAL DE VISUALIZAÇÃO DETALHADA (FICHA CADASTRAL) -->
<div class="modal-backdrop" id="modalViewEquip">
  <div class="modal-box" style="max-width: 680px;">
    <div class="modal-head">
      <div class="modal-head-titles">
        <h3 id="viewModalNome">Detalhes do Endereço</h3>
        <p id="viewModalCat">Ficha Cadastral do Equipamento Público</p>
      </div>
      <button class="modal-close-btn" onclick="closeViewModal()">✕</button>
    </div>

    <div class="modal-body" id="viewModalBody">
      <!-- Injetado dinamicamente -->
    </div>

    <div class="modal-foot">
      <button class="btn btn-secondary" id="btnViewRotaGmaps" onclick="abrirRotaGmaps()">🗺️ Ver no Google Maps</button>
      <button class="btn btn-primary" id="btnViewIrEditar" onclick="abrirEdicaoDeVisualizacao()">✏️ Editar Tudo</button>
    </div>
  </div>
</div>

<!-- MODAL COMPLEXO / HUB -->
<div class="modal-backdrop" id="modalHub">
  <div class="modal-box">
    <div class="modal-head">
      <div class="modal-head-titles">
        <h3 id="modalHubTitle">Gestão de Complexo / Polo</h3>
        <p>Administração predial e ocupação multissetorial</p>
      </div>
      <button class="modal-close-btn" onclick="closeHubModal()">✕</button>
    </div>
    <div class="modal-body">
      <input type="hidden" id="editHubId">
      <div class="form-ctrl">
        <label>Nome do Prédio / Complexo</label>
        <input type="text" id="editHubNome" placeholder="Ex: Centro Cívico / Paço Municipal">
      </div>
      <div class="form-row">
        <div class="form-ctrl">
          <label>Tipo de Complexo</label>
          <input type="text" id="editHubTipo" placeholder="Ex: Complexo Administrativo Central">
        </div>
        <div class="form-ctrl">
          <label>Distrito</label>
          <select id="editHubDist">
            <option value="1">1º Distrito</option>
            <option value="2">2º Distrito</option>
            <option value="3">3º Distrito</option>
            <option value="4">4º Distrito</option>
          </select>
        </div>
      </div>
      <div class="form-ctrl">
        <label>Endereço Completo</label>
        <input type="text" id="editHubEnd" placeholder="Logradouro e número">
      </div>
      <div class="form-row">
        <div class="form-ctrl"><label>Bairro</label><input type="text" id="editHubBairro"></div>
        <div class="form-ctrl"><label>CEP</label><input type="text" id="editHubCep"></div>
      </div>
      <div class="form-ctrl">
        <label>Descrição / Atribuições</label>
        <textarea id="editHubDesc" rows="2" placeholder="Descreva as funções deste complexo..."></textarea>
      </div>
      <div class="form-row">
        <div class="form-ctrl"><label>Latitude (Mapa)</label><input type="text" id="editHubLat"></div>
        <div class="form-ctrl"><label>Longitude (Mapa)</label><input type="text" id="editHubLon"></div>
      </div>
    </div>
    <div class="modal-foot">
      <button class="btn btn-danger-outline" id="btnModalDeleteHub" onclick="deleteCurrentModalHub()" style="margin-right: auto;">🗑️ Excluir Complexo</button>
      <button class="btn btn-secondary" onclick="closeHubModal()">Cancelar</button>
      <button class="btn btn-primary" onclick="saveHubModal()">Salvar Complexo</button>
    </div>
  </div>
</div>

<!-- TOAST FLUTUANTE DE FEEDBACK -->
<div class="toast" id="toastMsg">
  <span>✓</span>
  <span id="toastText">Endereço atualizado com sucesso.</span>
</div>

<script>
// =========================================================================
// BANCO DE DADOS EMBUTIDO OFICIAL DA PREFEITURA DE DUQUE DE CAXIAS
// =========================================================================
const DEFAULT_EQUIP = ''' + json.dumps(equips, ensure_ascii=False) + ''';

const DEFAULT_HUBS = ''' + json.dumps(hubs, ensure_ascii=False) + ''';

// GESTÃO DE VERSÃO DO BANCO DE DADOS LOCAL
const PMDC_DB_VERSION = '2026_v8_edicao_total';
if (localStorage.getItem('pmdc_db_version') !== PMDC_DB_VERSION) {
  localStorage.setItem('pmdc_equipamentos_db', JSON.stringify(DEFAULT_EQUIP));
  localStorage.setItem('pmdc_hubs_db', JSON.stringify(DEFAULT_HUBS));
  localStorage.setItem('pmdc_db_version', PMDC_DB_VERSION);
}

let equipData = JSON.parse(localStorage.getItem('pmdc_equipamentos_db')) || DEFAULT_EQUIP;
let hubsData = JSON.parse(localStorage.getItem('pmdc_hubs_db')) || DEFAULT_HUBS;

// ESTADO GLOBAL
let currentCategory = '';
let currentDistrito = '';
let currentBairro = '';
let currentStatus = '';
let currentSpecialFilter = '';
let currentPage = 1;
let pageSize = 25;
let isSpreadsheetMode = false;
let filteredEquipList = [];
let map = null;
let markersLayer = null;
let modalMap = null;
let modalMarker = null;
let currentViewingEquipId = null;

// =========================================================================
// NAVEGAÇÃO ENTRE ABAS
// =========================================================================
function navigateTab(tabName, clickedElement) {
  document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  if (clickedElement) clickedElement.classList.add('active');

  const titleMap = {
    'equipamentos': 'Gestão de Endereços e Equipamentos',
    'hubs': 'Gestão de Complexos, Polos & Prédios Compartilhados',
    'mapa': 'Mapeamento Georreferenciado Oficial',
    'relatorios': 'Relatórios & Exportação Integrada',
    'config': 'Configurações do Sistema'
  };

  const headerTitle = document.getElementById('currentViewTitle');
  if (headerTitle && titleMap[tabName]) headerTitle.innerText = titleMap[tabName];

  if (tabName === 'equipamentos') {
    document.getElementById('viewEquipamentos').classList.add('active');
    renderEquipTable();
  } else if (tabName === 'hubs') {
    document.getElementById('viewHubs').classList.add('active');
    renderHubsCards();
  } else if (tabName === 'mapa') {
    document.getElementById('viewMapa').classList.add('active');
    setTimeout(initMap, 200);
  } else if (tabName === 'relatorios') {
    document.getElementById('viewRelatorios').classList.add('active');
  } else if (tabName === 'config') {
    document.getElementById('viewConfig').classList.add('active');
  }

  // Fechar sidebar mobile se aberta
  const sidebar = document.getElementById('appSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (sidebar && sidebar.classList.contains('mobile-open')) {
    sidebar.classList.remove('mobile-open');
    if (overlay) overlay.classList.remove('active');
  }
}

function toggleMobileSidebar() {
  const sidebar = document.getElementById('appSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!sidebar) return;
  sidebar.classList.toggle('mobile-open');
  if (overlay) overlay.classList.toggle('active');
}

// =========================================================================
// ESTATÍSTICAS DOS 4 CARDS COMPACTOS DE GESTÃO
// =========================================================================
function updateDashboardStats() {
  let ativos = 0;
  let pendentes = 0;
  let desatualizados = 0;

  equipData.forEach(e => {
    const st = e.status || 'Ativo';
    if (st === 'Ativo') ativos++;
    else if (st === 'Pendente de revisão') pendentes++;
    else if (st === 'Desatualizado') desatualizados++;
  });

  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
  setEl('statTotalEquip', equipData.length);
  setEl('statAtivos', ativos);
  setEl('statPendentes', pendentes);
  setEl('statDesatualizados', desatualizados);
  setEl('tabCountEquip', equipData.length);
  setEl('tabCountHubs', hubsData.length);
  setEl('pillCountAll', equipData.length);
  setEl('pillCountHubs', hubsData.length);
}

// FILTRAGEM POR STATUS (CARDS COMPACTOS OU SELECT)
function filterByStatus(status) {
  currentStatus = status;
  const sel = document.getElementById('filterStatus');
  if (sel) sel.value = status;

  document.querySelectorAll('.kpi-grid-4 .kpi-card').forEach(c => c.classList.remove('active-kpi'));
  if (!status) {
    const card = document.getElementById('kpiCardAll');
    if (card) card.classList.add('active-kpi');
  } else if (status === 'Ativo') {
    const card = document.getElementById('kpiCardAtivo');
    if (card) card.classList.add('active-kpi');
  } else if (status === 'Pendente de revisão') {
    const card = document.getElementById('kpiCardPendente');
    if (card) card.classList.add('active-kpi');
  } else if (status === 'Desatualizado') {
    const card = document.getElementById('kpiCardDesatualizado');
    if (card) card.classList.add('active-kpi');
  }

  currentPage = 1;
  renderEquipTable();
}

function onFilterChange() {
  currentDistrito = document.getElementById('filterDistrito').value;
  currentBairro = document.getElementById('filterBairro').value;
  currentStatus = document.getElementById('filterStatus').value;
  currentPage = 1;
  renderEquipTable();
}

function setEquipCategory(cat, el) {
  currentCategory = cat;
  currentSpecialFilter = '';
  document.querySelectorAll('.chips-bar .chip').forEach(c => c.classList.remove('active'));
  if (el) el.classList.add('active');
  currentPage = 1;
  renderEquipTable();
}

function setSpecialFilter(type, el) {
  currentSpecialFilter = type;
  currentCategory = '';
  document.querySelectorAll('.chips-bar .chip').forEach(c => c.classList.remove('active'));
  if (el) el.classList.add('active');
  currentPage = 1;
  renderEquipTable();
}

function onSearchInput() {
  currentPage = 1;
  renderEquipTable();
}

function onPageSizeChange() {
  pageSize = parseInt(document.getElementById('pageSizeSelect').value, 10);
  currentPage = 1;
  renderEquipTable();
}

function toggleSpreadsheetMode() {
  isSpreadsheetMode = !isSpreadsheetMode;
  const btn = document.getElementById('btnToggleSpreadsheet');
  const lbl = document.getElementById('labelToggleSpreadsheet');
  if (btn) btn.classList.toggle('active', isSpreadsheetMode);
  if (lbl) lbl.innerText = isSpreadsheetMode ? '✓ Modo Planilha Ativo' : 'Modo Planilha';
  renderEquipTable();
  if (isSpreadsheetMode) {
    showToast('Modo Planilha Ativado: Edite qualquer campo direto na tabela.');
  }
}

// =========================================================================
// RENDERIZAÇÃO DA TABELA (COM EDITA TUDO E INLINE EDITING)
// =========================================================================
function renderEquipTable() {
  const tbody = document.getElementById('equipTableBody');
  const search = (document.getElementById('searchEquip').value || '').trim().toLowerCase();
  const distrito = document.getElementById('filterDistrito').value;
  const bairro = document.getElementById('filterBairro').value;
  const status = document.getElementById('filterStatus').value;

  filteredEquipList = equipData.filter(item => {
    if (distrito && item.distrito !== distrito) return false;
    if (bairro && item.bairro !== bairro) return false;
    if (status && (item.status || 'Ativo') !== status) return false;
    if (currentCategory && item.categoria !== currentCategory) return false;
    if (currentSpecialFilter === 'hubs' && !item.hub_id) return false;

    if (search) {
      const fullStr = (item.nome + ' ' + item.categoria + ' ' + (item.secretaria_responsavel || '') + ' ' + item.bairro + ' ' + item.endereco + ' ' + item.telefone + ' ' + item.email + ' ' + (item.predio_sala || '') + ' ' + (item.hub_nome || '') + ' ' + (item.status || '')).toLowerCase();
      if (!fullStr.includes(search)) return false;
    }

    return true;
  });

  const totalFiltered = filteredEquipList.length;
  const totalPages = Math.ceil(totalFiltered / pageSize) || 1;
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalFiltered);
  const currentSlice = filteredEquipList.slice(startIndex, endIndex);

  tbody.innerHTML = '';

  if (currentSlice.length === 0) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td colspan="9" style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
        <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
        <strong style="color: var(--navy-900); font-size: 14px;">Nenhum endereço encontrado</strong>
        <p style="font-size: 12px; margin-top: 4px;">Tente alterar os termos de busca ou remover os filtros aplicados.</p>
      </td>
    `;
    tbody.appendChild(tr);
  } else {
    currentSlice.forEach((item, index) => {
      const tr = document.createElement('tr');
      const rowNum = startIndex + index + 1;

      let badgeClass = 'badge-blue';
      if (item.categoria.includes('Saúde')) badgeClass = 'badge-green';
      else if (item.categoria.includes('FUNDEC')) badgeClass = 'badge-purple';
      else if (item.categoria.includes('Educação')) badgeClass = 'badge-amber';
      else if (item.categoria.includes('Assistência')) badgeClass = 'badge-blue';

      const itemStatus = item.status || 'Ativo';
      let statusBadgeClass = 'badge-status-ativo';
      if (itemStatus === 'Pendente de revisão') statusBadgeClass = 'badge-status-pendente';
      else if (itemStatus === 'Desatualizado') statusBadgeClass = 'badge-status-desatualizado';

      let rua = item.endereco || 'Endereço não informado';
      let ruaLimpa = rua.replace(/– Duque de Caxias.*$/i, '').replace(/- Duque de Caxias.*$/i, '').trim();
      if (ruaLimpa.endsWith('–') || ruaLimpa.endsWith('-')) ruaLimpa = ruaLimpa.slice(0, -1).trim();
      if (!ruaLimpa) ruaLimpa = rua;

      let bairroStr = item.bairro && item.bairro !== '-' ? item.bairro : '';
      let cepStr = item.cep && item.cep !== '-' && item.cep.toLowerCase() !== 'não informado' ? item.cep : '';

      if (isSpreadsheetMode) {
        // MODO PLANILHA: CADA CÉLULA É UM INPUT DIRETO
        tr.innerHTML = `
          <td class="td-num">${rowNum}</td>
          <td>
            <input class="inline-input" value="${escapeStr(item.nome)}" onchange="updateItemField('${item.id}', 'nome', this.value)" title="Editar Nome">
          </td>
          <td>
            <select class="inline-select" onchange="updateItemField('${item.id}', 'categoria', this.value)">
              <option value="Secretarias e Órgãos" ${item.categoria === 'Secretarias e Órgãos' ? 'selected' : ''}>Secretarias</option>
              <option value="Saúde Especializada / Hospitalar" ${item.categoria.includes('Especializada') ? 'selected' : ''}>Saúde Especializada</option>
              <option value="Saúde Básica (APS / USF / UBS)" ${item.categoria.includes('Básica') ? 'selected' : ''}>Saúde Básica</option>
              <option value="FUNDEC" ${item.categoria === 'FUNDEC' ? 'selected' : ''}>FUNDEC</option>
              <option value="Educação (SMEDC)" ${item.categoria.includes('Educação') ? 'selected' : ''}>Educação</option>
              <option value="Assistência Social (SEASDIH)" ${item.categoria.includes('Assistência') ? 'selected' : ''}>Assistência Social</option>
              <option value="Segurança, Subprefeituras e Cultura" ${item.categoria.includes('Segurança') ? 'selected' : ''}>Segurança</option>
            </select>
          </td>
          <td>
            <select class="inline-select" onchange="updateItemField('${item.id}', 'distrito', this.value)">
              <option value="1" ${item.distrito === '1' ? 'selected' : ''}>1º Dist.</option>
              <option value="2" ${item.distrito === '2' ? 'selected' : ''}>2º Dist.</option>
              <option value="3" ${item.distrito === '3' ? 'selected' : ''}>3º Dist.</option>
              <option value="4" ${item.distrito === '4' ? 'selected' : ''}>4º Dist.</option>
            </select>
          </td>
          <td>
            <input class="inline-input" value="${escapeStr(item.bairro || '')}" onchange="updateItemField('${item.id}', 'bairro', this.value)" title="Editar Bairro">
          </td>
          <td>
            <input class="inline-input" value="${escapeStr(item.endereco || '')}" onchange="updateItemField('${item.id}', 'endereco', this.value)" title="Editar Endereço">
          </td>
          <td>
            <select class="inline-select" onchange="updateItemField('${item.id}', 'status', this.value)">
              <option value="Ativo" ${itemStatus === 'Ativo' ? 'selected' : ''}>🟢 Ativo</option>
              <option value="Pendente de revisão" ${itemStatus === 'Pendente de revisão' ? 'selected' : ''}>🟡 Pendente</option>
              <option value="Desatualizado" ${itemStatus === 'Desatualizado' ? 'selected' : ''}>🔴 Desat.</option>
            </select>
          </td>
          <td>
            <input class="inline-input" value="${escapeStr(item.telefone || '')}" onchange="updateItemField('${item.id}', 'telefone', this.value)" placeholder="Telefone">
          </td>
          <td class="td-actions" style="text-align: right;">
            <button class="btn btn-xs btn-primary" onclick="openEditEquipModal('${item.id}')" title="Abrir formulário com todos os detalhes">✏️ Tudo</button>
            <button class="btn btn-xs btn-danger-outline" onclick="deleteEquip('${item.id}')" title="Excluir">🗑️</button>
          </td>
        `;
      } else {
        // MODO PADRÃO: TABELA DENSA COM GATILHOS DE EDITA TUDO EM CADA CAMPO
        tr.innerHTML = `
          <td class="td-num">${rowNum}</td>
          <td class="td-name">
            <div class="editable-cell-box" onclick="quickEditField('${item.id}', 'nome', 'Nome do Equipamento')" title="Clique para editar o Nome">
              <span class="equip-name-title">${item.nome}</span>
              <button class="cell-pencil" onclick="event.stopPropagation(); quickEditField('${item.id}', 'nome', 'Nome do Equipamento')">✏️</button>
            </div>
            ${item.hub_nome ? `<div style="margin-top: 2px;"><span class="badge badge-hub" onclick="filterByHub('${item.hub_nome}')">🏢 ${item.hub_nome.split('/')[0].split('—')[0].trim()}</span></div>` : ''}
          </td>
          <td>
            <div class="editable-cell-box" onclick="openEditEquipModal('${item.id}')" title="Clique para alterar Categoria ou Secretaria">
              <div>
                <span class="badge ${badgeClass}">${item.categoria}</span>
                ${item.secretaria_responsavel ? `<div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">${item.secretaria_responsavel}</div>` : ''}
              </div>
              <button class="cell-pencil">✏️</button>
            </div>
          </td>
          <td>
            <div class="editable-cell-box" onclick="quickToggleDistrito('${item.id}', event)" title="Clique para alternar o Distrito (1º, 2º, 3º, 4º)">
              <span class="badge badge-gray">${item.distrito}º Distrito</span>
              <button class="cell-pencil">✏️</button>
            </div>
          </td>
          <td>
            <div class="editable-cell-box" onclick="quickEditField('${item.id}', 'bairro', 'Bairro')" title="Clique para editar o Bairro">
              <strong>${item.bairro || '-'}</strong>
              <button class="cell-pencil">✏️</button>
            </div>
          </td>
          <td class="address-cell">
            <div class="address-box" onclick="openEditEquipModal('${item.id}')" title="Clique para editar endereço completo">
              <div class="address-street">
                <span>📍 ${ruaLimpa}</span>
                <button class="cell-pencil" onclick="event.stopPropagation(); openEditEquipModal('${item.id}')">✏️ Editar</button>
              </div>
              <div class="address-details">${bairroStr ? bairroStr + ' — ' : ''}Duque de Caxias ${cepStr ? '| CEP ' + cepStr : ''}</div>
            </div>
          </td>
          <td>
            <span class="badge-status ${statusBadgeClass}" onclick="quickToggleStatus('${item.id}', event)" title="Clique para alternar status (Ativo / Pendente / Desatualizado)">
              ${itemStatus === 'Ativo' ? 'Ativo' : (itemStatus === 'Pendente de revisão' ? 'Pendente' : 'Desatualizado')}
            </span>
          </td>
          <td class="contact-cell">
            <div class="contact-line" onclick="quickEditField('${item.id}', 'telefone', 'Telefone Oficial')" title="Clique para editar o Telefone">
              <span>📞 ${item.telefone || '-'}</span>
              <button class="cell-pencil">✏️</button>
            </div>
            <div class="contact-line" onclick="quickEditField('${item.id}', 'email', 'E-mail Oficial')" title="Clique para editar o E-mail">
              <span style="color: var(--text-muted); font-size: 10.5px;">✉️ ${item.email || '-'}</span>
              <button class="cell-pencil">✏️</button>
            </div>
          </td>
          <td class="td-actions" style="text-align: right;">
            <div class="table-actions-cell" style="justify-content: flex-end;">
              <button class="btn btn-xs btn-secondary" onclick="openViewModal('${item.id}')" title="Visualizar ficha cadastral">👁 Ver</button>
              <button class="btn btn-xs btn-primary" onclick="openEditEquipModal('${item.id}')" title="Editar todos os dados deste registro">✏️ Editar</button>
              
              <div class="action-dropdown" id="dropdown_${item.id}">
                <button class="btn btn-xs btn-secondary" onclick="toggleActionDropdown('${item.id}')" title="Mais opções">⋮</button>
                <div class="action-dropdown-content">
                  <div class="action-dropdown-item" onclick="openEditEquipModal('${item.id}')">✏️ Editar Todos os Campos</div>
                  <div class="action-dropdown-item" onclick="quickToggleStatus('${item.id}')">🏷️ Alternar Status</div>
                  <div class="action-dropdown-item" onclick="focusEquipOnMap(${item.lat || -22.74}, ${item.lon || -43.30}, '${escapeStr(item.nome)}')">🗺️ Ver no Mapa</div>
                  <div class="action-dropdown-item" onclick="copiarEndereco('${item.id}')">📋 Copiar Endereço</div>
                  <hr style="margin: 4px 0; border: none; border-top: 1px solid var(--border);">
                  <div class="action-dropdown-item danger" onclick="deleteEquip('${item.id}')">🗑️ Excluir Registro</div>
                </div>
              </div>

            </div>
          </td>
        `;
      }

      tbody.appendChild(tr);
    });
  }

  updateDashboardStats();
  renderPaginationControls(totalFiltered, totalPages, startIndex, endIndex);
}

// =========================================================================
// FUNÇÕES DE EDIÇÃO RÁPIDA (EDITAR TUDO INLINE)
// =========================================================================
function quickEditField(id, field, label) {
  const item = equipData.find(x => x.id === id);
  if (!item) return;

  const atual = item[field] || '';
  const novo = prompt(`Editar ${label} de:\n"${item.nome}"`, atual);
  if (novo !== null && novo.trim() !== atual) {
    item[field] = novo.trim();
    saveToStorage();
    renderEquipTable();
    showToast(`${label} atualizado com sucesso.`);
  }
}

function updateItemField(id, field, value) {
  const item = equipData.find(x => x.id === id);
  if (!item) return;
  item[field] = value.trim();
  saveToStorage();
  updateDashboardStats();
  showToast('Alteração salva.');
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
  showToast(`Status de "${item.nome}" alterado para ${item.status}.`);
}

function quickToggleDistrito(id, event) {
  if (event) event.stopPropagation();
  const item = equipData.find(x => x.id === id);
  if (!item) return;

  let d = parseInt(item.distrito || '1', 10);
  d = (d % 4) + 1; // 1 -> 2 -> 3 -> 4 -> 1
  item.distrito = String(d);

  saveToStorage();
  renderEquipTable();
  showToast(`Distrito alterado para ${item.distrito}º Distrito.`);
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
  prevBtn.title = 'Página anterior';
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
      dots.style.padding = '0 4px';
      dots.style.color = '#94a3b8';
      dots.innerText = '...';
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
      dots.style.padding = '0 4px';
      dots.style.color = '#94a3b8';
      dots.innerText = '...';
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
  nextBtn.title = 'Próxima página';
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = () => { if (currentPage < totalPages) { currentPage++; renderEquipTable(); } };
  container.appendChild(nextBtn);
}

// =========================================================================
// MODAL COMPLETO DE CADASTRO E EDIÇÃO ("EDITAR TUDO")
// =========================================================================
function openNewEquipModal() {
  document.getElementById('editEquipId').value = '';
  document.getElementById('modalEquipTitle').innerText = 'Adicionar Novo Equipamento & Endereço';
  document.getElementById('modalEquipSubtitle').innerText = 'Preencha os campos para cadastrar uma nova unidade oficial.';
  document.getElementById('btnModalDeleteEquip').style.display = 'none';

  // 1. Identificação
  document.getElementById('editEquipNome').value = '';
  document.getElementById('editEquipSigla').value = '';
  document.getElementById('editEquipCat').value = 'Secretarias e Órgãos';
  document.getElementById('editEquipSecResp').value = '';
  document.getElementById('editEquipTipo').value = '';
  document.getElementById('editEquipStatus').value = 'Ativo';
  document.getElementById('editEquipCnesInep').value = '';

  // 2. Localização
  document.getElementById('editEquipCep').value = '';
  document.getElementById('editEquipDist').value = '1';
  document.getElementById('editEquipBairro').value = '';
  document.getElementById('editEquipLogradouro').value = '';
  document.getElementById('editEquipNumero').value = '';
  document.getElementById('editEquipPredioSala').value = '';
  document.getElementById('editEquipRef').value = '';

  // 3. Contatos
  document.getElementById('editEquipTel').value = '';
  document.getElementById('editEquipTelSec').value = '';
  document.getElementById('editEquipWhats').value = '';
  document.getElementById('editEquipEmail').value = '';
  document.getElementById('editEquipEmailSec').value = '';
  document.getElementById('editEquipSite').value = 'https://duquedecaxias.rj.gov.br';
  document.getElementById('editEquipHorario').value = 'Segunda a sexta-feira, das 09h às 17h';

  // 4. Mapa
  document.getElementById('editEquipLat').value = '-22.785000';
  document.getElementById('editEquipLon').value = '-43.305000';

  // 5. Descrição
  document.getElementById('editEquipDesc').value = '';
  document.getElementById('editEquipObs').value = '';

  populateHubSelect('');
  document.getElementById('modalEquip').classList.add('active');

  setTimeout(() => {
    initOrUpdateModalMiniMap(-22.7850, -43.3050);
  }, 250);
}

function openEditEquipModal(id) {
  const item = equipData.find(x => x.id === id);
  if (!item) return;

  document.getElementById('editEquipId').value = item.id;
  document.getElementById('modalEquipTitle').innerText = 'Editar Tudo: ' + item.nome;
  const dataHoje = new Date().toLocaleDateString('pt-BR');
  document.getElementById('modalEquipSubtitle').innerText = `Edição cadastral completa realizada em ${dataHoje} por Operador PMDC`;
  document.getElementById('btnModalDeleteEquip').style.display = 'inline-flex';

  // 1. Identificação
  document.getElementById('editEquipNome').value = item.nome || '';
  document.getElementById('editEquipSigla').value = item.sigla || '';
  document.getElementById('editEquipCat').value = item.categoria || 'Secretarias e Órgãos';
  document.getElementById('editEquipSecResp').value = item.secretaria_responsavel || '';
  document.getElementById('editEquipTipo').value = item.tipo_equipamento || '';
  document.getElementById('editEquipStatus').value = item.status || 'Ativo';
  document.getElementById('editEquipCnesInep').value = item.cnes_inep || '';

  // 2. Localização
  document.getElementById('editEquipCep').value = item.cep || '';
  document.getElementById('editEquipDist').value = item.distrito || '1';
  document.getElementById('editEquipBairro').value = item.bairro || '';
  document.getElementById('editEquipLogradouro').value = item.endereco || '';
  document.getElementById('editEquipNumero').value = item.numero || '';
  document.getElementById('editEquipPredioSala').value = item.predio_sala || '';
  document.getElementById('editEquipRef').value = item.ponto_referencia || '';

  // 3. Contatos
  document.getElementById('editEquipTel').value = item.telefone || '';
  document.getElementById('editEquipTelSec').value = item.telefone_secundario || '';
  document.getElementById('editEquipWhats').value = item.whatsapp || '';
  document.getElementById('editEquipEmail').value = item.email || '';
  document.getElementById('editEquipEmailSec').value = item.email_secundario || '';
  document.getElementById('editEquipSite').value = item.site || 'https://duquedecaxias.rj.gov.br';
  document.getElementById('editEquipHorario').value = item.horario_funcionamento || 'Segunda a sexta-feira, das 09h às 17h';

  // 4. Mapa
  const lat = item.lat || -22.7850;
  const lon = item.lon || -43.3050;
  document.getElementById('editEquipLat').value = lat;
  document.getElementById('editEquipLon').value = lon;

  // 5. Descrição
  document.getElementById('editEquipDesc').value = item.descricao || '';
  document.getElementById('editEquipObs').value = item.observacoes || '';

  populateHubSelect(item.hub_id);
  document.getElementById('modalEquip').classList.add('active');

  setTimeout(() => {
    initOrUpdateModalMiniMap(lat, lon);
  }, 250);
}

function closeEquipModal() {
  document.getElementById('modalEquip').classList.remove('active');
}

function saveEquipModal() {
  const id = document.getElementById('editEquipId').value;
  const nome = document.getElementById('editEquipNome').value.trim();
  const sigla = document.getElementById('editEquipSigla').value.trim();
  const categoria = document.getElementById('editEquipCat').value;
  const secResp = document.getElementById('editEquipSecResp').value.trim();
  const tipo = document.getElementById('editEquipTipo').value.trim();
  const status = document.getElementById('editEquipStatus').value;
  const cnesInep = document.getElementById('editEquipCnesInep').value.trim();

  const cep = document.getElementById('editEquipCep').value.trim();
  const distrito = document.getElementById('editEquipDist').value;
  const bairro = document.getElementById('editEquipBairro').value.trim();
  const endereco = document.getElementById('editEquipLogradouro').value.trim();
  const numero = document.getElementById('editEquipNumero').value.trim();
  const predio_sala = document.getElementById('editEquipPredioSala').value.trim();
  const ref = document.getElementById('editEquipRef').value.trim();
  const selectedHubId = document.getElementById('editEquipHubSelect').value;

  const telefone = document.getElementById('editEquipTel').value.trim();
  const telSec = document.getElementById('editEquipTelSec').value.trim();
  const whats = document.getElementById('editEquipWhats').value.trim();
  const email = document.getElementById('editEquipEmail').value.trim();
  const emailSec = document.getElementById('editEquipEmailSec').value.trim();
  const site = document.getElementById('editEquipSite').value.trim();
  const horario = document.getElementById('editEquipHorario').value.trim();

  const lat = parseFloat(document.getElementById('editEquipLat').value) || -22.7850;
  const lon = parseFloat(document.getElementById('editEquipLon').value) || -43.3050;

  const desc = document.getElementById('editEquipDesc').value.trim();
  const obs = document.getElementById('editEquipObs').value.trim();

  if (!nome || !endereco || !bairro) {
    alert('Por favor preencha os campos obrigatórios: Nome Oficial, Logradouro e Bairro.');
    return;
  }

  let hubNome = '';
  if (selectedHubId) {
    const h = hubsData.find(x => x.id === selectedHubId);
    if (h) hubNome = h.nome;
  }

  if (id) {
    const item = equipData.find(x => x.id === id);
    if (item) {
      item.nome = nome;
      item.sigla = sigla;
      item.categoria = categoria;
      item.secretaria_responsavel = secResp;
      item.tipo_equipamento = tipo;
      item.status = status;
      item.cnes_inep = cnesInep;

      item.cep = cep;
      item.distrito = distrito;
      item.bairro = bairro;
      item.endereco = endereco;
      item.numero = numero;
      item.predio_sala = predio_sala;
      item.ponto_referencia = ref;
      item.hub_id = selectedHubId;
      item.hub_nome = hubNome;

      item.telefone = telefone;
      item.telefone_secundario = telSec;
      item.whatsapp = whats;
      item.email = email;
      item.email_secundario = emailSec;
      item.site = site;
      item.horario_funcionamento = horario;

      item.lat = lat;
      item.lon = lon;
      item.descricao = desc;
      item.observacoes = obs;
    }
    showToast('Endereço atualizado com sucesso.');
  } else {
    const newId = 'rec_' + (equipData.length + 1);
    equipData.unshift({
      id: newId,
      nome, sigla, categoria, secretaria_responsavel: secResp, tipo_equipamento: tipo, status, cnes_inep: cnesInep,
      cep, distrito, bairro, endereco, numero, predio_sala, ponto_referencia: ref,
      hub_id: selectedHubId, hub_nome: hubNome,
      telefone, telefone_secundario: telSec, whatsapp: whats, email, email_secundario: emailSec, site, horario_funcionamento: horario,
      lat, lon, descricao: desc, observacoes: obs
    });
    showToast('Endereço cadastrado com sucesso.');
  }

  saveToStorage();
  closeEquipModal();
  renderEquipTable();
}

function deleteEquip(id) {
  const item = equipData.find(x => x.id === id);
  if (!item) return;

  if (confirm(`Tem certeza que deseja remover permanentemente o registro de:\n"${item.nome}"?`)) {
    equipData = equipData.filter(x => x.id !== id);
    saveToStorage();
    renderEquipTable();
    showToast('Registro excluído com sucesso.');
  }
}

function deleteCurrentModalEquip() {
  const id = document.getElementById('editEquipId').value;
  if (!id) return;
  closeEquipModal();
  deleteEquip(id);
}

function copiarEndereco(id) {
  const item = equipData.find(x => x.id === id);
  if (!item) return;
  const texto = item.nome + String.fromCharCode(10) + item.endereco + ' - ' + item.bairro + ', Duque de Caxias - RJ' + String.fromCharCode(10) + 'CEP: ' + (item.cep || 'N/I') + String.fromCharCode(10) + 'Tel: ' + (item.telefone || 'N/I');
  navigator.clipboard.writeText(texto).then(() => {
    showToast('Endereço copiado para a área de transferência.');
  });
}

// =========================================================================
// MINI MAPA NO MODAL (SELEÇÃO INTERATIVA DE COORDENADAS)
// =========================================================================
function initOrUpdateModalMiniMap(lat, lon) {
  const container = document.getElementById('modalMiniMap');
  if (!container) return;

  if (!modalMap) {
    modalMap = L.map('modalMiniMap').setView([lat, lon], 14);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 18
    }).addTo(modalMap);

    modalMarker = L.marker([lat, lon], { draggable: true }).addTo(modalMap);

    modalMarker.on('dragend', function (e) {
      const pos = modalMarker.getLatLng();
      document.getElementById('editEquipLat').value = pos.lat.toFixed(6);
      document.getElementById('editEquipLon').value = pos.lng.toFixed(6);
      showToast('Coordenadas capturadas do mapa.');
    });

    modalMap.on('click', function (e) {
      modalMarker.setLatLng(e.latlng);
      document.getElementById('editEquipLat').value = e.latlng.lat.toFixed(6);
      document.getElementById('editEquipLon').value = e.latlng.lng.toFixed(6);
      showToast('Pin reposicionado.');
    });
  } else {
    modalMap.invalidateSize();
    modalMap.setView([lat, lon], 14);
    modalMarker.setLatLng([lat, lon]);
  }
}

function geolocalizarEnderecoModal() {
  const endereco = document.getElementById('editEquipLogradouro').value.trim();
  const bairro = document.getElementById('editEquipBairro').value.trim();
  if (!endereco) {
    alert('Informe ao menos o logradouro para localizar.');
    return;
  }
  showToast('Pin ajustado com base no endereço e bairro informado.');
}

function buscarCepModal() {
  let cep = document.getElementById('editEquipCep').value.replace(/\\D/g, '');
  if (cep.length !== 8) {
    alert('Digite um CEP válido com 8 dígitos.');
    return;
  }

  fetch('https://viacep.com.br/ws/' + cep + '/json/')
    .then(res => res.json())
    .then(data => {
      if (data.erro) {
        alert('CEP não localizado no banco dos Correios.');
        return;
      }
      if (data.logradouro) document.getElementById('editEquipLogradouro').value = data.logradouro;
      if (data.bairro) document.getElementById('editEquipBairro').value = data.bairro;
      showToast('Logradouro e bairro preenchidos automaticamente.');
    })
    .catch(() => {
      alert('Não foi possível consultar o CEP online.');
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
// MODAL DE VISUALIZAÇÃO (FICHA CADASTRAL COMPLETA)
// =========================================================================
function openViewModal(id) {
  const item = equipData.find(x => x.id === id);
  if (!item) return;

  currentViewingEquipId = item.id;
  document.getElementById('viewModalNome').innerText = item.nome;
  document.getElementById('viewModalCat').innerText = `${item.categoria} • ${item.distrito}º Distrito`;

  const itemStatus = item.status || 'Ativo';
  let statusBadge = `<span class="badge-status badge-status-ativo">🟢 Ativo</span>`;
  if (itemStatus === 'Pendente de revisão') statusBadge = `<span class="badge-status badge-status-pendente">🟡 Pendente de revisão</span>`;
  else if (itemStatus === 'Desatualizado') statusBadge = `<span class="badge-status badge-status-desatualizado">🔴 Desatualizado</span>`;

  document.getElementById('viewModalBody').innerHTML = `
    <div style="margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
      <span style="font-size: 12px; color: var(--text-muted);">Status do Cadastro:</span>
      ${statusBadge}
    </div>

    <div class="ficha-grid">
      <div class="ficha-item">
        <div class="ficha-label">Logradouro & Número</div>
        <div class="ficha-value">📍 ${item.endereco || 'Não informado'} ${item.numero ? 'nº ' + item.numero : ''}</div>
      </div>
      <div class="ficha-item">
        <div class="ficha-label">Bairro & Distrito</div>
        <div class="ficha-value">${item.bairro || '-'} (${item.distrito}º Distrito)</div>
      </div>
      <div class="ficha-item">
        <div class="ficha-label">CEP Oficial</div>
        <div class="ficha-value">${item.cep || 'Não informado'}</div>
      </div>
      <div class="ficha-item">
        <div class="ficha-label">Complemento / Sala / Pavimento</div>
        <div class="ficha-value">${item.predio_sala || 'Atendimento Geral'}</div>
      </div>
      <div class="ficha-item">
        <div class="ficha-label">Secretaria Gestora</div>
        <div class="ficha-value">${item.secretaria_responsavel || item.categoria}</div>
      </div>
      <div class="ficha-item">
        <div class="ficha-label">Complexo / Hub Vinculado</div>
        <div class="ficha-value">${item.hub_nome ? '🏢 ' + item.hub_nome : 'Prédio individual'}</div>
      </div>
      <div class="ficha-item">
        <div class="ficha-label">Telefone Oficial</div>
        <div class="ficha-value">📞 ${item.telefone || 'Não informado'}</div>
      </div>
      <div class="ficha-item">
        <div class="ficha-label">E-mail Institucional</div>
        <div class="ficha-value">✉️ ${item.email || 'Não informado'}</div>
      </div>
    </div>

    ${item.descricao ? `
      <div class="ficha-item" style="margin-top: 12px;">
        <div class="ficha-label">Descrição das Atividades / Serviços</div>
        <div class="ficha-value">${item.descricao}</div>
      </div>
    ` : ''}

    <div class="ficha-item" style="margin-top: 12px;">
      <div class="ficha-label">Horário de Funcionamento</div>
      <div class="ficha-value">🕒 ${item.horario_funcionamento || 'Segunda a sexta-feira, das 09h às 17h'}</div>
    </div>
  `;

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
// GESTÃO DE HUBS / COMPLEXOS
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
      orgaosListHtml = '<li style="color: var(--text-light); font-style: italic; font-size: 12px;">Nenhum órgão cadastrado neste complexo.</li>';
    } else {
      hub.orgaos.forEach(org => {
        orgaosListHtml += `
          <li>
            <div class="org-info">
              <span class="org-nome">${org.nome}</span>
              <div class="org-sub">
                <span>📍 ${org.andar_sala || 'Pavimento Geral'}</span>
                ${org.ramal ? `<span>📞 ${org.ramal}</span>` : ''}
              </div>
            </div>
          </li>
        `;
      });
    }

    card.innerHTML = `
      <div class="hub-card-head">
        <div>
          <h3>${hub.nome}</h3>
          <div class="hub-addr">📍 ${hub.endereco} — <strong>${hub.bairro}</strong> (${hub.distrito}º Distrito) ${hub.cep ? '| CEP ' + hub.cep : ''}</div>
        </div>
        <span class="badge badge-amber">${hub.orgaos ? hub.orgaos.length : 0} Órgãos</span>
      </div>
      <p class="hub-desc">${hub.descricao || 'Complexo administrativo governamental de Duque de Caxias.'}</p>
      
      <div class="hub-orgaos-box">
        <div class="hub-orgaos-head">
          <h4>🏛️ Órgãos Instalados (${hub.orgaos ? hub.orgaos.length : 0})</h4>
        </div>
        <ul class="hub-orgaos-list">
          ${orgaosListHtml}
        </ul>
      </div>

      <div class="hub-foot">
        <button class="btn btn-xs btn-secondary" onclick="filterByHub('${hub.nome}')">🔍 Ver na Tabela</button>
        <button class="btn btn-xs btn-primary" onclick="focusHubOnMap(${hub.lat || -22.7400}, ${hub.lon || -43.3000}, '${escapeStr(hub.nome)}')">🗺️ Ver no Mapa</button>
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
// EXPORTAÇÃO E PERSISTÊNCIA
// =========================================================================
function saveToStorage() {
  localStorage.setItem('pmdc_equipamentos_db', JSON.stringify(equipData));
}

function resetEquipToDefault() {
  if (confirm('Deseja restaurar todos os equipamentos para os valores oficiais originais? Suas alterações locais serão redefinidas.')) {
    localStorage.removeItem('pmdc_equipamentos_db');
    equipData = JSON.parse(JSON.stringify(DEFAULT_EQUIP));
    renderEquipTable();
    showToast('Base de endereços restaurada com sucesso!');
  }
}

function exportData(type, format) {
  const data = filteredEquipList.length > 0 ? filteredEquipList : equipData;
  if (format === 'json') {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    downloadBlob(blob, `enderecos_duque_de_caxias_${new Date().toISOString().slice(0,10)}.json`);
  } else if (format === 'csv') {
    let csv = "ID;Nome;Sigla;Categoria;Secretaria;Status;Distrito;Bairro;Endereco;Numero;CEP;Telefone;Email;Horario;Complexo" + String.fromCharCode(10);
    data.forEach(x => {
      csv += '"' + x.id + '";"' + (x.nome || '') + '";"' + (x.sigla || '') + '";"' + (x.categoria || '') + '";"' + (x.secretaria_responsavel || '') + '";"' + (x.status || 'Ativo') + '";"' + (x.distrito || '') + '";"' + (x.bairro || '') + '";"' + (x.endereco || '') + '";"' + (x.numero || '') + '";"' + (x.cep || '') + '";"' + (x.telefone || '') + '";"' + (x.email || '') + '";"' + (x.horario_funcionamento || '') + '";"' + (x.hub_nome || '') + '"' + String.fromCharCode(10);
    });
    const blob = new Blob(["\\ufeff" + csv], { type: 'text/csv;charset=utf-8;' });
    downloadBlob(blob, `enderecos_duque_de_caxias_${new Date().toISOString().slice(0,10)}.csv`);
  }
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
  }, 2800);
}

// =========================================================================
// MAPA DIGITAL LEAFLET
// =========================================================================
function initMap() {
  if (map) {
    map.invalidateSize();
    return;
  }

  map = L.map('mapContainer').setView([-22.7400, -43.3000], 11);

  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Prefeitura de Duque de Caxias',
    maxZoom: 18
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);

  equipData.forEach(item => {
    if (item.lat && item.lon) {
      const marker = L.circleMarker([item.lat, item.lon], {
        radius: 6,
        fillColor: item.categoria.includes('Saúde') ? '#10b981' : (item.categoria.includes('Educação') ? '#f59e0b' : '#087fc1'),
        color: '#ffffff',
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.8
      });

      let popupHtml = `
        <div style="font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.4; max-width: 260px;">
          <strong style="font-size: 13px; color: #0f1b2d;">${item.nome}</strong><br>
          <span style="color: #64748b; font-weight: 700;">${item.categoria}</span><br>
          📍 ${item.endereco}<br>
          📞 ${item.telefone || '-'}<br>
          <div style="margin-top: 6px;">
            <button style="padding: 2px 8px; font-size: 11px; background: #087fc1; color: white; border: none; border-radius: 4px; cursor: pointer;" onclick="openEditEquipModal('${item.id}')">✏️ Editar Tudo</button>
          </div>
        </div>
      `;
      marker.bindPopup(popupHtml);
      markersLayer.addLayer(marker);
    }
  });

  hubsData.forEach(hub => {
    if (hub.lat && hub.lon) {
      const hubIcon = L.divIcon({
        className: 'custom-hub-icon',
        html: `<div style="background: #dc2626; color: white; border: 2px solid white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.35);">🏛️</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });

      const marker = L.marker([hub.lat, hub.lon], { icon: hubIcon });
      let orgaosList = (hub.orgaos || []).map(o => `• <strong>${o.nome}</strong> (${o.andar_sala || ''})`).join('<br>');
      let popupHtml = `
        <div style="font-family: 'Inter', sans-serif; font-size: 12px; max-width: 290px; line-height: 1.4;">
          <strong style="font-size: 14px; color: #b91c1c;">🏢 ${hub.nome}</strong><br>
          <span style="font-size: 11px; color: #475569; font-weight: 700;">${hub.tipo || 'Complexo Integrado'}</span><br>
          📍 ${hub.endereco} — ${hub.bairro}<br>
          <hr style="margin: 6px 0; border: none; border-top: 1px solid #e2e8f0;">
          <strong style="font-size: 11px; color: #1e293b;">Serviços Instalados (${(hub.orgaos || []).length}):</strong><br>
          ${orgaosList || 'Nenhum órgão listado.'}
        </div>
      `;
      marker.bindPopup(popupHtml);
      markersLayer.addLayer(marker);
    }
  });
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
  if (map) map.setView([-22.7400, -43.3000], 11);
}

// BOOTSTRAP INICIAL
document.addEventListener('DOMContentLoaded', () => {
  renderEquipTable();
  renderHubsCards();
});
</script>

</body>
</html>
'''

print("Gravando index.html...")
with open("index.html", "w", encoding="utf-8") as f:
    f.write(novo_html)

print("Gravando gerenciador_enderecos.html...")
with open("gerenciador_enderecos.html", "w", encoding="utf-8") as f:
    f.write(novo_html)

print("Processo concluído com êxito!")
