const fs = require('fs');
const equip = JSON.parse(fs.readFileSync('dados/todos_os_enderecos_duque_de_caxias.json', 'utf8'));

function testSearch(q) {
  const normQ = q.toLowerCase();
  const res = equip.filter(item => {
    const fullStr = `${item.nome} ${item.categoria} ${item.bairro} ${item.endereco} ${item.telefone || ''} ${item.email || ''} ${item.predio_sala || ''} ${item.hub_nome || ''} ${item.horario_funcionamento || ''} ${item.descricao || ''}`.toLowerCase();
    return fullStr.includes(normQ);
  });
  console.log(`Search "${q}": ${res.length} matches:`);
  res.slice(0, 3).forEach(r => console.log(`  - [${r.id}] ${r.nome} | ${r.bairro} | ${r.horario_funcionamento}`));
}

testSearch('Primeiro Olhar');
testSearch('DETRAN');
testSearch('CMDCA');
testSearch('UBS Centro');
testSearch('Getsêmani');
