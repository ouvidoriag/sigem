const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const htmlPath = path.join(ROOT, 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const match = html.match(/const DEFAULT_EQUIP = (\[[\s\S]*?\]);/);
if (!match) {
  console.error('Could not find DEFAULT_EQUIP');
  process.exit(1);
}

let equip = JSON.parse(match[1]);
console.log('Total equipments in app:', equip.length);

// Try loading auge schools for enrichment
const augePath = path.join(ROOT, 'dados', 'educacao', 'escolas_duque_de_caxias.json');
let auge = [];
if (fs.existsSync(augePath)) {
  auge = JSON.parse(fs.readFileSync(augePath, 'utf8'));
}

function norm(s) {
  return (s || '').toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, ' ')
    .replace(/\b(escola|municipal|creche|pre|esc|ciep|brizolao|municipalizado|comunitaria|ccaic|unidade|de|da|do|dos|das|e|prof|profa|professor|professora|vereador|ver|doutor|dr|dra|ee|em)\b/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

let enrichedSchools = 0;
equip = equip.map(eq => {
  if (eq.categoria === 'Educação (SMEDC)' && eq.id !== 'rec_152') {
    const nEq = norm(eq.nome);
    const found = auge.find(a => {
      const nAu = norm(a.nome_escola);
      if (!nEq || !nAu) return false;
      if (nEq === nAu) return true;
      if (nEq.length > 4 && nAu.length > 4) {
        if (nEq.includes(nAu) || nAu.includes(nEq)) return true;
      }
      return false;
    });
    if (found) {
      enrichedSchools++;
      return {
        ...eq,
        email: (found.email && found.email.trim()) ? found.email.trim() : eq.email,
        telefone: (found.telefones && found.telefones.trim()) ? found.telefones.trim() : eq.telefone,
        predio_sala: found.diretor ? ('Direção: ' + found.diretor + (found.codigo_escola ? ' | INEP: ' + found.codigo_escola : '')) : eq.predio_sala
      };
    }
  }
  return eq;
});

console.log('Enriched schools:', enrichedSchools);

const headers = [
  'ID',
  'Categoria',
  'Nome_Equipamento',
  'Distrito',
  'Bairro',
  'Endereco_Completo',
  'CEP',
  'Telefone',
  'Email',
  'Detalhes_Complemento',
  'Latitude',
  'Longitude',
  'Hub_Vinculado'
];

function escapeCsv(val) {
  if (val === null || val === undefined) return '';
  const str = String(val).replace(/[\r\n]+/g, ' ').trim();
  if (str.includes(';') || str.includes('"') || str.includes(',')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}

const csvRows = [headers.join(';')];
equip.forEach(eq => {
  const row = [
    eq.id,
    eq.categoria,
    eq.nome,
    eq.distrito ? (eq.distrito + (eq.distrito.includes('Distrito') ? '' : 'º Distrito')) : '',
    eq.bairro,
    eq.endereco,
    eq.cep,
    eq.telefone,
    eq.email,
    eq.predio_sala,
    eq.lat,
    eq.lon,
    eq.hub_nome
  ].map(escapeCsv);
  csvRows.push(row.join(';'));
});

// UTF-8 BOM for Excel
const csvContent = '\uFEFF' + csvRows.join('\r\n');

// Write to dados/
const dadosDir = path.join(ROOT, 'dados');
fs.writeFileSync(path.join(dadosDir, 'todos_os_enderecos_duque_de_caxias.csv'), csvContent, 'utf8');
fs.writeFileSync(path.join(dadosDir, 'todos_os_enderecos_duque_de_caxias.json'), JSON.stringify(equip, null, 2), 'utf8');

console.log('Successfully wrote dados/todos_os_enderecos_duque_de_caxias.csv with', csvRows.length - 1, 'records!');
console.log('Successfully wrote dados/todos_os_enderecos_duque_de_caxias.json with', equip.length, 'records!');

// Also update index.html & gerenciador_enderecos.html
const updatedJsonStr = JSON.stringify(equip);
let updatedHtml = html.replace(/const DEFAULT_EQUIP = \[[\s\S]*?\];/, 'const DEFAULT_EQUIP = ' + updatedJsonStr + ';');
fs.writeFileSync(htmlPath, updatedHtml, 'utf8');
fs.writeFileSync(path.join(ROOT, 'gerenciador_enderecos.html'), updatedHtml, 'utf8');
console.log('Updated index.html and gerenciador_enderecos.html with enriched data!');

// Create dados/por_setor/
const porSetorDir = path.join(dadosDir, 'por_setor');
if (!fs.existsSync(porSetorDir)) fs.mkdirSync(porSetorDir, { recursive: true });

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
  console.log('Created sector CSV:', fileName, 'with', filtered.length, 'records');
});

// Remove obsolete folders
function rmDir(dir) {
  if (fs.existsSync(dir)) {
    fs.readdirSync(dir).forEach(f => {
      const p = path.join(dir, f);
      if (fs.statSync(p).isDirectory()) rmDir(p);
      else fs.unlinkSync(p);
    });
    fs.rmdirSync(dir);
  }
}

rmDir(path.join(dadosDir, 'consolidado'));
rmDir(path.join(dadosDir, 'secretarias'));
console.log('Removed obsolete subfolders dados/consolidado and dados/secretarias');
