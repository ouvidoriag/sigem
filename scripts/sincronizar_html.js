const fs = require('fs');

const equips = JSON.parse(fs.readFileSync('dados/todos_os_enderecos_duque_de_caxias.json', 'utf8'));
console.log('Total equips to embed:', equips.length);

let indexHtml = fs.readFileSync('index.html', 'utf8');

// Replace DEFAULT_EQUIP line
const regex = /const DEFAULT_EQUIP = \[.*?\];/s;
const newDeclaration = `const DEFAULT_EQUIP = ${JSON.stringify(equips)};`;

if (regex.test(indexHtml)) {
  indexHtml = indexHtml.replace(regex, newDeclaration);
  fs.writeFileSync('index.html', indexHtml, 'utf8');
  console.log('index.html updated successfully!');
  
  // Sync to gerenciador_enderecos.html
  fs.writeFileSync('gerenciador_enderecos.html', indexHtml, 'utf8');
  console.log('gerenciador_enderecos.html mirrored successfully!');
} else {
  console.error('Could not find DEFAULT_EQUIP pattern in index.html');
}
