const fs = require('fs');

function moveKpisInsideEquipamentos(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');

  // Extract <section class="kpi-section">...</section>
  const kpiSectionMatch = html.match(/(<!-- DASHBOARD \/ KPIS CARDS -->[\s\S]*?<section class="kpi-section">[\s\S]*?<\/section>)/);
  if (!kpiSectionMatch) {
    console.error('Could not find kpi-section in', filePath);
    return;
  }

  const kpiSectionContent = kpiSectionMatch[1];

  // Remove kpi-section from its current position
  html = html.replace(kpiSectionContent, '');

  // Place it directly inside <section id="viewEquipamentos" class="view-section active">
  const targetTag = '<section id="viewEquipamentos" class="view-section active">';
  if (!html.includes(targetTag)) {
    console.error('Could not find targetTag in', filePath);
    return;
  }

  html = html.replace(targetTag, `${targetTag}\n\n      ${kpiSectionContent}\n`);

  fs.writeFileSync(filePath, html, 'utf8');
  console.log('Successfully moved KPI section inside viewEquipamentos in', filePath);
}

moveKpisInsideEquipamentos('index.html');
moveKpisInsideEquipamentos('gerenciador_enderecos.html');
