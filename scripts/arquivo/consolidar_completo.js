const fs = require('fs');
const path = require('path');

// 1. Sync cadernos/03_Educacao/escolas_duque_de_caxias.json with the mapped version
const dadosEscolas = fs.readFileSync('dados/educacao/escolas_duque_de_caxias.json', 'utf8');
fs.writeFileSync('cadernos/03_Educacao/escolas_duque_de_caxias.json', dadosEscolas, 'utf8');
console.log('Synchronized cadernos/03_Educacao/escolas_duque_de_caxias.json');

// 2. Load current database
const baseEquip = JSON.parse(fs.readFileSync('dados/todos_os_enderecos_duque_de_caxias.json', 'utf8'));
console.log('Current count:', baseEquip.length);

const additional = [
  {
    nome: 'Central do Cadastro Único (CadÚnico / Bolsa Família)',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: '25 de Agosto',
    endereco: 'Av. Brigadeiro Lima e Silva, 1.618 – 25 de Agosto – Duque de Caxias – RJ – CEP 25.071-182',
    cep: '25.071-182',
    predio_sala: 'Sede SMASDH',
    telefone: '(21) 2672-6659',
    email: 'gabinete.seasdih@duquedecaxias.rj.gov.br',
    lat: -22.7912,
    lon: -43.3015,
    hub_id: 'hub_12',
    hub_nome: 'Polo Cívico e Histórico da 25 de Agosto',
    servicos: 'Inscrição e atualização no Cadastro Único, Programa Bolsa Família, Tarifa Social, BPC'
  },
  {
    nome: 'Subsecretaria de Direitos Humanos',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: '25 de Agosto',
    endereco: 'Av. Brigadeiro Lima e Silva, 1.618 – 25 de Agosto – Duque de Caxias – RJ – CEP 25.071-182',
    cep: '25.071-182',
    predio_sala: 'Sede SMASDH',
    telefone: '(21) 2672-6650',
    email: 'direitoshumanos@duquedecaxias.rj.gov.br',
    lat: -22.7912,
    lon: -43.3015,
    hub_id: 'hub_12',
    hub_nome: 'Polo Cívico e Histórico da 25 de Agosto',
    servicos: 'Políticas de Direitos Humanos, Igualdade Racial, Defesa da Mulher e Minorias'
  },
  {
    nome: 'Central de Merenda e Logística Escolar (SMEDC)',
    categoria: 'Educação (SMEDC)',
    distrito: '2',
    bairro: 'Jardim Primavera',
    endereco: 'Avenida Primavera, 78 – Jardim Primavera – Duque de Caxias – RJ – CEP 25.215-255',
    cep: '25.215-255',
    predio_sala: '',
    telefone: '(21) 2772-7200',
    email: 'merenda@smeduquedecaxias.rj.gov.br',
    lat: -22.68515,
    lon: -43.28399,
    hub_id: 'hub_1',
    hub_nome: 'Centro Cívico / Paço Municipal (Prefeitura)',
    servicos: 'Armazenamento, controle nutricional e distribuição da merenda escolar da rede municipal'
  },
  {
    nome: 'Coordenação Pedagógica e Matrículas (SMEDC)',
    categoria: 'Educação (SMEDC)',
    distrito: '1',
    bairro: '25 de Agosto',
    endereco: 'Rua Prefeito José Carlos Lacerda, 1.424 – 25 de Agosto – Duque de Caxias – RJ – CEP 25.071-120',
    cep: '25.071-120',
    predio_sala: 'Sede Central SMEDC',
    telefone: '(21) 2671-6612',
    email: 'assessoriadecomunicacao@smeduquedecaxias.rj.gov.br',
    lat: -22.7918,
    lon: -43.3032,
    hub_id: 'hub_12',
    hub_nome: 'Polo Cívico e Histórico da 25 de Agosto',
    servicos: 'Gestão da rede de ensino, matrícula escolar e diretrizes curriculares'
  },
  {
    nome: 'Comissão de Seleção e PSS Educação (SMEDC)',
    categoria: 'Educação (SMEDC)',
    distrito: '1',
    bairro: '25 de Agosto',
    endereco: 'Rua Prefeito José Carlos Lacerda, 1.424 – 25 de Agosto – Duque de Caxias – RJ – CEP 25.071-120',
    cep: '25.071-120',
    predio_sala: 'Sede Central SMEDC',
    telefone: '(21) 2671-6612',
    email: 'assessoriagabinete@smeduquedecaxias.rj.gov.br',
    lat: -22.7918,
    lon: -43.3032,
    hub_id: 'hub_12',
    hub_nome: 'Polo Cívico e Histórico da 25 de Agosto',
    servicos: 'Processos seletivos simplificados e convocações da Secretaria de Educação'
  },
  {
    nome: 'Defesa Civil — Base Avançada 2º Distrito (Campos Elíseos)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '2',
    bairro: 'Campos Elíseos',
    endereco: 'Av. Actura, s/n – Campos Elíseos – Duque de Caxias – RJ',
    cep: '25225-015',
    predio_sala: '',
    telefone: '199 / (21) 2699-4207',
    email: 'defesacivil@duquedecaxias.rj.gov.br',
    lat: -22.7215,
    lon: -43.2752,
    hub_id: '',
    hub_nome: '',
    servicos: 'Monitoramento hidrológico, resposta rápida a alagamentos e emergências do 2º Distrito'
  },
  {
    nome: 'Defesa Civil — Base Avançada 3º Distrito (Imbariê)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '3',
    bairro: 'Imbariê',
    endereco: 'Av. Automóvel Clube, s/n – Imbariê – Duque de Caxias – RJ',
    cep: '25266-000',
    predio_sala: '',
    telefone: '199 / (21) 2699-4207',
    email: 'defesacivil@duquedecaxias.rj.gov.br',
    lat: -22.6455,
    lon: -43.2505,
    hub_id: '',
    hub_nome: '',
    servicos: 'Apoio operacional, vistorias técnicas e alerta de enchentes no 3º Distrito'
  },
  {
    nome: 'Defesa Civil — Base Avançada 4º Distrito (Xerém)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '4',
    bairro: 'Xerém',
    endereco: 'Estrada Rio D\'Ouro, s/n – Xerém – Duque de Caxias – RJ',
    cep: '25272-000',
    predio_sala: '',
    telefone: '199 / (21) 2699-4207',
    email: 'defesacivil@duquedecaxias.rj.gov.br',
    lat: -22.5842,
    lon: -43.3102,
    hub_id: '',
    hub_nome: '',
    servicos: 'Monitoramento geológico de encostas, deslizamentos e contingência da Serra de Petrópolis'
  },
  {
    nome: 'Polo Operacional SMOAG Centro (1º Distrito)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '1',
    bairro: 'Centenário',
    endereco: 'Rua Dr. Manoel Reis, s/n – Centenário – Duque de Caxias – RJ',
    cep: '25030-240',
    predio_sala: '',
    telefone: '(21) 2772-7200',
    email: 'obraspmdc@gmail.com',
    lat: -22.782,
    lon: -43.312,
    hub_id: '',
    hub_nome: '',
    servicos: 'Equipes de obras, drenagem pluvial, pavimentação e iluminação no 1º Distrito'
  },
  {
    nome: 'Polo Operacional SMOAG Campos Elíseos (2º Distrito)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '2',
    bairro: 'Campos Elíseos',
    endereco: 'Av. Actura, s/n – Campos Elíseos – Duque de Caxias – RJ',
    cep: '25225-015',
    predio_sala: '',
    telefone: '(21) 2772-7200',
    email: 'obraspmdc@gmail.com',
    lat: -22.7215,
    lon: -43.2752,
    hub_id: '',
    hub_nome: '',
    servicos: 'Manutenção viária, desobstrução de canais e serviços urbanos no 2º Distrito'
  },
  {
    nome: 'Polo Operacional SMOAG Imbariê (3º Distrito)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '3',
    bairro: 'Imbariê',
    endereco: 'Av. Automóvel Clube, s/n – Imbariê – Duque de Caxias – RJ',
    cep: '25266-000',
    predio_sala: '',
    telefone: '(21) 2772-7200',
    email: 'obraspmdc@gmail.com',
    lat: -22.6455,
    lon: -43.2505,
    hub_id: '',
    hub_nome: '',
    servicos: 'Operação de maquinário pesado, terraplanagem e conservação de vias no 3º Distrito'
  },
  {
    nome: 'Polo Operacional SMOAG Xerém (4º Distrito)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '4',
    bairro: 'Xerém',
    endereco: 'Estrada Rio D\'Ouro, s/n – Xerém – Duque de Caxias – RJ',
    cep: '25272-000',
    predio_sala: '',
    telefone: '(21) 2679-1837',
    email: 'obraspmdc@gmail.com',
    lat: -22.5842,
    lon: -43.3102,
    hub_id: '',
    hub_nome: '',
    servicos: 'Contenção de encostas, dragagem de rios e conservação viária no 4º Distrito'
  },
  {
    nome: 'Usina de Asfalto Municipal (SMOAG)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '2',
    bairro: 'Jardim Primavera',
    endereco: 'Rodovia Washington Luiz, km 112 – Jardim Primavera – Duque de Caxias – RJ',
    cep: '25215-260',
    predio_sala: '',
    telefone: '(21) 2773-5500',
    email: 'obraspmdc@gmail.com',
    lat: -22.684,
    lon: -43.282,
    hub_id: '',
    hub_nome: '',
    servicos: 'Produção contínua de massa asfáltica e recapeamento da malha viária municipal'
  },
  {
    nome: 'Posto Avançado SINE — Shopping Center Caxias',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '1',
    bairro: 'Centro',
    endereco: 'Rua Mariano Sendra dos Santos, s/n – Centro – Duque de Caxias – RJ – CEP 25.010-080',
    cep: '25.010-080',
    predio_sala: '',
    telefone: '(21) 2672-7200',
    email: 'smter.gabinete@duquedecaxias.rj.gov.br',
    lat: -22.7865,
    lon: -43.308,
    hub_id: '',
    hub_nome: '',
    servicos: 'Intermediação pública de mão de obra, emissão de CTPS digital e balcão de empregos'
  },
  {
    nome: 'Polo de Qualificação Profissional Santa Cruz (SMTER)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '3',
    bairro: 'Santa Cruz da Serra',
    endereco: 'Av. Automóvel Clube, s/n – Santa Cruz da Serra – Duque de Caxias – RJ – CEP 25.260-000',
    cep: '25.260-000',
    predio_sala: '',
    telefone: '(21) 2772-7200',
    email: 'smter.gabinete@duquedecaxias.rj.gov.br',
    lat: -22.662,
    lon: -43.268,
    hub_id: '',
    hub_nome: '',
    servicos: 'Cursos gratuitos de capacitação profissional e inscrições para vagas de trabalho'
  },
  {
    nome: 'Base do Castramóvel Municipal (SMPA)',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '1',
    bairro: 'Itinerante (Todos os Distritos)',
    endereco: 'Unidade Móvel Distrital – Duque de Caxias – RJ',
    cep: '25000-000',
    predio_sala: '',
    telefone: '(21) 2773-5500',
    email: 'smpa@duquedecaxias.rj.gov.br',
    lat: -22.785,
    lon: -43.305,
    hub_id: '',
    hub_nome: '',
    servicos: 'Castrações gratuitas itinerantes de cães e gatos em comunidades e praças públicas'
  }
];

let maxId = 0;
baseEquip.forEach(e => {
  const m = e.id && e.id.match(/^rec_(\d+)$/);
  if (m) {
    const v = parseInt(m[1], 10);
    if (v > maxId) maxId = v;
  }
});

additional.forEach((item) => {
  maxId++;
  item.id = 'rec_' + maxId;
  baseEquip.push(item);
});

console.log('Total consolidated equipment:', baseEquip.length);

// Save dados/todos_os_enderecos_duque_de_caxias.json
fs.writeFileSync('dados/todos_os_enderecos_duque_de_caxias.json', JSON.stringify(baseEquip, null, 2), 'utf8');

// Generate master CSV
const csvHeaders = ['id', 'nome', 'categoria', 'distrito', 'bairro', 'endereco', 'cep', 'predio_sala', 'telefone', 'email', 'lat', 'lon', 'hub_id', 'hub_nome', 'servicos'];
const csvRows = [csvHeaders.join(';')];
baseEquip.forEach(item => {
  const row = csvHeaders.map(h => {
    let val = item[h] || '';
    if (typeof val === 'string') {
      val = val.replace(/"/g, '""').replace(/\r?\n/g, ' ');
      if (val.includes(';') || val.includes('"') || val.includes(',')) {
        val = `"${val}"`;
      }
    }
    return val;
  });
  csvRows.push(row.join(';'));
});
fs.writeFileSync('dados/todos_os_enderecos_duque_de_caxias.csv', '\uFEFF' + csvRows.join('\r\n'), 'utf8');

// Update sector CSVs
const sectorFiles = {
  'Secretarias e Órgãos': 'dados/por_setor/01_secretarias_e_orgaos.csv',
  'Saúde Especializada / Hospitalar': 'dados/por_setor/02_saude_completa.csv',
  'Saúde Básica (APS / USF / UBS)': 'dados/por_setor/02_saude_completa.csv',
  'Educação (SMEDC)': 'dados/por_setor/03_educacao_smedc.csv',
  'FUNDEC': 'dados/por_setor/04_fundec.csv',
  'Assistência Social (SEASDIH)': 'dados/por_setor/05_assistencia_social.csv',
  'Segurança, Subprefeituras e Cultura': 'dados/por_setor/06_seguranca_subprefeituras_cultura.csv'
};

const sectorData = {};
baseEquip.forEach(item => {
  const target = sectorFiles[item.categoria];
  if (target) {
    if (!sectorData[target]) sectorData[target] = [];
    sectorData[target].push(item);
  }
});

for (const [filePath, items] of Object.entries(sectorData)) {
  const rows = [csvHeaders.join(';')];
  items.forEach(item => {
    const row = csvHeaders.map(h => {
      let val = item[h] || '';
      if (typeof val === 'string') {
        val = val.replace(/"/g, '""').replace(/\r?\n/g, ' ');
        if (val.includes(';') || val.includes('"') || val.includes(',')) {
          val = `"${val}"`;
        }
      }
      return val;
    });
    rows.push(row.join(';'));
  });
  fs.writeFileSync(filePath, '\uFEFF' + rows.join('\r\n'), 'utf8');
}
console.log('Saved sector CSVs');

// Update index.html and gerenciador_enderecos.html
let indexHtml = fs.readFileSync('index.html', 'utf8');

// Replace PMDC_DB_VERSION
indexHtml = indexHtml.replace(/const PMDC_DB_VERSION = '.*?';/, "const PMDC_DB_VERSION = '2026_v5_full_consolidation';");

// Replace DEFAULT_EQUIP
const startIdx = indexHtml.indexOf('const DEFAULT_EQUIP = ');
const scriptRest = indexHtml.substring(startIdx + 'const DEFAULT_EQUIP = '.length);
let depth = 0, jsonEnd = -1;
for (let i = 0; i < scriptRest.length; i++) {
  if (scriptRest[i] === '[') depth++;
  else if (scriptRest[i] === ']') { depth--; if (depth === 0) { jsonEnd = i + 1; break; } }
}
const before = indexHtml.substring(0, startIdx + 'const DEFAULT_EQUIP = '.length);
const after = scriptRest.substring(jsonEnd);
indexHtml = before + JSON.stringify(baseEquip) + after;

// Write both files
fs.writeFileSync('index.html', indexHtml, 'utf8');
fs.writeFileSync('gerenciador_enderecos.html', indexHtml, 'utf8');
console.log('Updated index.html and gerenciador_enderecos.html successfully!');
