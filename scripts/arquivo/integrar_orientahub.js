const fs = require('fs');
const path = require('path');

// 1. Load current database (426)
const ourEquips = JSON.parse(fs.readFileSync('dados/todos_os_enderecos_duque_de_caxias.json', 'utf8'));
const orientaUnits = JSON.parse(fs.readFileSync('scripts/orientahub_units.json', 'utf8'));

console.log('Current equips:', ourEquips.length);
console.log('Orienta units:', orientaUnits.length);

function norm(s) {
  return (s || '').toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// Map coordinates for districts / neighborhoods
const coordMap = {
  'Jardim Primavera': { lat: -22.6852, lon: -43.2840, dist: '2' },
  'Centro': { lat: -22.7850, lon: -43.3080, dist: '1' },
  'Centenário': { lat: -22.7820, lon: -43.3120, dist: '1' },
  '25 de Agosto': { lat: -22.7915, lon: -43.3035, dist: '1' },
  'Figueira': { lat: -22.7350, lon: -43.2850, dist: '2' },
  'Capivari': { lat: -22.6950, lon: -43.2550, dist: '2' },
  'Imbariê': { lat: -22.6455, lon: -43.2505, dist: '3' },
  'Saracuruna': { lat: -22.6780, lon: -43.2420, dist: '2' }
};

// 2. The 16 new units from OrientaHub
const newUnitsFromOrienta = [
  {
    id_orig: 'abrigo-primeiro-olhar',
    nome: 'Abrigo Primeiro Olhar',
    sigla: 'Abrigo',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '2',
    bairro: 'Jardim Primavera',
    endereco: 'Av. Perimetral Tarce Menezes Freitas Lima, 19 – Jardim Primavera – Duque de Caxias – RJ – CEP 25.215-000',
    cep: '25.215-000',
    predio_sala: '',
    telefone: '(21) 2773-5500',
    email: 'gabinete.seasdih@duquedecaxias.rj.gov.br',
    lat: -22.6865,
    lon: -43.2835,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Atendimento 24 Horas',
    servicos: 'Unidade de alta complexidade do SUAS para acolhimento protetivo e temporário de bebês e crianças sob medida judicial de proteção.',
    descricao: 'Acolhimento protetivo e temporário de crianças sob tutela e determinação judicial.'
  },
  {
    id_orig: 'casa-de-passagem',
    nome: 'Casa de Passagem Municipal',
    sigla: 'Casa Passagem',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centenário',
    endereco: 'Rua Manoel Vieira, s/nº – Centenário – Duque de Caxias – RJ – CEP 25.030-220',
    cep: '25.030-220',
    predio_sala: '',
    telefone: '(21) 2771-8021',
    email: 'gabinete.seasdih@duquedecaxias.rj.gov.br',
    lat: -22.7815,
    lon: -43.3125,
    hub_id: 'hub_7',
    hub_nome: 'Polo de Assistência Social do Centenário',
    horario_funcionamento: 'Atendimento 24 Horas',
    servicos: 'Acolhimento emergencial temporário, pernoite, alimentação e apoio psicossocial para pessoas em situação de rua.',
    descricao: 'Unidade protetiva de acolhimento emergencial temporário para pessoas em trânsito e vulnerabilidade extrema em Duque de Caxias.'
  },
  {
    id_orig: 'casa-social-renascer',
    nome: 'Casa Social Renascer',
    sigla: 'Casa Renascer',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centro',
    endereco: 'Rua Coronel João Teles, 43 – Centro – Duque de Caxias – RJ – CEP 25.010-060',
    cep: '25.010-060',
    predio_sala: '',
    telefone: '(21) 2676-9600',
    email: 'gabinete.seasdih@duquedecaxias.rj.gov.br',
    lat: -22.7880,
    lon: -43.3050,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Alta complexidade, convivência e suporte para reinserção cidadã de adultos em vulnerabilidade.',
    descricao: 'Atuação na rede de proteção de alta complexidade para inserção cidadã de pessoas sob vulnerabilidade severa.'
  },
  {
    id_orig: 'casa-social-reviver',
    nome: 'Casa Social Reviver',
    sigla: 'Casa Reviver',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centro',
    endereco: 'Rua Manoel Teles, 700 – Centro – Duque de Caxias – RJ – CEP 25.010-180',
    cep: '25.010-180',
    predio_sala: '',
    telefone: '(21) 2671-8055',
    email: 'gabinete.seasdih@duquedecaxias.rj.gov.br',
    lat: -22.7860,
    lon: -43.3070,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Acolhimento institucional, suporte psicossocial e reinserção comunitária.',
    descricao: 'Acolhimento e suporte psicossocial focado na reabilitação e reinserção social de cidadãos em extrema vulnerabilidade.'
  },
  {
    id_orig: 'casa-comunitaria',
    nome: 'Casa Comunitária 25 de Agosto',
    sigla: 'Casa Comun.',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: '25 de Agosto',
    endereco: 'Rua Conde de Porto Alegre, 599 – 25 de Agosto – Duque de Caxias – RJ – CEP 25.070-350',
    cep: '25.070-350',
    predio_sala: '',
    telefone: '(21) 2783-1306',
    email: 'gabinete.seasdih@duquedecaxias.rj.gov.br',
    lat: -22.7930,
    lon: -43.3040,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Articulação de grupos comunitários, oficinas de convivência e fortalecimento de vínculos.',
    descricao: 'Espaço integrador comunitário focado em articular grupos sociais e cidadania no bairro 25 de Agosto.'
  },
  {
    id_orig: 'centro-pop',
    nome: 'Centro POP — Unidade Figueira',
    sigla: 'Centro POP',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '2',
    bairro: 'Figueira',
    endereco: 'Estrada Velha do Pilar, s/nº – Figueira – Duque de Caxias – RJ – CEP 25.230-020',
    cep: '25.230-020',
    predio_sala: '',
    telefone: '(21) 2771-0976',
    email: 'centropop@duquedecaxias.rj.gov.br',
    lat: -22.7355,
    lon: -43.2845,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Centro de Referência Especializado para População em Situação de Rua, higiene, alimentação e encaminhamento.',
    descricao: 'Atendimento especializado e continuado a pessoas em situação de rua com equipe multidisciplinar.'
  },
  {
    id_orig: 'cmdca',
    nome: 'CMDCA — Conselho Municipal dos Direitos da Criança e do Adolescente',
    sigla: 'CMDCA',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centenário',
    endereco: 'Rua Manoel Vieira, s/nº – Centenário – Duque de Caxias – RJ – CEP 25.030-220',
    cep: '25.030-220',
    predio_sala: 'Complexo de Assistência Social',
    telefone: '(21) 3652-5461',
    email: 'cmdca@duquedecaxias.rj.gov.br',
    lat: -22.7820,
    lon: -43.3120,
    hub_id: 'hub_7',
    hub_nome: 'Polo de Assistência Social do Centenário',
    horario_funcionamento: 'Segunda a sexta-feira, das 9h às 17h',
    servicos: 'Formulação, controle e deliberação das políticas públicas municipais para crianças e adolescentes.',
    descricao: 'Órgão deliberativo e controlador das ações de defesa dos direitos de crianças e jovens em Duque de Caxias.'
  },
  {
    id_orig: 'conselho-do-idoso',
    nome: 'COMDEPI — Conselho Municipal de Defesa dos Direitos da Pessoa Idosa',
    sigla: 'COMDEPI',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centenário',
    endereco: 'Rua Manoel Vieira, s/nº – Centenário – Duque de Caxias – RJ – CEP 25.030-220',
    cep: '25.030-220',
    predio_sala: 'Complexo de Assistência Social',
    telefone: '(21) 2672-6650',
    email: 'conselhoidoso@duquedecaxias.rj.gov.br',
    lat: -22.7820,
    lon: -43.3120,
    hub_id: 'hub_7',
    hub_nome: 'Polo de Assistência Social do Centenário',
    horario_funcionamento: 'Segunda a sexta-feira, das 9h às 17h',
    servicos: 'Fiscalização e proposição de políticas de valorização, saúde e dignidade para a terceira idade.',
    descricao: 'Conselho paritário dedicado à proteção e promoção dos direitos da população idosa do município.'
  },
  {
    id_orig: 'conselho-da-mulher',
    nome: 'COMDIM — Conselho Municipal dos Direitos da Mulher',
    sigla: 'COMDIM',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centenário',
    endereco: 'Rua Manoel Vieira, s/nº – Centenário – Duque de Caxias – RJ – CEP 25.030-220',
    cep: '25.030-220',
    predio_sala: 'Complexo de Assistência Social',
    telefone: '(21) 2672-6650',
    email: 'conselhomulher@duquedecaxias.rj.gov.br',
    lat: -22.7820,
    lon: -43.3120,
    hub_id: 'hub_7',
    hub_nome: 'Polo de Assistência Social do Centenário',
    horario_funcionamento: 'Segunda a sexta-feira, das 9h às 17h',
    servicos: 'Políticas de igualdade de gênero, enfrentamento à violência doméstica e combate à discriminação.',
    descricao: 'Instância de articulação e defesa dos direitos das mulheres caxienses.'
  },
  {
    id_orig: 'dedaf',
    nome: 'DEDAF — Departamento de Defesa dos Direitos da Mulher e da Família',
    sigla: 'DEDAF',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centro',
    endereco: 'Rua Frei Fidélis, 709 – Centro – Duque de Caxias – RJ – CEP 25.010-150',
    cep: '25.010-150',
    predio_sala: '',
    telefone: '(21) 2672-6650',
    email: 'direitoshumanos@duquedecaxias.rj.gov.br',
    lat: -22.7875,
    lon: -43.3075,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 9h às 17h',
    servicos: 'Atendimento especializado, suporte jurídico e psicossocial para famílias e mulheres.',
    descricao: 'Departamento vinculado à Subsecretaria de Direitos Humanos focado na estrutura familiar e apoio à mulher.'
  },
  {
    id_orig: 'lgbt-demppird',
    nome: 'DEMPPIRD — Depto. de Promoção da Igualdade Racial e Direitos LGBT',
    sigla: 'DEMPPIRD',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centro',
    endereco: 'Rua Frei Fidélis, 709 – Centro – Duque de Caxias – RJ – CEP 25.010-150',
    cep: '25.010-150',
    predio_sala: '',
    telefone: '(21) 2672-6650',
    email: 'direitoshumanos@duquedecaxias.rj.gov.br',
    lat: -22.7875,
    lon: -43.3075,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 9h às 17h',
    servicos: 'Combate à discriminação, políticas afirmativas e atendimento a vítimas de intolerância e preconceito.',
    descricao: 'Órgão de execução das políticas municipais antidiscriminação racial e diversidade sexual.'
  },
  {
    id_orig: 'equinovida',
    nome: 'Equinovida — Centro Municipal de Equoterapia',
    sigla: 'Equinovida',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '2',
    bairro: 'Jardim Primavera',
    endereco: 'Rua Maurício Santos Silva, 2846 – Jardim Primavera – Duque de Caxias – RJ – CEP 25.215-400',
    cep: '25.215-400',
    predio_sala: '',
    telefone: '(21) 3653-6731',
    email: 'equinovida@duquedecaxias.rj.gov.br',
    lat: -22.6820,
    lon: -43.2860,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Método terapêutico com cavalos para reabilitação biopsicossocial de pessoas com deficiência.',
    descricao: 'Centro de referência em tratamento terapêutico de crianças e jovens com deficiência ou TEA por equoterapia.'
  },
  {
    id_orig: 'getsemani',
    nome: 'Getsêmani — Centro Comunitário de Acolhimento',
    sigla: 'Getsêmani',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '2',
    bairro: 'Capivari',
    endereco: 'Rua Marquês de Barcena, 88 – Capivari – Duque de Caxias – RJ – CEP 25.220-100',
    cep: '25.220-100',
    predio_sala: '',
    telefone: '(21) 2773-9777',
    email: 'gabinete.seasdih@duquedecaxias.rj.gov.br',
    lat: -22.6955,
    lon: -43.2555,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Acolhimento comunitário, assistência a famílias em vulnerabilidade e projetos de cidadania.',
    descricao: 'Equipamento de suporte social integrado à rede do 2º Distrito.'
  },
  {
    id_orig: 'detran-imbarie',
    nome: 'Posto de Identificação Civil DETRAN — Imbariê',
    sigla: 'DETRAN Imbariê',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '3',
    bairro: 'Imbariê',
    endereco: 'Rua Ipameri, s/nº – Imbariê – Duque de Caxias – RJ – CEP 25.266-000',
    cep: '25.266-000',
    predio_sala: 'Subprefeitura / Polo de Serviços',
    telefone: '(21) 3460-4040',
    email: 'detran@duquedecaxias.rj.gov.br',
    lat: -22.6455,
    lon: -43.2505,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Emissão de Carteira de Identidade (RG), 2ª via e identificação civil descentralizada.',
    descricao: 'Posto avançado de atendimento do DETRAN RJ em Imbariê para serviços de identificação civil descentralizados.'
  },
  {
    id_orig: 'detran-saracuruna',
    nome: 'Posto de Identificação Civil DETRAN — Saracuruna',
    sigla: 'DETRAN Saracuruna',
    categoria: 'Segurança, Subprefeituras e Cultura',
    distrito: '2',
    bairro: 'Saracuruna',
    endereco: 'Rua Nascimento e Silva, 4, Lote 15 – Saracuruna – Duque de Caxias – RJ – CEP 25.212-000',
    cep: '25.212-000',
    predio_sala: '',
    telefone: '(21) 3460-4040',
    email: 'detran@duquedecaxias.rj.gov.br',
    lat: -22.6780,
    lon: -43.2420,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    servicos: 'Emissão de documento de identidade civil (RG) e certidões para moradores do 2º Distrito.',
    descricao: 'Posto de atendimento descentralizado do DETRAN RJ em Saracuruna para atendimento e suporte à cidadania local.'
  },
  {
    id_orig: 'ubs-centro',
    nome: 'UBS Centro — Unidade Básica de Saúde',
    sigla: 'UBS Centro',
    categoria: 'Saúde Básica (APS / USF / UBS)',
    distrito: '1',
    bairro: 'Centro',
    endereco: 'Rua Conde de Porto Alegre, 123 – Centro – Duque de Caxias – RJ – CEP 25.070-350',
    cep: '25.070-350',
    predio_sala: '',
    telefone: '(21) 2772-7200',
    email: 'smsdc@duquedecaxias.rj.gov.br',
    lat: -22.7870,
    lon: -43.3060,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 08h às 17h',
    servicos: 'Consultas médicas de clínica geral, vacinação de rotina, curativos, enfermagem e pré-natal.',
    descricao: 'Unidade Básica de Saúde da Atenção Primária para atendimento comunitário na região central.'
  }
];

// 3. Enrich existing records with OrientaHub data
let enrichedCount = 0;
const orientaMap = new Map();
orientaUnits.forEach(u => {
  orientaMap.set(norm(u.name), u);
});

ourEquips.forEach(e => {
  // Try to find in orienta
  let matched = orientaMap.get(norm(e.nome));
  if (!matched) {
    // try partial
    for (const [nName, u] of orientaMap.entries()) {
      if (norm(e.nome).includes(nName) || nName.includes(norm(e.nome))) {
        matched = u;
        break;
      }
    }
  }

  if (matched) {
    enrichedCount++;
    if (matched.hours && !e.horario_funcionamento) {
      e.horario_funcionamento = matched.hours;
    }
    if (matched.description && !e.descricao) {
      e.descricao = matched.description;
    }
    if (matched.acronym && !e.sigla) {
      e.sigla = matched.acronym;
    }
    // Update specific CEP if our is generic
    if (e.cep === '25000-000' && matched.zip_code && matched.zip_code !== '25000-000') {
      e.cep = matched.zip_code;
    }
  }

  // Ensure every item has reasonable default horario_funcionamento and descricao if not set
  if (!e.horario_funcionamento) {
    if (e.categoria.includes('Educação') || e.categoria.includes('FUNDEC')) {
      e.horario_funcionamento = 'Segunda a sexta-feira, das 07h às 21h (Conforme Turno)';
    } else if (e.nome.includes('UPA') || e.nome.includes('Hospital') || e.nome.includes('Maternidade') || e.nome.includes('24h')) {
      e.horario_funcionamento = 'Atendimento 24 Horas Ininterrupto';
    } else if (e.categoria.includes('Saúde Básica')) {
      e.horario_funcionamento = 'Segunda a sexta-feira, das 08h às 17h';
    } else {
      e.horario_funcionamento = 'Segunda a sexta-feira, das 09h às 17h';
    }
  }

  if (!e.descricao) {
    e.descricao = e.servicos || `Equipamento público oficial da Prefeitura Municipal de Duque de Caxias vinculado ao setor de ${e.categoria}.`;
  }
});

console.log(`Enriched ${enrichedCount} existing equipment with OrientaHub data!`);

// 4. Append the 16 new units
let maxId = 0;
ourEquips.forEach(e => {
  const m = e.id && e.id.match(/^rec_(\d+)$/);
  if (m) {
    const v = parseInt(m[1], 10);
    if (v > maxId) maxId = v;
  }
});

newUnitsFromOrienta.forEach(nu => {
  maxId++;
  const fullItem = {
    id: 'rec_' + maxId,
    nome: nu.nome,
    sigla: nu.sigla,
    categoria: nu.categoria,
    distrito: nu.distrito,
    bairro: nu.bairro,
    endereco: nu.endereco,
    cep: nu.cep,
    predio_sala: nu.predio_sala,
    telefone: nu.telefone,
    email: nu.email,
    lat: nu.lat,
    lon: nu.lon,
    hub_id: nu.hub_id,
    hub_nome: nu.hub_nome,
    horario_funcionamento: nu.horario_funcionamento,
    servicos: nu.servicos,
    descricao: nu.descricao
  };
  ourEquips.push(fullItem);
});

console.log('Total consolidated records now:', ourEquips.length);

// 5. Save master JSON
fs.writeFileSync('dados/todos_os_enderecos_duque_de_caxias.json', JSON.stringify(ourEquips, null, 2), 'utf8');
console.log('Saved dados/todos_os_enderecos_duque_de_caxias.json');

// 6. Save master CSV
const csvHeaders = [
  'id', 'nome', 'sigla', 'categoria', 'distrito', 'bairro', 'endereco', 'cep',
  'predio_sala', 'telefone', 'email', 'horario_funcionamento', 'lat', 'lon',
  'hub_id', 'hub_nome', 'servicos', 'descricao'
];

const csvRows = [csvHeaders.join(';')];
ourEquips.forEach(item => {
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
console.log('Saved master CSV');

// 7. Update Sector CSVs in dados/por_setor/
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
ourEquips.forEach(item => {
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

// 8. Copy to Transparencia folder if exists
const destDir = 'c:\\Users\\501379.PMDC\\Desktop\\Transparencia\\PASTAS_DE_ENDERECOS\\07_Bases_Consolidadas';
if (fs.existsSync(destDir)) {
  fs.copyFileSync('dados/todos_os_enderecos_duque_de_caxias.json', path.join(destDir, 'TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.json'));
  fs.copyFileSync('dados/todos_os_enderecos_duque_de_caxias.csv', path.join(destDir, 'TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.csv'));
  console.log('Copied to Transparencia/07_Bases_Consolidadas');
}
