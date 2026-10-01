const fs = require('fs');

const baseEquip = JSON.parse(fs.readFileSync('dados/todos_os_enderecos_duque_de_caxias.json', 'utf8'));
console.log('Loaded database for web app:', baseEquip.length);

function updateFile(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');

  // 1. Update version
  html = html.replace(/const PMDC_DB_VERSION = '.*?';/, "const PMDC_DB_VERSION = '2026_v6_orientahub_integrado';");

  // 2. Replace DEFAULT_EQUIP
  const startIdx = html.indexOf('const DEFAULT_EQUIP = ');
  const scriptRest = html.substring(startIdx + 'const DEFAULT_EQUIP = '.length);
  let depth = 0, jsonEnd = -1;
  for (let i = 0; i < scriptRest.length; i++) {
    if (scriptRest[i] === '[') depth++;
    else if (scriptRest[i] === ']') { depth--; if (depth === 0) { jsonEnd = i + 1; break; } }
  }
  const before = html.substring(0, startIdx + 'const DEFAULT_EQUIP = '.length);
  const after = scriptRest.substring(jsonEnd);
  html = before + JSON.stringify(baseEquip) + after;

  // 3. Update initial KPI numbers in HTML markup
  html = html.replace(/<span class="kpi-number" id="statTotalEquip">\d+<\/span>/, `<span class="kpi-number" id="statTotalEquip">442</span>`);
  html = html.replace(/<span class="kpi-number" id="statSaude">\d+<\/span>/, `<span class="kpi-number" id="statSaude">93</span>`);
  html = html.replace(/<span class="kpi-number" id="statAssistencia">\d+<\/span>/, `<span class="kpi-number" id="statAssistencia">43</span>`);
  html = html.replace(/<span class="kpi-number" id="statSeguranca">\d+<\/span>/, `<span class="kpi-number" id="statSeguranca">30</span>`);

  // 4. Update initial pill counts in HTML markup
  html = html.replace(/<span class="chip-count" id="pillCountAll">\d+<\/span>/, `<span class="chip-count" id="pillCountAll">442</span>`);
  html = html.replace(/<span id="pillCountSaudeBas">\d+<\/span>/, `<span id="pillCountSaudeBas">59</span>`);
  html = html.replace(/<span id="pillCountAssistencia">\d+<\/span>/, `<span id="pillCountAssistencia">43</span>`);
  html = html.replace(/<span id="pillCountSeguranca">\d+<\/span>/, `<span id="pillCountSeguranca">30</span>`);

  // 5. Update renderEquipTable row rendering to display Horário badge and search
  const oldRowCode = `<div class="equip-name-title">\${item.nome}</div>\n          <div class="equip-subtags">\${tagsHtml}</div>`;
  const newRowCode = `<div class="equip-name-title">\${item.nome}</div>\n          <div class="equip-subtags">\${tagsHtml}\${item.horario_funcionamento ? \`<span class="badge badge-gray" style="font-size: 10px; margin-top: 3px;" title="Horário de Atendimento">🕒 \${item.horario_funcionamento}</span>\` : ''}</div>`;
  if (html.includes(oldRowCode)) {
    html = html.replace(oldRowCode, newRowCode);
  }

  // Update search string to include horario and descricao
  const oldSearch = `const fullStr = \`\${item.nome} \${item.categoria} \${item.bairro} \${item.endereco} \${item.telefone} \${item.email} \${item.predio_sala || ''} \${item.hub_nome || ''}\`.toLowerCase();`;
  const newSearch = `const fullStr = \`\${item.nome} \${item.categoria} \${item.bairro} \${item.endereco} \${item.telefone} \${item.email} \${item.predio_sala || ''} \${item.hub_nome || ''} \${item.horario_funcionamento || ''} \${item.descricao || ''}\`.toLowerCase();`;
  if (html.includes(oldSearch)) {
    html = html.replace(oldSearch, newSearch);
  }

  // Update popup HTML on map to show hours and description
  const oldPopup = `📍 \${item.endereco}<br>\n          📞 \${item.telefone || '-'}<br>\n          ✉️ \${item.email || '-'}`;
  const newPopup = `📍 \${item.endereco}<br>\n          📞 \${item.telefone || '-'}<br>\n          ✉️ \${item.email || '-'}\${item.horario_funcionamento ? \`<br>🕒 \${item.horario_funcionamento}\` : ''}`;
  if (html.includes(oldPopup)) {
    html = html.replace(oldPopup, newPopup);
  }

  // Update reports text 426 -> 442
  html = html.replace(/Todos os 426 equipamentos/g, 'Todos os 442 equipamentos');

  fs.writeFileSync(filePath, html, 'utf8');
  console.log('Successfully updated', filePath);
}

updateFile('index.html');
updateFile('gerenciador_enderecos.html');
