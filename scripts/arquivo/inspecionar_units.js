const fs = require('fs');

const content = fs.readFileSync('orientahub_backup.sql', 'utf8');

// Find CREATE TABLE units
const unitsCreateMatch = content.match(/CREATE TABLE [`"]?units[`"]?\s*\(([\s\S]*?)\)(?:ENGINE|;)/i);
if (unitsCreateMatch) {
  console.log('=== CREATE TABLE units ===');
  console.log(unitsCreateMatch[1]);
} else {
  console.log('CREATE TABLE units not found with regex, searching lines...');
  const lines = content.split('\n');
  let inUnits = false;
  lines.forEach(l => {
    if (l.includes('CREATE TABLE') && l.includes('units')) inUnits = true;
    if (inUnits) {
      console.log(l);
      if (l.includes(';')) inUnits = false;
    }
  });
}

// Find INSERT INTO units
const insertUnitsMatch = content.match(/INSERT INTO [`"]?units[`"]?\s*(\([^)]+\))?\s*VALUES\s*([\s\S]*?);/i);
if (insertUnitsMatch) {
  console.log('\n=== INSERT INTO units columns ===');
  console.log(insertUnitsMatch[1] || 'Default columns');
  
  // Count rows in VALUES
  const valuesStr = insertUnitsMatch[2];
  console.log('Values length:', valuesStr.length);
}
