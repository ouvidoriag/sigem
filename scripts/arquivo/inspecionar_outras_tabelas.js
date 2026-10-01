const fs = require('fs');

const content = fs.readFileSync('orientahub_backup.sql', 'utf8');

// Check other tables
['unit_services', 'attendances', 'users'].forEach(table => {
  const createMatch = content.match(new RegExp(`CREATE TABLE \`?${table}\`?\\s*\\(([\\s\\S]*?)\\)(?:ENGINE|;)`, 'i'));
  console.log(`\n=== Table: ${table} ===`);
  if (createMatch) {
    console.log(createMatch[1].trim());
  }

  const insertMatch = content.match(new RegExp(`INSERT INTO \`?${table}\`?\\s*(?:\\([^)]+\\))?\\s*VALUES\\s*([\\s\\S]*?);`, 'i'));
  if (insertMatch) {
    const rawVal = insertMatch[1].trim();
    console.log(`Insert values length: ${rawVal.length}`);
  } else {
    console.log('No INSERT statement found for table:', table);
  }
});
