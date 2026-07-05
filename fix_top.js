const fs = require('fs');
let css = fs.readFileSync('src/index.css', 'utf8');
if (!css.includes('box-sizing: border-box')) {
  css = '* {\n  box-sizing: border-box;\n}\n\n' + css;
}
if (!css.includes('html, body')) {
  css += '\nhtml, body {\n  margin: 0;\n  padding: 0;\n  height: 100%;\n  width: 100%;\n}\n';
}
fs.writeFileSync('src/index.css', css);
