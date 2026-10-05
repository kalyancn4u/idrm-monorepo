// Minimal static file server for previewing the IDRM templates locally.
// Node-based (reliable on Windows). Serves the templates/ directory.
//   node templates/_preview-server.js   →  http://localhost:4599
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = process.env.PORT || 4599;
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.md': 'text/plain; charset=utf-8',
  '.json': 'application/json', '.png': 'image/png', '.ico': 'image/x-icon',
  '.svg': 'image/svg+xml', '.jpg': 'image/jpeg'
};

http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') p = '/idrm-templates-showcase.html';
  const fp = path.normalize(path.join(ROOT, p));
  if (!fp.startsWith(ROOT)) { res.writeHead(403); return res.end('Forbidden'); }
  fs.readFile(fp, (err, data) => {
    if (err) { res.writeHead(404, { 'Content-Type': 'text/plain' }); return res.end('Not found: ' + p); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(fp).toLowerCase()] || 'application/octet-stream' });
    res.end(data);
  });
}).listen(PORT, () => console.log('IDRM templates preview → http://localhost:' + PORT));
