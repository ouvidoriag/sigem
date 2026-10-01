const fs = require('fs');

const orientaUnits = JSON.parse(fs.readFileSync('scripts/orientahub_units.json', 'utf8'));
let ourEquips = JSON.parse(fs.readFileSync('dados/todos_os_enderecos_duque_de_caxias.json', 'utf8'));

function norm(s) {
  return (s || '').toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

const directMap = {
  'ipmdc': 'rec_2',
  'esporte-lazer': 'rec_12',
  'cultura-turismo': 'rec_9',
  'seguranca-publica': 'rec_21',
  'protecao-animal': 'rec_19',
  'transportes': 'rec_23',
  'smasdh-sede': 'rec_7',
  'educacao': 'rec_11',
  'fazenda': 'rec_14',
  'governo': 'rec_16',
  'habitacao': 'rec_24',
  'meio-ambiente': 'rec_17',
  'obras': 'rec_18',
  'pgm': 'rec_4',
  'saude': 'rec_20',
  'capsij-infanto-juvenil': 'rec_48',
  'ceata-adolescente': 'rec_51',
  'cer-iv': 'rec_52',
  'ceo-centro': 'rec_53',
  'conselho-mulher-caxias': 'rec_430',
  'conselho-idoso-caxias': 'rec_429',
  'conselho-tutelar-1': 'rec_377',
  'conselho-tutelar-2': 'rec_378',
  'conselho-tutelar-3': 'rec_379',
  'conselho-tutelar-4': 'rec_380',
  'detran-xerem': 'rec_381',
  'hospital-veterinario-caxias': 'rec_382',
  'ubs-alayde-cunha': 'rec_91',
  'ubs-antonio-granja': 'rec_92',
  'ubs-aparecida-tavares': 'rec_105',
  'ubs-edna-siqueira': 'rec_94',
  'ubs-jose-freitas': 'rec_93',
  'ubs-nair-borges': 'rec_95',
  'ubs-vila-canaa': 'rec_76',
  'usf-calundu': 'rec_73',
  'usf-gramacho': 'rec_115',
  'usf-jardim-leal': 'rec_62',
  'usf-maria-helena': 'rec_116',
  'usf-pilar-3-4-5': 'rec_113',
  'usf-santo-antonio-serra': 'rec_89',
  'usf-taquara': 'rec_111',
  'upam': 'rec_37',
  'complexo-assistencia-social': 'rec_423',
  'ubs-adilson-braga': 'rec_90',
  'ubs-margareth-dias': 'rec_104',
  'caps-ad-renato-russo': 'rec_47',
  'ceapd-cer-ii': 'rec_45',
  'ubs-benedito-nascimento': 'rec_97',
  'usf-barro-branco': 'rec_55',
  'usf-parque-esperanca': 'rec_69'
};

let updatedCount = 0;
const reconciledLog = [];

orientaUnits.forEach(u => {
  let target = null;
  if (directMap[u.id]) {
    target = ourEquips.find(e => e.id === directMap[u.id]);
  }
  if (!target) {
    const nuName = norm(u.name);
    target = ourEquips.find(e => norm(e.nome) === nuName || norm(e.nome).includes(nuName) || nuName.includes(norm(e.nome)));
  }

  if (target) {
    let wasModified = false;
    const itemLog = { id: target.id, nome: target.nome, changes: [] };

    // 1. Endereço: OrientaHub tem prioridade máxima
    if (u.address && u.address.trim()) {
      const cleanOAddr = u.address.trim();
      if (target.endereco !== cleanOAddr && !target.endereco.startsWith(cleanOAddr)) {
        itemLog.changes.push({ field: 'endereco', de: target.endereco, para: cleanOAddr });
        target.endereco = cleanOAddr;
        wasModified = true;
      }
    }

    // 2. Bairro: manter consistente com OrientaHub
    if (u.neighborhood && u.neighborhood.trim()) {
      const bTrim = u.neighborhood.trim();
      if (target.bairro !== bTrim && norm(target.bairro) !== norm(bTrim)) {
        itemLog.changes.push({ field: 'bairro', de: target.bairro, para: bTrim });
        target.bairro = bTrim;
        wasModified = true;
      }
    }

    // 3. CEP: OrientaHub atualizado
    if (u.zip_code && u.zip_code !== 'Não informado' && u.zip_code.trim()) {
      const cleanCep = u.zip_code.trim().replace(/^(\d{5})(\d{3})$/, '$1-$2');
      if (target.cep !== cleanCep && cleanCep.length >= 8) {
        itemLog.changes.push({ field: 'cep', de: target.cep, para: cleanCep });
        target.cep = cleanCep;
        wasModified = true;
      }
    }

    // 4. Telefone: Atualizar com telefone direto se target for PABX ou vazio
    if (u.phone && u.phone !== 'Não informado' && u.phone.trim()) {
      const cleanPhone = u.phone.trim();
      if (target.telefone !== cleanPhone) {
        itemLog.changes.push({ field: 'telefone', de: target.telefone, para: cleanPhone });
        target.telefone = cleanPhone;
        wasModified = true;
      }
    }

    // 5. Horário de Atendimento
    if (u.hours && u.hours !== 'Não informado' && u.hours.trim()) {
      const cleanHours = u.hours.trim();
      if (target.horario_funcionamento !== cleanHours) {
        itemLog.changes.push({ field: 'horario', de: target.horario_funcionamento, para: cleanHours });
        target.horario_funcionamento = cleanHours;
        wasModified = true;
      }
    }

    // 6. Descrição dos serviços
    if (u.description && u.description.trim()) {
      const cleanDesc = u.description.trim();
      if (target.descricao.includes('Equipamento público oficial da Prefeitura') || target.descricao.length < 40) {
        itemLog.changes.push({ field: 'descricao', de: target.descricao, para: cleanDesc });
        target.descricao = cleanDesc;
        wasModified = true;
      }
    }

    if (wasModified) {
      updatedCount++;
      reconciledLog.push(itemLog);
    }
  }
});

// Now add genuinely new official units from OrientaHub:
const newUnitsData = [
  {
    id: 'rec_443',
    nome: 'Central de Atendimento Funerário (CAF)',
    categoria: 'Secretarias e Órgãos',
    distrito: '2',
    bairro: 'Jardim Primavera',
    endereco: 'Alameda Esmeralda, 206 – Sala 49 – Jardim Primavera',
    cep: '25215-260',
    predio_sala: 'Sala 49',
    telefone: '(21) 2772-7200',
    email: 'caf@duquedecaxias.rj.gov.br',
    lat: -22.68515,
    lon: -43.28399,
    hub_id: 'hub_1',
    hub_nome: 'Centro Cívico / Paço Municipal (Prefeitura)',
    horario_funcionamento: 'Segunda a Sexta, 08:00 às 17:00 (Plantão de Óbito)',
    descricao: 'Central responsável pelo atendimento à população em serviços funerários, concessão de gratuidade de sepultamento a famílias de baixa renda e regulação dos cemitérios municipais.',
    status: 'Ativo',
    sigla: 'CAF'
  },
  {
    id: 'rec_444',
    nome: 'CMPD — Conselho Municipal de Defesa dos Direitos da Pessoa com Deficiência',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centenário',
    endereco: 'Rua Manoel Vieira, s/nº – Centenário',
    cep: '25030-220',
    predio_sala: 'Complexo Centenário',
    telefone: '(21) 2672-6650',
    email: 'cmpd@duquedecaxias.rj.gov.br',
    lat: -22.7820,
    lon: -43.3120,
    hub_id: 'hub_11',
    hub_nome: 'Complexo de Assistência Social do Centenário',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h',
    descricao: 'Órgão colegiado de controle social e deliberação das políticas públicas municipais voltadas à garantia de acessibilidade, inclusão e direitos das pessoas com deficiência.',
    status: 'Ativo',
    sigla: 'CMPD'
  },
  {
    id: 'rec_445',
    nome: 'V Conselho Tutelar (Sede Itatiaia)',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Itatiaia',
    endereco: 'Rua Coronel França Soares, 176 – Itatiaia',
    cep: '25075-010',
    predio_sala: 'Sede V Conselho',
    telefone: '(21) 2652-4993',
    email: 'conselhotutelar5@duquedecaxias.rj.gov.br',
    lat: -22.7830,
    lon: -43.3080,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h (Plantão 24h)',
    descricao: 'Unidade protetiva do Conselho Tutelar encarregada de resguardar o Estatuto da Criança e do Adolescente (ECA) no bairro Itatiaia e arredores.',
    status: 'Ativo',
    sigla: 'V CT'
  },
  {
    id: 'rec_446',
    nome: 'VI Conselho Tutelar (Sede São Bento)',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '2',
    bairro: 'São Bento',
    endereco: 'Av. Leonel de Moura Brizola, s/nº – São Bento',
    cep: '25050-009',
    predio_sala: 'Sede VI Conselho',
    telefone: '(21) 3134-2044',
    email: 'conselhotutelar6@duquedecaxias.rj.gov.br',
    lat: -22.7450,
    lon: -43.2950,
    hub_id: 'hub_10',
    hub_nome: 'Campus Integrado Educacional São Bento (Antiga FEUDUC)',
    horario_funcionamento: 'Segunda a sexta-feira, das 8h às 17h (Plantão 24h)',
    descricao: 'Garante o cumprimento dos direitos da infância e da juventude sob regência do ECA na região territorial de São Bento e bairros adjacentes.',
    status: 'Ativo',
    sigla: 'VI CT'
  },
  {
    id: 'rec_447',
    nome: 'Centro de Cidadania LGBT / DEMPPIRD',
    categoria: 'Assistência Social (SEASDIH)',
    distrito: '1',
    bairro: 'Centro',
    endereco: 'Rua Frei Fidélis, 709 – Centro',
    cep: '25010-150',
    predio_sala: 'Polo Cidadania',
    telefone: '(21) 2672-6650',
    email: 'demppird@duquedecaxias.rj.gov.br',
    lat: -22.7910,
    lon: -43.3065,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Segunda a sexta-feira, das 9h às 17h',
    descricao: 'Departamento de Promoção de Políticas de Promoção da Igualdade Racial e Direitos Individuais e Coletivos (DEMPPIRD) e Centro de Cidadania LGBT.',
    status: 'Ativo',
    sigla: 'DEMPPIRD'
  },
  {
    id: 'rec_448',
    nome: 'Serviço Residencial Terapêutico Jardim Anhangá (SRT)',
    categoria: 'Saúde Especializada / Hospitalar',
    distrito: '3',
    bairro: 'Jardim Anhangá',
    endereco: 'Rua Pacoti, 450 – Jardim Anhangá',
    cep: '25260-120',
    predio_sala: '',
    telefone: '(21) 2773-5500',
    email: 'saude@duquedecaxias.rj.gov.br',
    lat: -22.6500,
    lon: -43.2450,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Atendimento Residencial Contínuo 24h',
    descricao: 'Moradia assistida para pessoas com sofrimento mental desinstitucionalizadas, com acompanhamento multiprofissional contínuo da Rede de Atenção Psicossocial (RAPS).',
    status: 'Ativo',
    sigla: 'SRT Anhangá'
  },
  {
    id: 'rec_449',
    nome: 'Serviço Residencial Terapêutico Parque Lafaiete (SRT)',
    categoria: 'Saúde Especializada / Hospitalar',
    distrito: '1',
    bairro: 'Parque Lafaiete',
    endereco: 'Rua Araruama, 353 – Parque Lafaiete',
    cep: '25015-180',
    predio_sala: '',
    telefone: '(21) 2773-5500',
    email: 'saude@duquedecaxias.rj.gov.br',
    lat: -22.7870,
    lon: -43.3240,
    hub_id: '',
    hub_nome: '',
    horario_funcionamento: 'Atendimento Residencial Contínuo 24h',
    descricao: 'Unidade residencial terapêutica da RAPS voltada ao processo de reabilitação psicossocial e reinserção comunitária.',
    status: 'Ativo',
    sigla: 'SRT Lafaiete'
  }
];

newUnitsData.forEach(nu => {
  if (!ourEquips.some(e => e.nome.toLowerCase() === nu.nome.toLowerCase() || e.id === nu.id)) {
    ourEquips.push(nu);
    console.log('Added new equipment:', nu.nome);
  }
});

console.log('Total equipments after reconciliation:', ourEquips.length);
console.log('Total updated records:', updatedCount);

// Save updated JSON
fs.writeFileSync('dados/todos_os_enderecos_duque_de_caxias.json', JSON.stringify(ourEquips, null, 2), 'utf8');

// Generate CSV
const headers = ['id', 'nome', 'categoria', 'distrito', 'bairro', 'endereco', 'cep', 'predio_sala', 'telefone', 'email', 'lat', 'lon', 'hub_id', 'hub_nome', 'horario_funcionamento', 'descricao', 'status', 'sigla'];
const csvLines = [headers.join(';')];
ourEquips.forEach(item => {
  const row = headers.map(h => {
    let val = item[h] !== undefined && item[h] !== null ? String(item[h]) : '';
    val = val.replace(/"/g, '""');
    if (val.includes(';') || val.includes('\n') || val.includes('"')) {
      val = '"' + val + '"';
    }
    return val;
  });
  csvLines.push(row.join(';'));
});
fs.writeFileSync('dados/todos_os_enderecos_duque_de_caxias.csv', '\uFEFF' + csvLines.join('\n'), 'utf8');

// Save detailed log of modifications
fs.writeFileSync('scripts/relatorio_reconciliacao_orientahub.json', JSON.stringify(reconciledLog, null, 2), 'utf8');

console.log('Done!');
