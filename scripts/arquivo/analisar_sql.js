const fs = require('fs');

const stats = fs.statSync('orientahub_backup.sql');
console.log('File size:', (stats.size / 1024).toFixed(2), 'KB');

const content = fs.readFileSync('orientahub_backup.sql', 'utf8');
const lines = content.split('\n');
console.log('Total lines:', lines.length);

const tables = [];
const inserts = {};
let currentTable = null;

lines.forEach(l => {
  const createMatch = l.match(/CREATE TABLE [`"]?([a-zA-Z0-9_]+)[`"]?/i);
  if (createMatch) tables.push(createMatch[1]);
  
  const insertMatch = l.match(/INSERT INTO [`"]?([a-zA-Z0-9_]+)[`"]?/i);
  if (insertMatch) {
    inserts[insertMatch[1]] = (inserts[insertMatch[1]] || 0) + 1;
  }
});

console.log('Tables created:', tables);
console.log('Insert statements per table:', inserts);
