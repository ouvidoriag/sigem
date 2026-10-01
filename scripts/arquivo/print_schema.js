const fs = require('fs');

const content = fs.readFileSync('orientahub_backup.sql', 'utf8');

const lines = content.split('\n');
let print = false;
console.log('--- SCHEMA UNITS ---');
for (const l of lines) {
  if (l.includes('CREATE TABLE') && l.includes('units')) print = true;
  if (print) {
    console.log(l);
    if (l.includes('ENGINE') || l.includes(';')) {
      print = false;
      break;
    }
  }
}
