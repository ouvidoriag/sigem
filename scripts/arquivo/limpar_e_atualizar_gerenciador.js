const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const htmlPath = path.join(ROOT, 'index.html');
let html = fs.readFileSync(htmlPath, 'utf8');

const match = html.match(/const DEFAULT_EQUIP = (\[[\s\S]*?\]);/);
let equip = JSON.parse(match[1]);

console.log('Total equipments in app:', equip.length);

// 1. Clean all names, addresses, predio_sala, emails, phones
equip = equip.map(e => ({
  ...e,
  nome: (e.nome || '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim(),
  endereco: (e.endereco || '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim(),
  bairro: (e.bairro || '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim(),
  predio_sala: (e.predio_sala || '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim(),
  telefone: (e.telefone || '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim(),
  email: (e.email || '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim()
}));

const remaining = equip.filter(e => e.nome.includes('\n') || e.endereco.includes('\n'));
console.log('Remaining items with linebreaks:', remaining.length);

// 2. Bump DB version
const newVersion = '2026_v3_dados_limpos';
html = html.replace(/const PMDC_DB_VERSION = '[^']+';/, `const PMDC_DB_VERSION = '${newVersion}';`);

// 3. Update DEFAULT_EQUIP in HTML
html = html.replace(/const DEFAULT_EQUIP = \[[\s\S]*?\];/, `const DEFAULT_EQUIP = ${JSON.stringify(equip)};`);

fs.writeFileSync(htmlPath, html, 'utf8');
fs.writeFileSync(path.join(ROOT, 'gerenciador_enderecos.html'), html, 'utf8');
console.log('Updated index.html and gerenciador_enderecos.html with cleaned data and version', newVersion);

// 4. Update CSV and JSON in dados/
const headers = [
  'ID', 'Categoria', 'Nome_Equipamento', 'Distrito', 'Bairro',
  'Endereco_Completo', 'CEP', 'Telefone', 'Email', 'Detalhes_Complemento',
  'Latitude', 'Longitude', 'Hub_Vinculado'
];

function escapeCsv(val) {
  if (val === null || val === undefined) return '';
  const str = String(val).trim();
  if (str.includes(';') || str.includes('"') || str.includes(',')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}

const csvRows = [headers.join(';')];
equip.forEach(eq => {
  csvRows.push([
    eq.id, eq.categoria, eq.nome,
    eq.distrito ? (eq.distrito + (eq.distrito.includes('Distrito') ? '' : 'º Distrito')) : '',
    eq.bairro, eq.endereco, eq.cep, eq.telefone, eq.email, eq.predio_sala,
    eq.lat, eq.lon, eq.hub_nome
  ].map(escapeCsv).join(';'));
});

fs.writeFileSync(path.join(ROOT, 'dados', 'todos_os_enderecos_duque_de_caxias.csv'), '\uFEFF' + csvRows.join('\r\n'), 'utf8');
fs.writeFileSync(path.join(ROOT, 'dados', 'todos_os_enderecos_duque_de_caxias.json'), JSON.stringify(equip, null, 2), 'utf8');
console.log('Updated dados/todos_os_enderecos_duque_de_caxias.csv and .json');

// 5. Update dados/por_setor/
const porSetorDir = path.join(ROOT, 'dados', 'por_setor');
const categoriasMap = {
  '01_secretarias_e_orgaos.csv': ['Secretarias e Órgãos'],
  '02_saude_completa.csv': ['Saúde Especializada / Hospitalar', 'Saúde Básica (APS / USF / UBS)'],
  '03_educacao_smedc.csv': ['Educação (SMEDC)'],
  '04_fundec.csv': ['FUNDEC'],
  '05_assistencia_social.csv': ['Assistência Social (SEASDIH)'],
  '06_seguranca_subprefeituras_cultura.csv': ['Segurança, Subprefeituras e Cultura']
};

Object.entries(categoriasMap).forEach(([fileName, cats]) => {
  const filtered = equip.filter(e => cats.includes(e.categoria));
  const subRows = [headers.join(';')];
  filtered.forEach(eq => {
    subRows.push([
      eq.id, eq.categoria, eq.nome,
      eq.distrito ? (eq.distrito + (eq.distrito.includes('Distrito') ? '' : 'º Distrito')) : '',
      eq.bairro, eq.endereco, eq.cep, eq.telefone, eq.email, eq.predio_sala,
      eq.lat, eq.lon, eq.hub_nome
    ].map(escapeCsv).join(';'));
  });
  fs.writeFileSync(path.join(porSetorDir, fileName), '\uFEFF' + subRows.join('\r\n'), 'utf8');
});
console.log('Updated sector CSVs in dados/por_setor/');

// 6. Clean school markdown files in cadernos/03_Educacao/
const educacaoCadernosDir = path.join(ROOT, 'cadernos', '03_Educacao');
['03_Escolas_Municipais_e_Creches_Distrito_1.md',
 '04_Escolas_Municipais_e_Creches_Distrito_2.md',
 '05_Escolas_Municipais_e_Creches_Distrito_3.md',
 '06_Escolas_Municipais_e_Creches_Distrito_4.md'
].forEach(file => {
  const filePath = path.join(educacaoCadernosDir, file);
  if (!fs.existsSync(filePath)) return;
  let md = fs.readFileSync(filePath, 'utf8');
  
  // Fix broken linebreaks inside table cells
  // If a line doesn't start with |, append it to the previous line
  const lines = md.split('\n');
  const cleanLines = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim().startsWith('|') || line.trim().startsWith('#') || line.trim().startsWith('>') || line.trim() === '') {
      cleanLines.push(line);
    } else {
      // Continuation of previous table cell!
      if (cleanLines.length > 0 && cleanLines[cleanLines.length - 1].includes('|')) {
        cleanLines[cleanLines.length - 1] = cleanLines[cleanLines.length - 1].trim() + ' ' + line.trim();
      } else {
        cleanLines.push(line);
      }
    }
  }
  fs.writeFileSync(filePath, cleanLines.join('\n'), 'utf8');
  console.log('Cleaned table linebreaks in:', file);
});
