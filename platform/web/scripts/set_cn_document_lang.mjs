// The static export has a single root layout, so every exported page starts
// as <html lang="en">. Pages under out/cn/ are Chinese: declare that in the
// HTML itself (the inline script in app/layout.tsx and the client components
// keep it right at run time and after client-side navigation).
import fs from 'node:fs';
import path from 'node:path';

const root = path.join(process.cwd(), 'out', 'cn');
let changed = 0;

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full);
    } else if (entry.name.endsWith('.html')) {
      const html = fs.readFileSync(full, 'utf-8');
      const next = html.replace(/<html lang="en"/, '<html lang="zh-CN"');
      if (next !== html) {
        fs.writeFileSync(full, next);
        changed += 1;
      }
    }
  }
}

if (fs.existsSync(root)) {
  walk(root);
}
console.log(`set lang="zh-CN" on ${changed} pages under out/cn/`);
