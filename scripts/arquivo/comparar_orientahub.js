const fs = require('fs');

const orientaUnits = JSON.parse(fs.readFileSync('scripts/orientahub_units.json', 'utf8'));
const ourEquips = JSON.parse(fs.readFileSync('dados/todos_os_enderecos_duque_de_caxias.json', 'utf8'));

console.log('Total in OrientaHub:', orientaUnits.length);
console.log('Total in our dataset:', ourEquips.length);

function norm(s) {
  return (s || '').toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// Map our equipment for fast matching
const ourList = ourEquips.map(e => ({
  ...e,
  normNome: norm(e.nome),
  normEnd: norm(e.endereco),
  normBairro: norm(e.bairro)
}));

const matched = [];
const notInOur = [];

orientaUnits.forEach(u => {
  const nuName = norm(u.name);
  const nuAddress = norm(u.address);
  const nuBairro = norm(u.neighborhood);

  // Match strategy:
  // 1. Exact or contains name
  let found = ourList.find(e => {
    if (e.normNome === nuName) return true;
    if (e.normNome.includes(nuName) || nuName.includes(e.normNome)) return true;
    
    // Check significant words overlap
    const w1 = nuName.split(' ').filter(w => w.length > 3 && !['unidade', 'centro', 'municipal', 'duque', 'caxias', 'posto'].includes(w));
    const w2 = e.normNome.split(' ').filter(w => w.length > 3 && !['unidade', 'centro', 'municipal', 'duque', 'caxias', 'posto'].includes(w));
    if (w1.length > 0 && w2.length > 0) {
      const common = w1.filter(w => w2.includes(w));
      if (common.length >= Math.min(w1.length, 2)) return true;
    }

    // Check address match if in same neighborhood
    if (nuAddress.length > 10 && e.normEnd.length > 10) {
      if (nuBairro && e.normBairro && (nuBairro.includes(e.normBairro) || e.normBairro.includes(nuBairro))) {
        const addrNum1 = (u.address || '').match(/\d+/);
        const addrNum2 = (e.endereco || '').match(/\d+/);
        if (addrNum1 && addrNum2 && addrNum1[0] === addrNum2[0]) {
          const streetWords1 = nuAddress.split(' ').filter(w => w.length > 4);
          const streetWords2 = e.normEnd.split(' ').filter(w => w.length > 4);
          const streetCommon = streetWords1.filter(w => streetWords2.includes(w));
          if (streetCommon.length >= 1) return true;
        }
      }
    }

    return false;
  });

  if (found) {
    matched.push({ orienta: u, our: found });
  } else {
    notInOur.push(u);
  }
});

console.log('\n=== MATCH RESULTS ===');
console.log('Matched in our dataset:', matched.length);
console.log('Present in OrientaHub but NOT in our dataset:', notInOur.length);

if (notInOur.length > 0) {
  console.log('\n--- Units in OrientaHub NOT found in our dataset ---');
  notInOur.forEach((u, idx) => {
    console.log(`${idx + 1}. [${u.type}] ${u.name}`);
    console.log(`   End: ${u.address} | Bairro: ${u.neighborhood} | Tel: ${u.phone} | Horas: ${u.hours}`);
  });
}

// Check differences in matched items (phone, address, email, etc.)
const diffs = [];
matched.forEach(({ orienta, our }) => {
  const itemDiff = {
    name: our.nome,
    orientaName: orienta.name,
    changes: []
  };

  if (orienta.hours) {
    itemDiff.hours = orienta.hours;
  }
  if (orienta.description) {
    itemDiff.description = orienta.description;
  }

  // Compare phone
  const p1 = (orienta.phone || '').replace(/\D/g, '');
  const p2 = (our.telefone || '').replace(/\D/g, '');
  if (p1 && p2 && p1 !== p2 && !p2.includes(p1) && !p1.includes(p2)) {
    itemDiff.changes.push(`Telefone: Orienta='${orienta.phone}' vs Nosso='${our.telefone}'`);
  }

  // Compare CEP
  const c1 = (orienta.zip_code || '').replace(/\D/g, '');
  const c2 = (our.cep || '').replace(/\D/g, '');
  if (c1 && c2 && c1 !== c2) {
    itemDiff.changes.push(`CEP: Orienta='${orienta.zip_code}' vs Nosso='${our.cep}'`);
  }

  if (itemDiff.changes.length > 0) {
    diffs.push(itemDiff);
  }
});

console.log(`\nMatched items with differences in Phone/CEP: ${diffs.length}`);
diffs.slice(0, 10).forEach(d => {
  console.log(`\n* ${d.name} (Orienta: ${d.orientaName})`);
  d.changes.forEach(c => console.log(`  - ${c}`));
});

// Save complete comparison report to JSON
fs.writeFileSync('scripts/relatorio_comparacao_orientahub.json', JSON.stringify({
  summary: {
    totalOrienta: orientaUnits.length,
    totalOur: ourEquips.length,
    matched: matched.length,
    notInOurCount: notInOur.length
  },
  notInOur,
  diffs
}, null, 2), 'utf8');

console.log('\nReport saved to scripts/relatorio_comparacao_orientahub.json');
