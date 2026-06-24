/* eslint-env node */

import { createServer } from 'http';
import { readFile } from 'fs';
import { join, extname } from 'path';

const PORT = 5000;
const MIME_TYPES = {
  default: 'application/octet-stream',
  html: 'text/html; charset=UTF-8',
  js: 'application/javascript',
  css: 'text/css',
  png: 'image/png',
  jpg: 'image/jpg',
  gif: 'image/gif',
  ico: 'image/x-icon',
  svg: 'image/svg+xml',
};

const STATIC_PATH = join(process.cwd(), './dist');

createServer((req, res) => {
  const filePath = join(STATIC_PATH, req.url === '/' ? 'index.html' : req.url);
  readFile(filePath, (err, data) => {
    if (err) {
      readFile(join(STATIC_PATH, 'index.html'), (err, data) => {
        if (err) { Object.assign(res, { statusCode: 500 }).end('Error'); return; }
        Object.assign(res, { statusCode: 200 }).setHeader('Content-Type', MIME_TYPES.html);
        res.end(data);
      });
      return;
    }
    const ext = extname(filePath).substring(1).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || MIME_TYPES.default });
    res.end(data);
  });
}).listen(PORT, '127.0.0.1', () => console.log(`Server running at http://127.0.0.1:${PORT}/`));
