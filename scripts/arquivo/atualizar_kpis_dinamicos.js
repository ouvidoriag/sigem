const fs = require('fs');

function updateHtml(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');

  // 1. Replace KPI Grid
  const kpiRegex = /<div class="kpi-grid">[\s\S]*?<\/div>\s*<\/section>/;
  const newKpiGrid = `<div class="kpi-grid">
          
          <div class="kpi-card active-kpi" onclick="quickFilterKpi('')" title="Clique para ver todos os equipamentos">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-blue">🏛️</span>
              <span class="kpi-number" id="statTotalEquip">426</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Equipamentos Públicos</div>
              <div class="kpi-desc">Total consolidado no município</div>
            </div>
          </div>

          <div class="kpi-card" onclick="navigateTab('hubs', document.querySelectorAll('.nav-item')[1])" title="Clique para gerenciar os Complexos Compartilhados">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-navy">🏢</span>
              <span class="kpi-number" id="statTotalHubs">12</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Hubs / Prédios Integrados</div>
              <div class="kpi-desc">Complexos multissetoriais</div>
            </div>
          </div>

          <div class="kpi-card" onclick="quickFilterKpi('Secretarias e Órgãos')" title="Filtrar Secretarias e Gabinetes">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-blue">🏛️</span>
              <span class="kpi-number" id="statSecretarias">32</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Secretarias & Gabinete</div>
              <div class="kpi-desc">Órgãos do Poder Executivo</div>
            </div>
          </div>

          <div class="kpi-card" onclick="quickFilterKpi('Saúde Especializada / Hospitalar')" title="Filtrar Hospitais, UPAs e Postos de Saúde">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-green">🏥</span>
              <span class="kpi-number" id="statSaude">92</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Hospitais, UPAs & USFs</div>
              <div class="kpi-desc">Rede municipal de saúde</div>
            </div>
          </div>

          <div class="kpi-card" onclick="quickFilterKpi('Educação (SMEDC)')" title="Filtrar Escolas, Creches e Sede SMEDC">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-amber">🏫</span>
              <span class="kpi-number" id="statEducacao">209</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Escolas & Creches</div>
              <div class="kpi-desc">Rede oficial de ensino</div>
            </div>
          </div>

          <div class="kpi-card" onclick="quickFilterKpi('FUNDEC')" title="Filtrar Polos da FUNDEC">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-purple">🎓</span>
              <span class="kpi-number" id="statFundec">35</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Polos da FUNDEC</div>
              <div class="kpi-desc">Qualificação profissional</div>
            </div>
          </div>

          <div class="kpi-card" onclick="quickFilterKpi('Assistência Social (SEASDIH)')" title="Filtrar Assistência Social e Conselhos">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-red">🤝</span>
              <span class="kpi-number" id="statAssistencia">30</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Assistência Social</div>
              <div class="kpi-desc">CRAS, CREAS e Conselhos</div>
            </div>
          </div>

          <div class="kpi-card" onclick="quickFilterKpi('Segurança, Subprefeituras e Cultura')" title="Filtrar Segurança, Defesa Civil, Obras e Serviços">
            <div class="kpi-top">
              <span class="kpi-icon-box kpi-icon-navy">🛡️</span>
              <span class="kpi-number" id="statSeguranca">28</span>
            </div>
            <div class="kpi-bottom">
              <div class="kpi-title">Segurança & Serviços</div>
              <div class="kpi-desc">Guarda, Defesa Civil e Obras</div>
            </div>
          </div>

        </div>
      </section>`;

  if (kpiRegex.test(html)) {
    html = html.replace(kpiRegex, newKpiGrid);
    console.log('Replaced KPI Grid in', filePath);
  } else {
    console.error('Could not find KPI Grid in', filePath);
  }

  // 2. Replace Chips Bar
  const chipsRegex = /<!-- LINHA 2: CHIPS \/ PILLS DE CATEGORIAS -->[\s\S]*?<div class="chips-bar">[\s\S]*?<\/div>\s*<\/div>/;
  const newChipsBar = `<!-- LINHA 2: CHIPS / PILLS DE CATEGORIAS -->
            <div class="chips-bar">
              <div class="chip active" onclick="setEquipCategory('', this)">
                <span>Todos os Setores</span>
                <span class="chip-count" id="pillCountAll">426</span>
              </div>
              <div class="chip" onclick="setSpecialFilter('hubs', this)">
                <span>🏢 Prédios Compartilhados (<span id="pillCountHubs">12</span>)</span>
              </div>
              <div class="chip" onclick="setSpecialFilter('anexos', this)">
                <span>📍 Módulos & Anexos</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Secretarias e Órgãos', this)">
                <span>🏛️ Secretarias & Gabinete (<span id="pillCountSecretarias">32</span>)</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Saúde Especializada / Hospitalar', this)">
                <span>🏥 Saúde Especializada & UPAs (<span id="pillCountSaudeEsp">34</span>)</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Saúde Básica (APS / USF / UBS)', this)">
                <span>🩺 Atenção Básica (USF / UBS) (<span id="pillCountSaudeBas">58</span>)</span>
              </div>
              <div class="chip" onclick="setEquipCategory('FUNDEC', this)">
                <span>🎓 FUNDEC (<span id="pillCountFundec">35</span>)</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Educação (SMEDC)', this)">
                <span>🏫 Educação (<span id="pillCountEducacao">209</span>)</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Assistência Social (SEASDIH)', this)">
                <span>🤝 Assistência Social (<span id="pillCountAssistencia">30</span>)</span>
              </div>
              <div class="chip" onclick="setEquipCategory('Segurança, Subprefeituras e Cultura', this)">
                <span>🛡️ Segurança, Obras & Serviços (<span id="pillCountSeguranca">28</span>)</span>
              </div>
            </div>

          </div>`;

  if (chipsRegex.test(html)) {
    html = html.replace(chipsRegex, newChipsBar);
    console.log('Replaced Chips Bar in', filePath);
  } else {
    console.error('Could not find Chips Bar in', filePath);
  }

  // 3. Add / Update updateDashboardStats() in JavaScript
  const statsFnStr = `
function updateDashboardStats() {
  const counts = {
    total: equipData.length,
    hubs: (typeof hubsData !== 'undefined' && hubsData) ? hubsData.length : 12,
    secretarias: 0,
    saudeEsp: 0,
    saudeBas: 0,
    saudeTotal: 0,
    educacao: 0,
    fundec: 0,
    assistencia: 0,
    seguranca: 0
  };

  equipData.forEach(e => {
    const cat = e.categoria || '';
    if (cat === 'Secretarias e Órgãos') counts.secretarias++;
    else if (cat === 'Saúde Especializada / Hospitalar') { counts.saudeEsp++; counts.saudeTotal++; }
    else if (cat === 'Saúde Básica (APS / USF / UBS)') { counts.saudeBas++; counts.saudeTotal++; }
    else if (cat === 'Educação (SMEDC)') counts.educacao++;
    else if (cat === 'FUNDEC') counts.fundec++;
    else if (cat === 'Assistência Social (SEASDIH)') counts.assistencia++;
    else if (cat === 'Segurança, Subprefeituras e Cultura') counts.seguranca++;
  });

  // KPI cards
  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
  setEl('statTotalEquip', counts.total);
  setEl('statTotalHubs', counts.hubs);
  setEl('statSecretarias', counts.secretarias);
  setEl('statSaude', counts.saudeTotal);
  setEl('statEducacao', counts.educacao);
  setEl('statFundec', counts.fundec);
  setEl('statAssistencia', counts.assistencia);
  setEl('statSeguranca', counts.seguranca);

  // Sidebar badges
  setEl('tabCountEquip', counts.total);
  setEl('tabCountHubs', counts.hubs);

  // Chips bar counts
  setEl('pillCountAll', counts.total);
  setEl('pillCountHubs', counts.hubs);
  setEl('pillCountSecretarias', counts.secretarias);
  setEl('pillCountSaudeEsp', counts.saudeEsp);
  setEl('pillCountSaudeBas', counts.saudeBas);
  setEl('pillCountFundec', counts.fundec);
  setEl('pillCountEducacao', counts.educacao);
  setEl('pillCountAssistencia', counts.assistencia);
  setEl('pillCountSeguranca', counts.seguranca);
}
`;

  // Check if updateDashboardStats already exists
  if (!html.includes('function updateDashboardStats()')) {
    // Insert before renderEquipTable
    html = html.replace('function renderEquipTable() {', statsFnStr + '\nfunction renderEquipTable() {');
  }

  // Ensure updateDashboardStats is called inside renderEquipTable
  if (!html.includes('updateDashboardStats();')) {
    html = html.replace("document.getElementById('statTotalEquip').innerText = equipData.length;", "updateDashboardStats();\n  document.getElementById('statTotalEquip').innerText = equipData.length;");
  }

  // Also call it in initApp
  if (html.includes('function initApp() {') && !html.includes('initApp() {\n  updateDashboardStats();')) {
    html = html.replace('function initApp() {', 'function initApp() {\n  updateDashboardStats();');
  }

  // Update report text 398 -> 426
  html = html.replace('Todos os 398 equipamentos', 'Todos os 426 equipamentos');

  fs.writeFileSync(filePath, html, 'utf8');
  console.log('Saved', filePath);
}

updateHtml('index.html');
updateHtml('gerenciador_enderecos.html');
