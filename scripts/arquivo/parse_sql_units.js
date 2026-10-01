const fs = require('fs');

const content = fs.readFileSync('orientahub_backup.sql', 'utf8');

// Extract the INSERT INTO `units` statement
const insertMatch = content.match(/INSERT INTO `units` VALUES\s*([\s\S]*?);(?:\r?\n|$)/);
if (!insertMatch) {
  console.error('INSERT INTO units not found');
  process.exit(1);
}

const rawValues = insertMatch[1].trim();

// SQL VALUES parser for rows in form: ('val1', 'val2', NULL, ...)
function parseSqlValues(str) {
  const rows = [];
  let inRow = false;
  let inString = false;
  let escape = false;
  let currentVal = '';
  let currentRow = [];

  for (let i = 0; i < str.length; i++) {
    const char = str[i];

    if (!inRow) {
      if (char === '(') {
        inRow = true;
        currentRow = [];
        currentVal = '';
        inString = false;
        escape = false;
      }
    } else {
      if (inString) {
        if (escape) {
          currentVal += char;
          escape = false;
        } else if (char === '\\') {
          escape = true;
        } else if (char === "'") {
          // check for double single quote ''
          if (str[i + 1] === "'") {
            currentVal += "'";
            i++;
          } else {
            inString = false;
          }
        } else {
          currentVal += char;
        }
      } else {
        if (char === "'") {
          inString = true;
        } else if (char === ',') {
          currentRow.push(currentVal === 'NULL' ? null : currentVal.trim());
          currentVal = '';
        } else if (char === ')') {
          currentRow.push(currentVal === 'NULL' ? null : currentVal.trim());
          rows.push(currentRow);
          inRow = false;
          currentRow = [];
          currentVal = '';
        } else {
          currentVal += char;
        }
      }
    }
  }

  return rows;
}

const rawRows = parseSqlValues(rawValues);
console.log('Total units parsed from SQL:', rawRows.length);

const columns = [
  'id', 'name', 'acronym', 'type', 'address', 'zip_code',
  'neighborhood', 'city', 'phone', 'email', 'hours', 'description', 'color', 'icon'
];

const sqlUnits = rawRows.map(r => {
  const obj = {};
  columns.forEach((col, idx) => {
    obj[col] = r[idx];
  });
  return obj;
});

// Write to JSON for inspection and comparison
fs.writeFileSync('scripts/orientahub_units.json', JSON.stringify(sqlUnits, null, 2), 'utf8');
console.log('Saved units to scripts/orientahub_units.json');

// Group by type
const byType = {};
sqlUnits.forEach(u => {
  byType[u.type] = (byType[u.type] || 0) + 1;
});
console.log('Units by type:', byType);

// Sample unit
console.log('Sample unit:', sqlUnits[0]);
