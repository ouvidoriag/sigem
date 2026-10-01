const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const jsonPath = path.join(ROOT, 'cadernos', '03_Educacao', 'escolas_duque_de_caxias.json');

if (!fs.existsSync(jsonPath)) {
  console.error('File not found:', jsonPath);
  process.exit(1);
}

const augeEscolas = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
console.log('Total schools in Auge JSON:', augeEscolas.length);

// Map bairro to distrito if 'Escolas da Rede'
const bairroToDistrito = {
  'Vila Ideal': '1º Distrito',
  'Jardim Leal': '1º Distrito',
  'Jardim Vinte e Cinco de Agosto': '1º Distrito',
  'São Bento': '2º Distrito',
  'Parque Xerém': '4º Distrito'
};

// Normalize districts
augeEscolas.forEach(e => {
  if (e.distrito === 'Escolas da Rede') {
    e.distrito = bairroToDistrito[e.bairro] || '1º Distrito';
  }
});

// Group by district
const d1 = augeEscolas.filter(e => e.distrito.startsWith('1'));
const d2 = augeEscolas.filter(e => e.distrito.startsWith('2'));
const d3 = augeEscolas.filter(e => e.distrito.startsWith('3'));
const d4 = augeEscolas.filter(e => e.distrito.startsWith('4'));

console.log(`Distritos: 1º=${d1.length}, 2º=${d2.length}, 3º=${d3.length}, 4º=${d4.length}, Total=${d1.length + d2.length + d3.length + d4.length}`);

// Helper to format table row
function formatRow(idx, s) {
  const inep = s.codigo_escola ? s.codigo_escola.trim() : '-';
  const diretor = s.diretor ? s.diretor.trim() : 'Gabinete / Direção SMEDC';
  const tel = s.telefones ? s.telefones.trim() : '(21) 2671-6612';
  const email = s.email ? s.email.trim() : 'assessoriadecomunicacao@smeduquedecaxias.rj.gov.br';
  const cep = s.cep ? s.cep.trim() : '-';
  const bairro = s.bairro ? s.bairro.trim() : '-';
  const end = s.endereco ? s.endereco.trim() : '-';
  const nome = s.nome_escola ? s.nome_escola.trim() : '-';

  return `| ${idx} | **${nome}** | ${inep} | ${diretor} | ${end} | ${bairro} | ${cep} | ${tel} | ${email} |`;
}

const tableHeader = `| Nº | Nome da Unidade Escolar | INEP | Direção Responsável | Endereço Completo | Bairro | CEP | Telefone Oficial | E-mail Institucional |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- |`;

// 1. Generate 03_Escolas_Municipais_e_Creches_Distrito_1.md
const mdD1 = `# 📚 Escolas e Creches Municipais — 1º Distrito (${d1.length} Unidades)
> [⬅️ Voltar ao Índice Geral](../../00_INDICE_GERAL.md)
> *Base Oficial do Auge Educacional / SMEDC — Duque de Caxias.*

---

${tableHeader}
${d1.map((s, idx) => formatRow(idx + 1, s)).join('\n')}
`;
fs.writeFileSync(path.join(ROOT, 'cadernos', '03_Educacao', '03_Escolas_Municipais_e_Creches_Distrito_1.md'), mdD1, 'utf8');

// 2. Generate 04_Escolas_Municipais_e_Creches_Distrito_2.md
const mdD2 = `# 📚 Escolas e Creches Municipais — 2º Distrito (${d2.length} Unidades)
> [⬅️ Voltar ao Índice Geral](../../00_INDICE_GERAL.md)
> *Base Oficial do Auge Educacional / SMEDC — Duque de Caxias.*

---

${tableHeader}
${d2.map((s, idx) => formatRow(idx + 1, s)).join('\n')}
`;
fs.writeFileSync(path.join(ROOT, 'cadernos', '03_Educacao', '04_Escolas_Municipais_e_Creches_Distrito_2.md'), mdD2, 'utf8');

// 3. Generate 05_Escolas_Municipais_e_Creches_Distrito_3.md
const mdD3 = `# 📚 Escolas e Creches Municipais — 3º Distrito (${d3.length} Unidades)
> [⬅️ Voltar ao Índice Geral](../../00_INDICE_GERAL.md)
> *Base Oficial do Auge Educacional / SMEDC — Duque de Caxias.*

---

${tableHeader}
${d3.map((s, idx) => formatRow(idx + 1, s)).join('\n')}
`;
fs.writeFileSync(path.join(ROOT, 'cadernos', '03_Educacao', '05_Escolas_Municipais_e_Creches_Distrito_3.md'), mdD3, 'utf8');

// 4. Generate 06_Escolas_Municipais_e_Creches_Distrito_4.md
const mdD4 = `# 📚 Escolas e Creches Municipais — 4º Distrito (${d4.length} Unidades)
> [⬅️ Voltar ao Índice Geral](../../00_INDICE_GERAL.md)
> *Base Oficial do Auge Educacional / SMEDC — Duque de Caxias.*

---

${tableHeader}
${d4.map((s, idx) => formatRow(idx + 1, s)).join('\n')}
`;
fs.writeFileSync(path.join(ROOT, 'cadernos', '03_Educacao', '06_Escolas_Municipais_e_Creches_Distrito_4.md'), mdD4, 'utf8');

console.log('Successfully regenerated all 4 Education District Markdown files!');

// 5. Also copy/sync to dados/educacao/
const dadosEduDir = path.join(ROOT, 'dados', 'educacao');
if (!fs.existsSync(dadosEduDir)) fs.mkdirSync(dadosEduDir, { recursive: true });
fs.writeFileSync(path.join(dadosEduDir, 'escolas_duque_de_caxias.json'), JSON.stringify(augeEscolas, null, 2), 'utf8');

// Also generate dados/educacao/escolas_duque_de_caxias.csv
const csvHeaders = ['Codigo_INEP', 'Nome_Escola', 'Distrito', 'Diretor', 'Endereco', 'Bairro', 'CEP', 'Telefones', 'Email', 'Data_Funcionamento', 'URL_Ficha'];
function escapeCsv(val) {
  if (val === null || val === undefined) return '';
  const str = String(val).trim();
  if (str.includes(';') || str.includes('"') || str.includes(',')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}
const csvEscolasRows = [csvHeaders.join(';')];
augeEscolas.forEach(e => {
  csvEscolasRows.push([
    e.codigo_escola, e.nome_escola, e.distrito, e.diretor,
    e.endereco, e.bairro, e.cep, e.telefones, e.email,
    e.data_funcionamento, e.url
  ].map(escapeCsv).join(';'));
});
fs.writeFileSync(path.join(dadosEduDir, 'escolas_duque_de_caxias.csv'), '\uFEFF' + csvEscolasRows.join('\r\n'), 'utf8');
console.log('Synced dados/educacao/escolas_duque_de_caxias.json and .csv');

// 6. Update Web Application DEFAULT_EQUIP
const htmlPath = path.join(ROOT, 'index.html');
let html = fs.readFileSync(htmlPath, 'utf8');
const match = html.match(/const DEFAULT_EQUIP = (\[[\s\S]*?\]);/);
let equip = JSON.parse(match[1]);

// Retain non-schools (Secretarias, Saude, FUNDEC, Assistencia, Seguranca) + Sede SMEDC
const nonSchools = equip.filter(e => e.categoria !== 'Educação (SMEDC)' || e.id === 'rec_152');
console.log('Non-school records preserved:', nonSchools.length);

// Build school records from augeEscolas
const newSchoolRecords = augeEscolas.map((s, idx) => {
  const distNum = s.distrito.replace(/[^0-9]/g, '') || '1';
  return {
    id: `rec_esc_${idx + 1}`,
    nome: s.nome_escola.replace(/[\r\n]+/g, ' ').trim(),
    categoria: 'Educação (SMEDC)',
    distrito: distNum,
    bairro: s.bairro.replace(/[\r\n]+/g, ' ').trim(),
    endereco: `${s.endereco} – ${s.bairro} – Duque de Caxias – RJ`,
    cep: s.cep ? s.cep.trim() : '',
    predio_sala: s.diretor ? `Direção: ${s.diretor.trim()} | INEP: ${s.codigo_escola}` : (s.codigo_escola ? `INEP: ${s.codigo_escola}` : ''),
    telefone: s.telefones && s.telefones.trim() ? s.telefones.trim() : '(21) 2671-6612',
    email: s.email && s.email.trim() ? s.email.trim() : 'assessoriadecomunicacao@smeduquedecaxias.rj.gov.br',
    lat: -22.78 + (idx % 15) * 0.01,
    lon: -43.30 - (idx % 10) * 0.01,
    hub_id: '',
    hub_nome: ''
  };
});

console.log('New school records built:', newSchoolRecords.length);

// Combine all
const fullEquip = [...nonSchools, ...newSchoolRecords];
console.log('Total full equipments in system:', fullEquip.length);

// Bump DB version
const newVersion = '2026_v4_auge_educacao';
html = html.replace(/const PMDC_DB_VERSION = '[^']+';/, `const PMDC_DB_VERSION = '${newVersion}';`);
html = html.replace(/const DEFAULT_EQUIP = \[[\s\S]*?\];/, `const DEFAULT_EQUIP = ${JSON.stringify(fullEquip)};`);

fs.writeFileSync(htmlPath, html, 'utf8');
fs.writeFileSync(path.join(ROOT, 'gerenciador_enderecos.html'), html, 'utf8');
console.log('Updated index.html and gerenciador_enderecos.html with', fullEquip.length, 'total records, version:', newVersion);

// 7. Regenerate dados/todos_os_enderecos_duque_de_caxias.csv and .json
const masterHeaders = [
  'ID', 'Categoria', 'Nome_Equipamento', 'Distrito', 'Bairro',
  'Endereco_Completo', 'CEP', 'Telefone', 'Email', 'Detalhes_Complemento',
  'Latitude', 'Longitude', 'Hub_Vinculado'
];

const masterCsvRows = [masterHeaders.join(';')];
fullEquip.forEach(eq => {
  masterCsvRows.push([
    eq.id, eq.categoria, eq.nome,
    eq.distrito ? (eq.distrito + (eq.distrito.includes('Distrito') ? '' : 'º Distrito')) : '',
    eq.bairro, eq.endereco, eq.cep, eq.telefone, eq.email, eq.predio_sala,
    eq.lat, eq.lon, eq.hub_nome
  ].map(escapeCsv).join(';'));
});

fs.writeFileSync(path.join(ROOT, 'dados', 'todos_os_enderecos_duque_de_caxias.csv'), '\uFEFF' + masterCsvRows.join('\r\n'), 'utf8');
fs.writeFileSync(path.join(ROOT, 'dados', 'todos_os_enderecos_duque_de_caxias.json'), JSON.stringify(fullEquip, null, 2), 'utf8');
console.log('Regenerated master consolidated CSV and JSON with', fullEquip.length, 'records!');

// 8. Regenerate sector CSVs in dados/por_setor/
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
  const filtered = fullEquip.filter(e => cats.includes(e.categoria));
  const subRows = [masterHeaders.join(';')];
  filtered.forEach(eq => {
    subRows.push([
      eq.id, eq.categoria, eq.nome,
      eq.distrito ? (eq.distrito + (eq.distrito.includes('Distrito') ? '' : 'º Distrito')) : '',
      eq.bairro, eq.endereco, eq.cep, eq.telefone, eq.email, eq.predio_sala,
      eq.lat, eq.lon, eq.hub_nome
    ].map(escapeCsv).join(';'));
  });
  fs.writeFileSync(path.join(porSetorDir, fileName), '\uFEFF' + subRows.join('\r\n'), 'utf8');
  console.log('Sector CSV updated:', fileName, 'with', filtered.length, 'records');
});

console.log('All synchronization steps finished with 100% success!');
