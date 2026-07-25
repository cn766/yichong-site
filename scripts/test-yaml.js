const fs = require('fs');
const yaml = require('js-yaml');
const content = fs.readFileSync('src/content/blog/baowen-wanzhinan.md', 'utf8');
const match = content.match(/^---\n([\s\S]*?)\n---/);
if (match) {
  try {
    yaml.load(match[1]);
    console.log('YAML OK');
  } catch (e) {
    console.log('YAML ERROR:', e.message);
    console.log('Line in frontmatter:', e.mark?.line);
    const lines = match[1].split('\n');
    const errLine = e.mark?.line || 0;
    for (let i = Math.max(0, errLine - 2); i <= Math.min(lines.length - 1, errLine + 2); i++) {
      console.log(`Line ${i + 1}: [${lines[i]}]`);
    }
  }
} else {
  console.log('No frontmatter found');
}
