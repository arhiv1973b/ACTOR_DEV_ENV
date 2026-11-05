const fs = require('fs');
const path = require('path');

const networkFile = path.join('output', 'network', '0007.txt');
const content = fs.readFileSync(networkFile, 'utf8');
const lines = content.split('\n');
let jsonLine = '';

for (const line of lines) {
  if (line.trim().startsWith('[["wrb.fr"')) {
    jsonLine = line.trim();
    break;
  }
}

const parsed = JSON.parse(jsonLine);
console.log('parsed length:', parsed.length);
console.log('parsed[0]:', parsed[0]);
console.log('parsed[1]:', parsed[1]);
console.log('typeof parsed[2]:', typeof parsed[2]);
if (typeof parsed[2] === 'string') {
  console.log('parsed[2] slice:', parsed[2].slice(0, 200));
} else {
  console.log('parsed[2]:', JSON.stringify(parsed[2]).slice(0, 200));
}
