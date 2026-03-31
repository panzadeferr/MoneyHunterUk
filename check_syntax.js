const fs = require('fs');
const content = fs.readFileSync('app.html', 'utf8');

const scripts = [];
const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/g;
let match;
while ((match = scriptRegex.exec(content)) !== null) {
  if (!match[0].includes('src=')) {
    scripts.push(match[1]);
  }
}

console.log('Found', scripts.length, 'inline script blocks');

scripts.forEach((script, idx) => {
  try {
    new Function(script);
    console.log('Script', idx+1, ': VALID (length:', script.length, ')');
  } catch(e) {
    console.log('Script', idx+1, 'ERROR:', e.message);
    const lines = script.split('\n');
    console.log('Total lines:', lines.length);
    
    let lastGoodLine = 0;
    for (let size = lines.length; size >= 1; size -= 50) {
      try {
        new Function(lines.slice(0, size).join('\n'));
        lastGoodLine = size;
        break;
      } catch(e2) {}
    }
    
    if (lastGoodLine > 0) {
      for (let size = lastGoodLine; size <= lines.length; size++) {
        try {
          new Function(lines.slice(0, size).join('\n'));
        } catch(e2) {
          console.log('Error introduced at line', size);
          for (let i = Math.max(0, size-3); i < Math.min(lines.length, size+3); i++) {
            console.log((i+1) + ': ' + lines[i]);
          }
          break;
        }
      }
    }
  }
});
