const fs = require('fs');
const orienta = JSON.parse(fs.readFileSync('scripts/orientahub_units.json', 'utf8'));

const ids = [
  'abrigo-primeiro-olhar', 'casa-comunitaria', 'casa-de-passagem', 'casa-social-renascer',
  'casa-social-reviver', 'centro-pop', 'cmdca', 'conselho-do-idoso', 'conselho-da-mulher',
  'dedaf', 'lgbt-demppird', 'equinovida', 'getsemani', 'detran-imbarie', 'detran-saracuruna', 'ubs-centro'
];

orienta.filter(u => ids.includes(u.id)).forEach(u => {
  console.log(`\n=== [${u.id}] ${u.name} ===`);
  console.log(`Tipo: ${u.type} | Sigla: ${u.acronym}`);
  console.log(`Endereço: ${u.address} - ${u.neighborhood}`);
  console.log(`Telefone: ${u.phone} | Email: ${u.email}`);
  console.log(`Horário: ${u.hours}`);
  console.log(`Descrição: ${u.description}`);
});
