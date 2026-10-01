const fs = require('fs');

const orienta = JSON.parse(fs.readFileSync('scripts/orientahub_units.json', 'utf8'));

// Print secretarias in orientahub
console.log('=== SECRETARIAS IN ORIENTAHUB (14) ===');
orienta.filter(u => u.type === 'secretaria').forEach(s => {
  console.log(`- ${s.name} (${s.acronym || 'Sem sigla'})`);
  console.log(`  End: ${s.address}, ${s.neighborhood} | Tel: ${s.phone} | Email: ${s.email}`);
});

// Check health units summary
console.log('\n=== SAÚDE IN ORIENTAHUB (96) ===');
const saudeTypes = {};
orienta.filter(u => u.type === 'unidade-saude').forEach(h => {
  const acr = h.acronym || 'Sem sigla';
  saudeTypes[acr] = (saudeTypes[acr] || 0) + 1;
});
console.log('Health units by acronym:', saudeTypes);
